from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import OutstandingToken, BlacklistedToken
from .models import *
from .nlp import get_chatbot_response
from .recommend import calculate_investable_amount, generate_investment_advice
from .serializer import ProfileSerializer
import pdfplumber
import datetime

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    serializer = ProfileSerializer(profile, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Profile saved'})
    return Response(serializer.errors, status=400)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_statement(request):
    file = request.FILES['file']
    bank_file = BankStatement.objects.create(user=request.user, file=file)
    with pdfplumber.open(bank_file.file.path) as pdf:
        text = "\n".join([p.extract_text() for p in pdf.pages])
    for line in text.split('\n'):
        if 'swiggy' in line.lower():
            Expense.objects.create(user=request.user, category="Food", amount=200, date=datetime.date.today())
    return Response({'status': 'Uploaded and categorized'})

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
