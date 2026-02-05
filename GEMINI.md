# GEMINI.md

## 프로젝트 개요 (Project Overview)

**BizTone Converter**는 일상적인 표현이나 비공식적인 문장을 전문적인 비즈니스 언어로 변환해주는 AI 기반 웹 솔루션입니다. 신입사원이나 비즈니스 커뮤니케이션에 익숙하지 않은 직장인들이 대상(**상사, 동료, 고객**)에 맞춰 적절한 톤앤매너를 갖출 수 있도록 돕습니다.

### 핵심 기술 스택
- **프론트엔드:** HTML5, Tailwind CSS (Play CDN 방식), JavaScript (ES6+).
- **백엔드:** Python 3.11+, Flask.
- **AI 통합:** Groq API 및 `moonshotai/kimi-k2-instruct-0905` 모델 사용 (Temperature 0.3 설정으로 일관성 확보).
- **디자인:** Tailwind CSS와 Pretendard 폰트를 활용한 밝고 깔끔하며 현대적인 UI.

### 아키텍처
프로젝트는 프론트엔드와 백엔드가 분리된 구조를 따릅니다.
- **`frontend/`**: 정적 자산(HTML, JS) 포함.
- **`backend/`**: Groq AI 서비스와 연동되는 Flask 기반 REST API (페르소나 기반 프롬프트 엔지니어링 적용).
- **통신:** 프론트엔드에서 `/api/convert` 엔드포인트로 비동기 `fetch` 호출을 수행합니다.

---

## 빌드 및 실행 방법 (Building and Running)

### 사전 요구 사항
- Python 3.11 이상.
- Groq API 키 (`.env` 파일에 저장 필요).

### 설정 (Setup)
1. **리포지토리를 클론하고 프로젝트 루트 디렉토리로 이동합니다.**
2. **가상 환경 생성 및 활성화:**
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\activate
   ```
3. **의존성 설치:**
   ```powershell
   pip install -r backend/requirements.txt
   ```
4. **환경 변수 설정:**
   루트 디렉토리에 `.env` 파일을 생성하고 Groq API 키를 추가합니다:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   ```

### 애플리케이션 실행
1. **Flask 서버 시작:**
   ```powershell
   python backend/app.py
   ```
2. **브라우저 접속:**
   `http://localhost:5000` 주소로 접속합니다.

### 테스트
- **API 상태 확인:** `GET http://localhost:5000/health`
- **UI 테스트:** "원문 입력" 영역에 텍스트를 입력하고 대상을 선택한 후 "변환하기" 버튼을 클릭합니다.

---

## 개발 컨벤션 (Development Conventions)

### 프론트엔드
- **Utility-First CSS:** Tailwind CSS 클래스를 HTML 내에 직접 사용합니다. 꼭 필요한 경우가 아니면 외부 CSS 파일을 생성하지 않습니다.
- **Pretendard 폰트:** 일관된 한국어 타이포그래피를 위해 Pretendard 폰트를 사용합니다.
- **DOM 조작:** 로딩 표시, 글자 수 체크 등 UI 상태 관리는 순수 JavaScript(Vanilla JS)를 사용합니다.
- **반응형 디자인:** Mobile-first 원칙을 따르며, 화면 너비가 768px 이하일 때 카드가 세로로 쌓이도록 구성합니다.

### 백엔드
- **RESTful API:** 데이터 처리 로직과 UI 라우팅 로직을 명확히 분리합니다.
- **프롬프트 엔지니어링:** 대상별 맞춤형 페르소나 기반 프롬프트는 `backend/app.py`에 정의되어 있습니다. 상사(보고형), 동료(협조형), 고객(서비스형)에 최적화된 지시문을 사용합니다.
- **모델 설정:** 일관성 있는 변환 결과를 위해 `temperature=0.3`을 유지하며, AI가 불필요한 서술(conversational filler)을 추가하지 않도록 엄격한 규칙을 적용합니다.
- **환경 변수 보안:** API 키를 코드에 직접 하드코딩하지 않습니다. 반드시 `python-dotenv`를 사용하여 `.env` 파일에서 로드합니다.
- **에러 처리:** 명확한 JSON 에러 메시지(`{"error": "...", "details": "..."}`)와 적절한 HTTP 상태 코드를 반환합니다.

### 프로젝트 구조
- `backend/app.py`: API 엔드포인트 및 정적 파일 라우팅의 메인 엔트리 포인트.
- `frontend/index.html`: 메인 UI 템플릿.
- `frontend/js/script.js`: API 호출 및 UI 업데이트를 위한 클라이언트 측 로직.
- `PRD.md`: 제품 요구사항 및 스프린트 계획의 기준 문서.