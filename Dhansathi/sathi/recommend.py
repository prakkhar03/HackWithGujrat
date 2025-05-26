def calculate_investable_amount(expenses, income=50000):
    total = sum(e.amount for e in expenses)
    return income - total

def generate_investment_advice(user, amount, risk_level):
    if amount <= 0:
        return "No surplus this month. Try spending less."
    if risk_level == 'high':
        return f"Invest ₹{amount} in equity mutual funds or stocks."
    elif risk_level == 'medium':
        return f"Split ₹{amount}: 60% mutual funds, 40% fixed income."
    else:
        return f"Invest ₹{amount} in safe debt funds, PPF, or FDs."
