import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from groq import Groq

# 1. 환경 변수 로드
# 현재 파일(app.py)의 위치를 기준으로 .env 파일을 찾습니다.
current_dir = os.path.dirname(os.path.abspath(__file__))
frontend_dir = os.path.join(current_dir, '..', 'frontend')
env_path = os.path.join(current_dir, '..', '.env')
load_dotenv(env_path)

app = Flask(__name__)
CORS(app)  # 프론트엔드와 통신을 위한 CORS 허용

# 2. Groq 클라이언트 초기화 및 디버깅
api_key = os.environ.get("GROQ_API_KEY")

# 서버 실행 시 터미널에서 키 로드 여부를 확인하기 위한 용도입니다.
if api_key:
    # 따옴표가 섞여 들어오는 경우를 대비해 제거 처리
    api_key = api_key.strip("'").strip('"')
    print(f"✅ Groq API Key loaded successfully (Starts with: {api_key[:10]}...)")
else:
    print("❌ Critical: GROQ_API_KEY not found in environment variables!")

groq_client = Groq(api_key=api_key)

# --- 정적 파일 서빙 로직 추가 ---

@app.route('/')
def serve_index():
    """메인 페이지(index.html) 서빙"""
    return send_from_directory(frontend_dir, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """CSS, JS 등 정적 파일 서빙"""
    return send_from_directory(frontend_dir, path)

# -----------------------------

@app.route('/health', methods=['GET'])
def health_check():
    """서버 상태 확인 엔드포인트"""
    return jsonify({"status": "healthy", "service": "BizTone Converter API"}), 200

@app.route('/api/convert', methods=['POST'])
def convert_text():
    """
    텍스트를 비즈니스 톤으로 변환하는 API
    JSON 데이터 예시: { "text": "안녕", "target": "boss" }
    """
    data = request.get_json()
    
    if not data or 'text' not in data:
        return jsonify({"error": "No text provided"}), 400
    
    original_text = data['text']
    target_audience = data.get('target', 'boss')
    
    # 타겟별 시스템 프롬프트 설정
    prompts = {
        "boss": "Convert the following text into a professional, respectful, and formal business tone suitable for reporting to a boss. Use appropriate honorifics (존댓말) and clear, concise language.",
        "colleague": "Convert the following text into a polite, cooperative, and professional business tone suitable for communicating with a colleague. Use '해요' style but maintain professionalism.",
        "client": "Convert the following text into a highly formal, service-oriented, and respectful business tone suitable for communicating with an external customer. Use '하십시오' style."
    }
    
    system_prompt = prompts.get(target_audience, prompts['boss'])
    
    try:
        # Groq API 호출
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": original_text}
            ],
            model="llama-3.3-70b-versatile",
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
        # 상세한 에러 내용을 서버 터미널에 출력
        print(f"🔥 Error during Groq API call: {str(e)}")
        return jsonify({
            "error": "Failed to process text conversion",
            "details": str(e)  # 클라이언트에게 에러 원인 전달 (디버깅용)
        }), 500

if __name__ == '__main__':
    # host='0.0.0.0'으로 설정해야 외부(브라우저 등) 접속이 원활합니다.
    app.run(debug=True, host='0.0.0.0', port=5000)