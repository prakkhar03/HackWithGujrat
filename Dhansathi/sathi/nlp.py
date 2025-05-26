from transformers import pipeline

chatbot = pipeline("text-generation", model="gpt2")

def get_chatbot_response(prompt):
    result = chatbot(prompt, max_length=100, do_sample=True)
    return result[0]['generated_text']
