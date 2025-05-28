# import os
# from dotenv import load_dotenv
# import time


# load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

# import google.generativeai as genai

# genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


# model = genai.GenerativeModel("gemini-1.0-pro")

# def get_chatbot_response(prompt, user_context=None):
#     try:
      
#         if user_context:
#             context = f"""User Profile:
#             - Income: {user_context.get('income', 'Not specified')}
#             - Risk Tolerance: {user_context.get('risk_tolerance', 'Not specified')}
#             - Investment Goals: {user_context.get('investment_goals', 'Not specified')}
#             - Current Savings: {user_context.get('savings', 'Not specified')}
            
#             Based on this profile, please provide personalized advice for the following query:
#             {prompt}"""
#             response = model.generate_content(context)
#         else:
#             response = model.generate_content(prompt)
#         return response.text
#     except Exception as e:
#         error_str = str(e)
#         if "429" in error_str or "quota" in error_str.lower():
#             return get_fallback_response(prompt, user_context)
#         return "I apologize, but I'm having trouble processing your request right now. Please try again later."

# def get_fallback_response(prompt, user_context=None):
#     responses = {
#         "invest": {
#             "high": "For high-risk tolerance investors: Consider growth stocks, aggressive mutual funds, and emerging market investments. Maintain an emergency fund of 6 months expenses.",
#             "medium": "For moderate-risk investors: Mix of index funds, blue-chip stocks, and bonds. Consider 60-40 equity-debt split.",
#             "low": "For conservative investors: Focus on government bonds, fixed deposits, and low-risk mutual funds. Prioritize capital preservation."
#         },
#         "save": {
#             "high": "With your income level, aim to save 30% of monthly income. Use tax-saving instruments and maximize retirement contributions.",
#             "medium": "Try to save 20-25% of your income. Build emergency fund first, then focus on goal-based savings.",
#             "low": "Start with saving 10-15% of income. Focus on reducing expenses and building an emergency fund."
#         },
#         "budget": {
#             "high": "Use 50-30-20 rule: 50% needs, 30% wants, 20% savings/investments. Track using budgeting apps.",
#             "medium": "Follow 60-20-20 rule: 60% needs, 20% wants, 20% savings. Review expenses monthly.",
#             "low": "Use 70-20-10 rule: 70% needs, 20% savings, 10% wants. Focus on essential expenses."
#         }
#     }
    
#     risk_level = user_context.get('risk_tolerance', 'medium') if user_context else 'medium'
#     income_level = get_income_level(user_context.get('income', 50000)) if user_context else 'medium'
    
#     prompt_lower = prompt.lower()
#     for key, response_dict in responses.items():
#         if key in prompt_lower:
#             return response_dict.get(risk_level, response_dict['medium'])
            
#     return f"""Based on your {risk_level} risk tolerance and {income_level} income level, here are some personalized financial tips:
# 1. Create a budget aligned with your income level
# 2. Build an emergency fund of {6 if income_level == 'high' else 3} months of expenses
# 3. Consider {get_investment_suggestions(risk_level)}
# 4. Review and rebalance your portfolio quarterly
# 5. Consider tax-saving investments suitable for your income bracket

# For more specific advice, please consult with a financial advisor."""

# def get_income_level(income):
#     if income > 100000:
#         return 'high'
#     elif income > 50000:
#         return 'medium'
#     return 'low'

# def get_investment_suggestions(risk_level):
#     suggestions = {
#         'high': 'growth stocks, aggressive mutual funds, and some cryptocurrency exposure',
#         'medium': 'a mix of index funds, blue-chip stocks, and government bonds',
#         'low': 'fixed deposits, government bonds, and low-risk mutual funds'
#     }
#     return suggestions.get(risk_level, suggestions['medium'])

import os
from dotenv import load_dotenv
import time

# Specify the correct path to your .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

import google.generativeai as genai

# Debug: Print to verify API key is loaded
api_key = os.getenv("GOOGLE_API_KEY")
# print(f"API Key loaded: {'Yes' if api_key else 'No'}")
# print(f"API Key length: {len(api_key) if api_key else 0}")

if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in environment variables")

genai.configure(api_key=api_key)

# Use the latest model
model = genai.GenerativeModel("gemini-1.5-flash")

def get_chatbot_response(prompt, user_context=None):
    try:
        print(f"Processing prompt: {prompt[:50]}...")  # Debug log
        
        if user_context:
            context = f"""User Profile:
            - Income: {user_context.get('income', 'Not specified')}
            - Risk Tolerance: {user_context.get('risk_tolerance', 'Not specified')}
            - Investment Goals: {user_context.get('investment_goals', 'Not specified')}
            - Current Savings: {user_context.get('savings', 'Not specified')}
            
            Based on this profile, please provide personalized advice for the following query:
            {prompt}"""
        else:
            context = prompt
            
        # print("Sending request to Gemini...")  # Debug log
        
        # Add generation config for better control
        generation_config = {
            "temperature": 0.7,
            "top_p": 0.8,
            "top_k": 40,
            "max_output_tokens": 1024,
        }
        
        response = model.generate_content(
            context,
            generation_config=generation_config
        )
        
        print(f"Response received: {bool(response.text)}")  # Debug log
        
        # Check if response was blocked
        if hasattr(response, 'prompt_feedback'):
            if response.prompt_feedback.block_reason:
                print(f"Prompt was blocked: {response.prompt_feedback.block_reason}")
                return "Your request was blocked due to safety filters. Please rephrase your question."
        
        # Check for content filtering
        if not response.text:
            print("Empty response received")
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'finish_reason'):
                    print(f"Finish reason: {candidate.finish_reason}")
                    if candidate.finish_reason == "SAFETY":
                        return "Response was filtered for safety reasons. Please rephrase your question."
            return get_fallback_response(prompt, user_context)
            
        return response.text
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")  # Debug log
        error_str = str(e)
        
        # Handle specific error types
        if "429" in error_str or "quota" in error_str.lower():
            print("Rate limit/quota issue - using fallback")
            return get_fallback_response(prompt, user_context)
        elif "403" in error_str:
            return "API access denied. Please check your API key and billing status."
        elif "400" in error_str:
            return "Invalid request format. Please try rephrasing your question."
        elif "INVALID_API_KEY" in error_str:
            return "Invalid API key. Please check your Google API key configuration."
        else:
            return f"I apologize, but I'm having trouble processing your request: {error_str}"

def test_api_connection():
    """Test function to verify API is working"""
    try:
        print("Testing API connection...")
        test_response = model.generate_content("Say 'Hello, API is working!'")
        print(f"Test response: {test_response.text}")
        return True
    except Exception as e:
        print(f"API test failed: {str(e)}")
        return False

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

# Test the connection when module is imported
# if __name__ == "__main__":
#     if test_api_connection():
#         print("✅ Gemini API is working correctly!")
        
#         # Test with a sample financial query
#         test_context = {
#             'income': 75000,
#             'risk_tolerance': 'medium',
#             'investment_goals': 'retirement',
#             'savings': 10000
#         }
        
#         sample_response = get_chatbot_response("How should I invest my money?", test_context)
#         # print(f"\nSample response: {sample_response[:200]}...")
#     else:
#         print("❌ Gemini API connection failed!")