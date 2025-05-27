def calculate_investable_amount(expenses, income=50000):
    total = sum(e.amount for e in expenses)
    return income - total

def analyze_expense_pattern(expenses):
    categories = {}
    for expense in expenses:
        categories[expense.category] = categories.get(expense.category, 0) + expense.amount
    
    total = sum(categories.values())
    if total == 0:
        return None
        
    patterns = {
        cat: {
            'amount': amt,
            'percentage': (amt / total) * 100
        }
        for cat, amt in categories.items()
    }
    return patterns

def get_expense_recommendations(patterns):
    if not patterns:
        return "Start tracking your expenses to get personalized recommendations."
        
    recommendations = []
    
    # Check for high food expenses
    food_percent = patterns.get('Food', {}).get('percentage', 0)
    if food_percent > 30:
        recommendations.append("Your food expenses are high. Consider meal planning and cooking at home more often.")
    
    # Check for high entertainment expenses
    entertainment_percent = patterns.get('Entertainment', {}).get('percentage', 0)
    if entertainment_percent > 20:
        recommendations.append("Entertainment expenses could be reduced. Look for free or low-cost activities.")
    
    # Check for high shopping expenses
    shopping_percent = patterns.get('Shopping', {}).get('percentage', 0)
    if shopping_percent > 25:
        recommendations.append("Consider creating a shopping budget and avoiding impulse purchases.")
    
    return recommendations if recommendations else ["Your expense distribution looks reasonable."]

def generate_investment_advice(user, amount, risk_level):
    if amount <= 0:
        return "Currently your expenses exceed your income. Here are some suggestions:\n" + \
               "1. Review and cut non-essential expenses\n" + \
               "2. Look for additional income sources\n" + \
               "3. Create a strict budget\n" + \
               "4. Avoid taking on new debt"
               
    # Calculate monthly investment allocation
    emergency_fund = min(amount * 0.3, 50000)  # 30% or max 50k for emergency fund
    remaining = amount - emergency_fund
    
    risk_allocations = {
        'high': {
            'equity': 0.70,
            'debt': 0.20,
            'gold': 0.10
        },
        'medium': {
            'equity': 0.50,
            'debt': 0.40,
            'gold': 0.10
        },
        'low': {
            'equity': 0.30,
            'debt': 0.60,
            'gold': 0.10
        }
    }
    
    allocation = risk_allocations.get(risk_level, risk_allocations['medium'])
    
    advice = f"""Investment Advice based on your risk profile ({risk_level}) and surplus amount (₹{amount}):

1. Emergency Fund (Priority):
   - Set aside ₹{emergency_fund:.0f} in a high-yield savings account or liquid fund
   
2. Investment Allocation for remaining ₹{remaining:.0f}:
   - Equity: ₹{(remaining * allocation['equity']):.0f}
     * {get_equity_suggestions(risk_level)}
   
   - Debt: ₹{(remaining * allocation['debt']):.0f}
     * {get_debt_suggestions(risk_level)}
   
   - Gold: ₹{(remaining * allocation['gold']):.0f}
     * Consider Sovereign Gold Bonds or Gold ETFs

3. Additional Recommendations:
   - Review and rebalance portfolio quarterly
   - Consider tax-saving investments under Section 80C
   - Set up automatic monthly investments (SIP)
   """
    
    return advice

def get_equity_suggestions(risk_level):
    suggestions = {
        'high': "Focus on mid-cap and small-cap mutual funds, with some exposure to international funds",
        'medium': "Mix of large-cap and mid-cap mutual funds through index funds",
        'low': "Stick to large-cap mutual funds and blue-chip stocks"
    }
    return suggestions.get(risk_level, suggestions['medium'])

def get_debt_suggestions(risk_level):
    suggestions = {
        'high': "Corporate bonds and dynamic bond funds",
        'medium': "Government securities and high-rated corporate bonds",
        'low': "Fixed deposits and government bonds"
    }
    return suggestions.get(risk_level, suggestions['medium'])

def get_smart_recommendations(patterns, monthly_income, current_savings, savings_goal, risk_tolerance, investment_goals):
    """Generate smart, personalized recommendations based on user's financial data."""
    recommendations = []
    
    def get_rec_id(prefix):
        import uuid
        return f"{prefix}_{str(uuid.uuid4())[:8]}"
    
    # Use savings_goal as the target amount since this is what user wants to save
    target_savings = savings_goal
    
    # 1. Maximum Savings Recommendation
    if target_savings > 0:
        recommendations.append({
            'id': get_rec_id('savings'),
            'type': 'opportunity',
            'title': 'Your Savings Target',
            'description': f'You aim to save ₹{target_savings:,.0f} per month. Let\'s help you achieve this goal!',
            'amount': target_savings,
            'action': 'Set Up Auto-Save'
        })
        
        # Investment suggestions based on target savings
        if target_savings >= 1000:  # Minimum threshold for investment suggestions
            if risk_tolerance == 'low':
                # Conservative allocation: 70% safe investments, 30% liquid
                safe_invest = target_savings * 0.7
                recommendations.append({
                    'id': get_rec_id('invest'),
                    'type': 'opportunity',
                    'title': 'Safe Investment Plan',
                    'description': f'Invest ₹{safe_invest:,.0f} in Fixed Deposits (8.5% p.a.) and Government Securities. Keep ₹{(target_savings - safe_invest):,.0f} as emergency fund.',
                    'amount': safe_invest,
                    'action': 'View Options'
                })
            elif risk_tolerance == 'medium':
                # Balanced allocation: 80% investments (mixed), 20% liquid
                balanced_invest = target_savings * 0.8
                recommendations.append({
                    'id': get_rec_id('invest'),
                    'type': 'opportunity',
                    'title': 'Balanced Investment Plan',
                    'description': f'Invest ₹{balanced_invest:,.0f} in Mutual Funds (mix of equity and debt, potential 12-15% returns). Keep ₹{(target_savings - balanced_invest):,.0f} liquid.',
                    'amount': balanced_invest,
                    'action': 'View Portfolio'
                })
            else:  # high risk tolerance
                # Aggressive allocation: 90% investments, 10% liquid
                growth_invest = target_savings * 0.9
                recommendations.append({
                    'id': get_rec_id('invest'),
                    'type': 'opportunity',
                    'title': 'Growth Investment Plan',
                    'description': f'Invest ₹{growth_invest:,.0f} in Equity Funds and Stocks (potential 15-18% returns). Keep ₹{(target_savings - growth_invest):,.0f} as buffer.',
                    'amount': growth_invest,
                    'action': 'View Options'
                })

            # Add SIP recommendation
            recommendations.append({
                'id': get_rec_id('sip'),
                'type': 'opportunity',
                'title': 'Start Monthly SIP',
                'description': f'Set up a Systematic Investment Plan (SIP) of ₹{(target_savings * 0.5):,.0f} for long-term wealth creation.',
                'amount': target_savings * 0.5,
                'action': 'Setup SIP'
            })
    
    # 2. Emergency Fund Progress
    if current_savings < target_savings * 6:  # 6 months of target savings as emergency fund
        emergency_target = target_savings * 6
        recommendations.append({
            'id': get_rec_id('emergency'),
            'type': 'alert',
            'title': 'Build Emergency Fund',
            'description': f'Aim to save ₹{emergency_target:,.0f} (6 months of savings target) as emergency fund. Currently short by ₹{(emergency_target - current_savings):,.0f}.',
            'amount': emergency_target - current_savings,
            'action': 'Learn More'
        })
    
    # 3. Goal-based Investment Suggestion
    if investment_goals:
        # Calculate long-term investment potential
        yearly_potential = target_savings * 12
        recommendations.append({
            'id': get_rec_id('goals'),
            'type': 'opportunity',
            'title': 'Yearly Investment Potential',
            'description': f'With your savings target, you can invest ₹{yearly_potential:,.0f} annually towards your goals: {investment_goals}.',
            'amount': yearly_potential,
            'action': 'Create Plan'
        })
    
    return recommendations[:5]  # Return top 5 recommendations
