import google.generativeai as genai

genai.configure(api_key="xxx-xxx-xxx-xxx")  # Replace with your actual API key
models = genai.list_models()
for model in models:
    print(f"Name: {model.name}, Display Name: {model.display_name}")