import os
from dotenv import load_dotenv
import time

# Specify the correct path to your .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

import google.generativeai as genai

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


model = genai.GenerativeModel("gemini-1.5pro")

def get_chatbot_response(prompt, user_context=None):
    try:
      
        if user_context:
            context = f"""User Profile:
            - Income: {user_context.get('income', 'Not specified')}
            - Risk Tolerance: {user_context.get('risk_tolerance', 'Not specified')}
            - Investment Goals: {user_context.get('investment_goals', 'Not specified')}
            - Current Savings: {user_context.get('savings', 'Not specified')}
            
            Based on this profile, please provide personalized advice for the following query:
            {prompt}"""
            response = model.generate_content(context)
        else:
            response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        error_str = str(e)
        if "429" in error_str or "quota" in error_str.lower():
            return get_fallback_response(prompt, user_context)
        return "I apologize, but I'm having trouble processing your request right now. Please try again later."

def get_fallback_response(prompt, user_context=None):
    responses = {
        "invest": {
            "high": "For high-risk tolerance investors: Consider growth stocks, aggressive mutual funds, and emerging market investments. Maintain an emergency fund of 6 months expenses.",
            "medium": "For moderate-risk investors: Mix of index funds, blue-chip stocks, and bonds. Consider 60-40 equity-debt split.",
            "low": "For conservative investors: Focus on government bonds, fixed deposits, and low-risk mutual funds. Prioritize capital preservation."
        },
        "save": {
            "high": "With your income level, aim to save 30% of monthly income. Use tax-saving instruments and maximize retirement contributions.",
            "medium": "Try to save 20-25% of your income. Build emergency fund first, then focus on goal-based savings.",
            "low": "Start with saving 10-15% of income. Focus on reducing expenses and building an emergency fund."
        },
        "budget": {
            "high": "Use 50-30-20 rule: 50% needs, 30% wants, 20% savings/investments. Track using budgeting apps.",
            "medium": "Follow 60-20-20 rule: 60% needs, 20% wants, 20% savings. Review expenses monthly.",
            "low": "Use 70-20-10 rule: 70% needs, 20% savings, 10% wants. Focus on essential expenses."
        }
    }
    
    risk_level = user_context.get('risk_tolerance', 'medium') if user_context else 'medium'
    income_level = get_income_level(user_context.get('income', 50000)) if user_context else 'medium'
    
    prompt_lower = prompt.lower()
    for key, response_dict in responses.items():
        if key in prompt_lower:
            return response_dict.get(risk_level, response_dict['medium'])
            
    return f"""Based on your {risk_level} risk tolerance and {income_level} income level, here are some personalized financial tips:
1. Create a budget aligned with your income level
2. Build an emergency fund of {6 if income_level == 'high' else 3} months of expenses
3. Consider {get_investment_suggestions(risk_level)}
4. Review and rebalance your portfolio quarterly
5. Consider tax-saving investments suitable for your income bracket

For more specific advice, please consult with a financial advisor."""

def get_income_level(income):
    if income > 100000:
        return 'high'
    elif income > 50000:
        return 'medium'
    return 'low'

def get_investment_suggestions(risk_level):
    suggestions = {
        'high': 'growth stocks, aggressive mutual funds, and some cryptocurrency exposure',
        'medium': 'a mix of index funds, blue-chip stocks, and government bonds',
        'low': 'fixed deposits, government bonds, and low-risk mutual funds'
    }
    return suggestions.get(risk_level, suggestions['medium'])
