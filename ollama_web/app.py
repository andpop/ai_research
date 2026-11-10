# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "flask",
#     "ollama",
# ]
# ///
from flask import Flask, render_template, request, jsonify
import ollama

app = Flask(__name__)
MODEL_NAME = 'qwen2.5:1.5b'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    
    try:
        response = ollama.chat(
            model=MODEL_NAME,
            messages=[{'role': 'user', 'content': user_message}]
        )
        ai_response = response['message']['content']
        return jsonify({'response': ai_response})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print(f"=== Веб-чат с {MODEL_NAME} запущен ===")
    print("Откройте браузер: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
