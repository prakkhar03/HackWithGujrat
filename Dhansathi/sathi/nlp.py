import os
from dotenv import load_dotenv
import time

# Specify the correct path to your .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

import google.generativeai as genai

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Using the standard gemini-pro model which has better rate limits
model = genai.GenerativeModel("gemini-pro")

def get_chatbot_response(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        error_str = str(e)
        if "429" in error_str or "quota" in error_str.lower():
            # Return a pre-defined response for common financial queries
            return get_fallback_response(prompt)
        return "I apologize, but I'm having trouble processing your request right now. Please try again later."

def get_fallback_response(prompt):
    # Common financial advice responses
    responses = {
        "invest": "For investment advice, consider: 1) Diversifying your portfolio 2) Starting with low-risk options 3) Consulting a financial advisor",
        "save": "To improve savings: 1) Create a budget 2) Set up automatic transfers 3) Cut unnecessary expenses 4) Follow the 50/30/20 rule",
        "budget": "Budgeting tips: 1) Track all expenses 2) Categorize spending 3) Set realistic goals 4) Review and adjust monthly",
        "debt": "To manage debt: 1) List all debts 2) Prioritize high-interest debt 3) Consider debt consolidation 4) Create a repayment plan",
        "expense": "To reduce expenses: 1) Review subscriptions 2) Plan meals 3) Use cashback cards 4) Compare service providers",
    }
    
    # Find the most relevant pre-defined response based on the prompt
    prompt_lower = prompt.lower()
    for key, response in responses.items():
        if key in prompt_lower:
            return response
            
    # Default response if no specific match is found
    return """Here are some general financial tips:
1. Create and stick to a budget
2. Build an emergency fund
3. Invest for the long term
4. Minimize high-interest debt
5. Save regularly for your goals

For personalized advice, please consult with a financial advisor."""
