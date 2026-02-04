import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize Groq client
# Ensure GROQ_API_KEY is set in your .env file
groq_client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify server status."""
    return jsonify({"status": "healthy", "service": "BizTone Converter API"}), 200

@app.route('/api/convert', methods=['POST'])
def convert_text():
    """
    Endpoint to convert text using Groq AI.
    Expected JSON payload:
    {
        "text": "Original text to convert",
        "target": "boss" | "colleague" | "client"
    }
    """
    data = request.get_json()
    
    if not data or 'text' not in data:
        return jsonify({"error": "No text provided"}), 400
    
    original_text = data['text']
    target_audience = data.get('target', 'boss') # Default to boss
    
    # Define system prompts based on target audience
    prompts = {
        "boss": "Convert the following text into a professional, respectful, and formal business tone suitable for reporting to a boss. Use appropriate honorifics (존댓말) and clear, concise language.",
        "colleague": "Convert the following text into a polite, cooperative, and professional business tone suitable for communicating with a colleague from another team. Use '해요' style (polite informal) but maintain professionalism.",
        "client": "Convert the following text into a highly formal, service-oriented, and respectful business tone suitable for communicating with an external customer. Use '하십시오' style (formal polite) and emphasize service mindset."
    }
    
    system_prompt = prompts.get(target_audience, prompts['boss'])
    
    try:
        # Call Groq API
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": original_text
                }
            ],
            model="llama3-8b-8192", # Using a fast, efficient model
            temperature=0.7,
            max_tokens=500,
        )
        
        converted_text = chat_completion.choices[0].message.content.strip()
        
        return jsonify({
            "original": original_text,
            "converted": converted_text,
            "target": target_audience
        }), 200

    except Exception as e:
        # In a real production app, log the full error securely
        print(f"Error calling Groq API: {e}")
        return jsonify({"error": "Failed to process text conversion"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
