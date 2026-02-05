import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from groq import Groq

# 1. 환경 변수 로드
# 현재 파일(app.py)의 위치를 기준으로 .env 파일을 찾습니다.
current_dir = os.path.dirname(os.path.abspath(__file__))
# 루트 디렉토리 (backend의 상위)
root_dir = os.path.dirname(current_dir)
frontend_dir = os.path.join(root_dir, 'frontend')
env_path = os.path.join(root_dir, '.env')
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
    
    # 타겟별 시스템 프롬프트 설정 (페르소나 기반 프롬프트 엔지니어링)
    prompts = {
        "boss": (
            "You are a professional business communication assistant. "
            "Convert the user's input into a respectful, formal, and clear business tone suitable for reporting to a supervisor or boss (Upward communication). "
            "Follow these rules: 1. Use formal honorifics (존댓말, -습니다/하십시오 style). 2. Structure the message logically, starting with the main point. 3. Maintain professional boundaries and use standard business terminology. 4. Do not add any conversational filler before or after the conversion."
        ),
        "colleague": (
            "You are a professional business communication assistant. "
            "Convert the user's input into a polite, cooperative, and professional business tone suitable for communicating with a colleague or another team (Lateral communication). "
            "Follow these rules: 1. Use polite honorifics (해요 style). 2. Focus on collaboration and clear requests. 3. Use professional but slightly less rigid language than upward communication. 4. Include clear deadlines or action items if implied. 5. Do not add any conversational filler before or after the conversion."
        ),
        "client": (
            "You are a professional business communication assistant. "
            "Convert the user's input into a highly formal, service-oriented, and extremely respectful business tone suitable for external clients or customers (External communication). "
            "Follow these rules: 1. Use the highest level of honorifics (극존칭, -하십시오 style). 2. Emphasize service, gratitude, and professionalism. 3. Ensure the tone is welcoming yet authoritative. 4. Structure as a formal business message (Greeting -> Body -> Closing). 5. Do not add any conversational filler before or after the conversion."
        )
    }
    
    system_prompt = prompts.get(target_audience, prompts['boss'])
    
    print(f"--- Conversion Request ---")
    print(f"Target: {target_audience}")
    print(f"Original: {original_text}")

    try:
        # Groq API 호출 (Moonshot Kimi K2 모델 사용)
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Please convert this message: {original_text}"}
            ],
            model="moonshotai/kimi-k2-instruct-0905",
            temperature=0.3, # 일관성 있는 변환을 위해 온도를 낮춤
            max_tokens=1000,
        )
        
        converted_text = chat_completion.choices[0].message.content.strip()
        
        # 따옴표 등으로 감싸져서 반환되는 경우를 대비한 간단한 정제
        if (converted_text.startswith('"') and converted_text.endswith('"')) or \
           (converted_text.startswith("'") and converted_text.endswith("'")):
            converted_text = converted_text[1:-1]

        print(f"Converted: {converted_text}")
        print(f"--------------------------")
        
        return jsonify({
            "original": original_text,
            "converted": converted_text,
            "target": target_audience
        }), 200

    except Exception as e:
        error_msg = f"🔥 Error during Groq API call: {str(e)}"
        print(error_msg)
        return jsonify({
            "error": "변환 처리 중 오류가 발생했습니다.",
            "details": str(e) if app.debug else "Internal Server Error"
        }), 500

if __name__ == '__main__':
    # host='0.0.0.0'으로 설정해야 외부(브라우저 등) 접속이 원활합니다.
    app.run(host='127.0.0.1', port=5000, debug=True)