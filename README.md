# 💬 FastAPI ChatGPT Mini Project

> ChatGPT API를 활용한 로그인 기반 채팅 웹 애플리케이션  
> FastAPI 백엔드 + JS 프론트엔드 + OpenAI API 연동

---

## 🚀 프로젝트 소개

- FastAPI와 JavaScript를 이용한 채팅 웹 앱
- OpenAI ChatGPT API 연동으로 AI 챗봇 기능 구현
- HTML/CSS/JS로 UI 구성

---

## 🛠️ 기술 스택

| 구분     | 기술 |
|----------|------|
| Backend  | FastAPI, Uvicorn, Pydantic, Python|
| Frontend | HTML, CSS, JavaScript |
| API      | OpenAI ChatGPT (gpt-3.5-turbo) |
| Auth     | JWT (python-jose), bcrypt |
| ETC      | dotenv, passlib |

---

## 📁 프로젝트 구조
📦project-root/
┣ 📄 main.py # FastAPI 메인 앱
┣ 📄 models.py # 데이터 모델
┣ 📄 utils.py # JWT 및 해시 유틸
┣ 📄 .env # 환경 변수 파일 (OPENAI_API_KEY 등)
┣ 📄 templates/
┃ ┗ 📄 chat.html # 채팅 UI
┣ 📄 static/
┃ ┣ 📄 style.css # CSS 스타일
┃ ┗ 📄 app.js # JS 로직
┗ 📄 README.md

## 🔑 핵심 기능
- 사용자 회원가입 및 로그인 (JWT 기반)
- 로그인된 사용자만 채팅 가능
- ChatGPT API와 연동된 비동기 채팅
- 로딩 상태 표시 및 에러 처리
- UI: 채팅창, 입력창, 전송 버튼
- 채팅 기록 저장 및 조회

📸 와이어프레임

![image](https://github.com/user-attachments/assets/d602667f-e71e-4c77-96e6-a3dba46b421f)
![image](https://github.com/user-attachments/assets/534009a1-4f65-468c-b8e7-2210c648b19b)
![image](https://github.com/user-attachments/assets/ecdf86f2-2ed6-43d4-9b20-377f1e38e304)

## 📌 포트폴리오 목적
- FastAPI 활용 능력 시연
- OpenAI API 통신 구현 경험
- 사용자 인증/보안 및 프론트-백 통신 구현

## 🙋 기여자
- nanna0


