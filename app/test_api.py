import google.generativeai as genai
import sys

# --- PASTE YOUR KEY HERE ---
# Replace this placeholder string with your actual Google AI API Key
YOUR_API_KEY = "AIzaSyCKMPZbvf1I2Dq0cs37bh8jD45a4o2OU8I"
# -------------------------

if YOUR_API_KEY == "AIzaSyBgvrZaPNn1bmSYEjkGeGJAJxfaEGT2urw":
    print("="*50)
    print("!!! ERROR: You must edit this script and paste your API key")
    print("!!! into the `YOUR_API_KEY` variable on line 6.")
    print("="*50)
    sys.exit() # Stops the script

try:
    print(f"Configuring with API key ending in: ...{YOUR_API_KEY[-4:]}")
    genai.configure(api_key=YOUR_API_KEY)

    print("Successfully configured API key.")
    print("Listing available models your key can access...")
    print("="*30)

    found_models = False
    # This is the 'ListModels' call the error log mentioned
    for model in genai.list_models():
        # We only care about models that support 'generateContent'
        if 'generateContent' in model.supported_generation_methods:
            print(f"Found model: {model.name}")
            found_models = True
    
    if not found_models:
        print("No models with 'generateContent' were found for your key.")
        print("This might mean your project has a billing issue or is in a region that doesn't support these models.")

    print("="*30)
    print("Test complete.")
    print("\nWHAT TO DO NEXT:")
    print("1. If this printed model names (like 'models/gemini-pro'):")
    print("   Copy that *exact name* (e.g., 'models/gemini-pro') and paste it into your routes.py file.")
    print("\n2. If this printed an ERROR (like 'API key not valid' or 'permission denied'):")
    print("   Your API key is the problem. You must go to Google AI Studio and create a new key, or go to Google Cloud and enable the 'Generative Language API'.")


except Exception as e:
    print("\n" + "="*30)
    print("!!! TEST FAILED !!!")
    print(f"An error occurred: {e}")
    print("\nThis error confirms the problem is your API key or project setup.")
    print("Go to your Google dashboard (AI Studio or Cloud Console) to fix your API key or enable the API service.")
    print("Common errors are 'API key not valid' or 'permission denied'.")
