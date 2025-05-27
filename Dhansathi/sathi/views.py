from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import OutstandingToken, BlacklistedToken
from .models import *
from .nlp import get_chatbot_response
from .recommend import calculate_investable_amount, generate_investment_advice, analyze_expense_pattern, get_expense_recommendations, get_smart_recommendations
from .serializer import ProfileSerializer
import pdfplumber
import datetime
import re
from django.shortcuts import render
from django.db.models import Sum, Avg
from django.core.paginator import Paginator
from collections import defaultdict

# Template views
def home_view(request):
    return render(request, 'home.html')

def login_view(request):
    return render(request, 'login.html')

def register_view(request):
    return render(request, 'register.html')

def dashboard_view(request):
    return render(request, 'dashboard.html')

def profile_view(request):
    return render(request, 'profile.html')

# API views
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    serializer = ProfileSerializer(profile, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Profile saved successfully'})
    return Response(serializer.errors, status=400)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_statement(request):
    try:
        if 'file' not in request.FILES:
            return Response({
                'status': 'Error',
                'message': 'No file was uploaded. Please select a PDF file.'
            }, status=400)

        file = request.FILES['file']
        
        # Validate file type
        if not file.name.endswith('.pdf'):
            return Response({
                'status': 'Error',
                'message': 'Invalid file type. Please upload a PDF file.'
            }, status=400)

        try:
            bank_file = BankStatement.objects.create(user=request.user, file=file)
        except Exception as e:
            return Response({
                'status': 'Error',
                'message': f'Error saving file: {str(e)}'
            }, status=400)

        expense_categories = {
            'Food': ['swiggy', 'zomato', 'restaurant', 'cafe', 'food', 'dining', 'eat', 'lunch', 'dinner', 'breakfast'],
            'Transportation': ['uber', 'ola', 'petrol', 'fuel', 'metro', 'bus', 'train', 'taxi', 'auto', 'transport'],
            'Shopping': ['amazon', 'flipkart', 'myntra', 'retail', 'mall', 'shop', 'store', 'market', 'purchase'],
            'Entertainment': ['movie', 'netflix', 'prime', 'hotstar', 'entertainment', 'game', 'sport', 'theater'],
            'Utilities': ['electricity', 'water', 'gas', 'internet', 'phone', 'mobile', 'bill', 'recharge', 'broadband'],
            'Healthcare': ['hospital', 'medical', 'pharmacy', 'doctor', 'health', 'clinic', 'medicine', 'dental'],
            'Education': ['course', 'tuition', 'school', 'college', 'books', 'class', 'training', 'workshop'],
            'Insurance': ['insurance', 'policy', 'premium', 'life', 'health', 'vehicle'],
            'Investment': ['mutual fund', 'stocks', 'shares', 'demat', 'investment', 'fd', 'deposit']
        }

        amount_pattern = r'(?:Rs\.|INR|₹)\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:DR|Debit|Debited)?'
        debit_pattern = r'\b(?:debit|dr|withdrawn|paid|debited|payment|purchase|spent)\b'

        date_patterns = [
            r'(\d{2}[-/]\d{2}[-/]\d{4})',
            r'(\d{4}[-/]\d{2}[-/]\d{2})',
            r'(\d{2}(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\d{4})',
            r'(\d{2}-(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)-\d{4})'
        ]

        expenses_found = []
        total_expenditure = 0
        processed_lines = set()

        try:
            with pdfplumber.open(bank_file.file.path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if not text:
                        continue

                    lines = text.split('\n')
                    for line in lines:
                        if line in processed_lines or any(header in line.lower() for header in 
                            ['page', 'statement', 'opening balance', 'closing balance', 'brought forward']):
                            continue

                        processed_lines.add(line)

                        transaction_date = None
                        for pattern in date_patterns:
                            date_match = re.search(pattern, line)
                            if date_match:
                                try:
                                    date_str = date_match.group(1)
                                    if '/' in date_str or '-' in date_str:
                                        if len(date_str.split('/')[-1]) == 4 or len(date_str.split('-')[-1]) == 4:
                                            transaction_date = datetime.datetime.strptime(date_str.replace('-', '/'), '%d/%m/%Y').date()
                                    else:
                                        transaction_date = datetime.datetime.strptime(date_str, '%d%b%Y').date()
                                    break
                                except ValueError:
                                    continue

                        amount_match = re.search(amount_pattern, line)
                        if amount_match:
                            amount_str = amount_match.group(1).replace(',', '')
                            try:
                                amount = float(amount_str)
                                is_debit = re.search(debit_pattern, line.lower())
                                if not is_debit or amount <= 0:
                                    continue

                                category = 'Other'
                                line_lower = line.lower()
                                for cat, keywords in expense_categories.items():
                                    if any(keyword in line_lower for keyword in keywords):
                                        category = cat
                                        break

                                if not transaction_date:
                                    transaction_date = datetime.date.today()

                                description = line.strip()
                                noise_patterns = ['UPI/', 'IMPS/', 'NEFT/', 'REF NO.', '*']
                                for pattern in noise_patterns:
                                    description = description.replace(pattern, '')
                                description = ' '.join(description.split())

                                expense_entry = {
                                    'date': transaction_date,
                                    'amount': amount,
                                    'category': category,
                                    'description': description
                                }

                                expenses_found.append(expense_entry)
                                total_expenditure += amount

                            except ValueError:
                                continue

            if not expenses_found:
                bank_file.delete()
                return Response({
                    'status': 'Warning',
                    'message': 'No expenses were found in the uploaded statement. Please check if the PDF contains valid transaction data.'
                }, status=200)

            earliest_date = min(expense['date'] for expense in expenses_found)
            latest_date = max(expense['date'] for expense in expenses_found)

            Expense.objects.filter(
                user=request.user,
                date__range=[earliest_date, latest_date]
            ).delete()

            for expense in expenses_found:
                Expense.objects.create(
                    user=request.user,
                    date=expense['date'],
                    amount=expense['amount'],
                    category=expense['category'],
                    description=expense['description']
                )

            profile, _ = UserProfile.objects.get_or_create(user=request.user)
            profile.total_expenditure = Expense.objects.filter(user=request.user).aggregate(total=Sum('amount'))['total'] or 0
            profile.save()

            all_expenses = Expense.objects.filter(user=request.user)
            patterns = analyze_expense_pattern(all_expenses)
            recommendations = get_expense_recommendations(patterns)

            category_totals = defaultdict(float)
            for expense in expenses_found:
                category_totals[expense['category']] += expense['amount']

            return Response({
                'status': 'Success',
                'expenses_found': len(expenses_found),
                'total_expenditure': total_expenditure,
                'category_breakdown': dict(category_totals),
                'categories_found': list(set(e['category'] for e in expenses_found)),
                'recommendations': recommendations,
                'date_range': {
                    'start': earliest_date.strftime('%Y-%m-%d'),
                    'end': latest_date.strftime('%Y-%m-%d')
                }
            })

        except Exception as e:
            bank_file.delete()
            return Response({
                'status': 'Error',
                'message': f'Error processing PDF: {str(e)}'
            }, status=400)

    except Exception as e:
        return Response({
            'status': 'Error',
            'message': f'Upload failed: {str(e)}'
        }, status=400)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def investment_advice(request):
    expenses = Expense.objects.filter(user=request.user)
    profile = UserProfile.objects.get(user=request.user)
    amount = calculate_investable_amount(expenses)
    advice = generate_investment_advice(request.user, amount, profile.risk_tolerance)
    return Response({'advice': advice})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ask_bot(request):
    query = request.data.get('query')
    response = get_chatbot_response(query)
    ChatLog.objects.create(user=request.user, query=query, response=response)
    return Response({'response': response})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request):
    try:
        tokens = OutstandingToken.objects.filter(user=request.user)
        for token in tokens:
            BlacklistedToken.objects.get_or_create(token=token)
        return Response({'status': 'Logged out'})
    except:
        return Response({'error': 'Logout failed'}, status=400)


from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializer import RegisterSerializer

@api_view(['POST'])
def register_user(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "User registered successfully."}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_data(request):
    try:
        # Get user's expenses for the current month
        today = datetime.date.today()
        start_of_month = today.replace(day=1)
        
        # Get all expenses and current month expenses
        all_expenses = Expense.objects.filter(user=request.user)
        current_month_expenses = all_expenses.filter(date__gte=start_of_month)
        
        # Calculate total expenditure
        total_expenditure = all_expenses.aggregate(total=Sum('amount'))['total'] or 0
        current_month_total = current_month_expenses.aggregate(total=Sum('amount'))['total'] or 0
        
        # Calculate monthly averages
        monthly_expenses = defaultdict(float)
        for expense in all_expenses:
            month_key = expense.date.strftime('%Y-%m')
            monthly_expenses[month_key] += expense.amount
        
        num_months = len(monthly_expenses) or 1  # Avoid division by zero
        monthly_average = sum(monthly_expenses.values()) / num_months
        
        # Get category breakdown for current month
        category_breakdown = defaultdict(float)
        for expense in current_month_expenses:
            category_breakdown[expense.category] += expense.amount
        
        # Convert defaultdict to regular dict for JSON serialization
        category_breakdown = dict(category_breakdown)
        
        # Get top category
        top_category = max(category_breakdown.items(), key=lambda x: x[1])[0] if category_breakdown else None
        
        # Calculate investable amount based on current month
        investable_amount = calculate_investable_amount(current_month_expenses)
        
        # Get monthly trend (last 6 months)
        monthly_trend = {}
        for i in range(5, -1, -1):
            month = today.replace(day=1) - datetime.timedelta(days=i*30)
            month_key = month.strftime('%b %Y')
            month_expenses = all_expenses.filter(
                date__year=month.year,
                date__month=month.month
            ).aggregate(total=Sum('amount'))['total'] or 0
            monthly_trend[month_key] = month_expenses
        
        # Calculate month-over-month change
        previous_month = (today.replace(day=1) - datetime.timedelta(days=1)).replace(day=1)
        previous_month_total = all_expenses.filter(
            date__year=previous_month.year,
            date__month=previous_month.month
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        if previous_month_total > 0:
            month_change = ((current_month_total - previous_month_total) / previous_month_total) * 100
        else:
            month_change = 0
        
        return Response({
            'total_expenditure': total_expenditure,
            'current_month_total': current_month_total,
            'monthly_average': monthly_average,
            'investable_amount': investable_amount,
            'top_category': top_category,
            'category_breakdown': category_breakdown,
            'monthly_trend': monthly_trend,
            'month_change': month_change
        })
    except Exception as e:
        return Response({
            'error': f'Error fetching dashboard data: {str(e)}'
        }, status=400)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_expenses(request):
    timeframe = request.GET.get('timeframe', 'all')
    page = int(request.GET.get('page', 1))
    
    # Get base queryset
    expenses = Expense.objects.filter(user=request.user).order_by('-date')
    
    # Apply timeframe filter
    today = datetime.date.today()
    if timeframe == 'week':
        start_date = today - datetime.timedelta(days=7)
        expenses = expenses.filter(date__gte=start_date)
    elif timeframe == 'month':
        start_date = today.replace(day=1)
        expenses = expenses.filter(date__gte=start_date)
    
    # Paginate results
    paginator = Paginator(expenses, 10)  # 10 items per page
    page_obj = paginator.get_page(page)
    
    # Format response
    expenses_data = [{
        'date': expense.date,
        'category': expense.category,
        'description': expense.description,
        'amount': expense.amount
    } for expense in page_obj]
    
    return Response({
        'expenses': expenses_data,
        'total_pages': paginator.num_pages,
        'current_page': page
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recommendations(request):
    """Get personalized recommendations for the user."""
    try:
        # Get user's profile
        profile = UserProfile.objects.get(user=request.user)
        
        # Get recent expenses (last 3 months)
        three_months_ago = datetime.date.today() - datetime.timedelta(days=90)
        expenses = Expense.objects.filter(
            user=request.user,
            date__gte=three_months_ago
        ).order_by('-date')
        
        # Get expense patterns
        patterns = analyze_expense_pattern(expenses)
        
        # Calculate metrics
        total_expenses = sum(e.amount for e in expenses)
        monthly_income = profile.monthly_income or 0
        savings_goal = profile.savings_goal or monthly_income * 0.2  # Default 20% if not set
        current_savings = monthly_income - (total_expenses / 3)  # Average monthly expenses
        
        # Get smart recommendations
        recommendations = get_smart_recommendations(
            patterns=patterns,
            monthly_income=monthly_income,
            current_savings=current_savings,
            savings_goal=savings_goal,
            risk_tolerance=profile.risk_tolerance,
            investment_goals=profile.investment_goals
        )
        
        return Response({
            'recommendations': recommendations
        })
        
    except UserProfile.DoesNotExist:
        return Response({
            'recommendations': [{
                'id': 'profile',
                'type': 'alert',
                'title': 'Complete Your Profile',
                'description': 'Update your profile to get personalized recommendations.',
                'action': 'Update Profile'
            }]
        })
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_profile(request):
    try:
        profile = UserProfile.objects.get(user=request.user)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)
    except UserProfile.DoesNotExist:
        return Response({
            'message': 'Profile not found'
        }, status=404)
