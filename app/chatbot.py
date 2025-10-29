import google.generativeai as genai
from flask import jsonify, request
from app import app
import os

# Configure the Gemini API
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# Create the model
model = genai.GenerativeModel('gemini-pro-2.5')

# Context about the Alumni Portal
ALUMNI_CONTEXT = """
This is an Alumni Portal website with the following features:
- Alumni can register and create profiles
- Institutions can register and manage their alumni
- Users can view and participate in events
- Alumni can connect with each other
- Users can view alumni directories
- The portal facilitates networking between alumni and institutions
"""

@app.route('/chatbot', methods=['POST'])
def chatbot():
    try:
        data = request.json
        user_message = data.get('message', '')
        
        # Combine the context with user's message
        prompt = f"{ALUMNI_CONTEXT}\nUser: {user_message}\nAssistant:"
        
        # Generate response using Gemini
        response = model.generate_content(prompt)
        
        return jsonify({
            'response': response.text
        })
    except Exception as e:
        print(f"Error in chatbot route: {str(e)}")
        return jsonify({
            'response': 'Sorry, I encountered an error. Please try again.'
        }), 500