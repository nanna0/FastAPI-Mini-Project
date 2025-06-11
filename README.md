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
| API      | OpenAI ChatGPT|
| Auth     | JWT (python-jose), bcrypt |

---

## 📁 프로젝트 구조
```cpp
📦project-root/

┣ 📄 auth.py # 로그인, 유저관리 
┣ 📄 main.py # FastAPI 메인 앱
┣ 📄 models.py # 모델 정의
┣ 📁 static
┃ ┗ 📄 index.html
┗ 📄 README.md
```
## ⚙️ 실행 방법
```
uvicorn main:app --reload
```
접속: http://127.0.0.1:8000

## WBS (Work Breakdown Structure)
```
gantt
    title FastAPI ChatGPT Mini Project WBS (일정 기반)
    dateFormat  YYYY-MM-DD
    section 프로젝트 초기 설정
    레포 생성, GSheet 기록        :done, task1, 2025-06-10, 1h
    ├─ 레포지토리 생성             :done, sub1, 2025-06-10, 0.1h
    ├─ 주제 확정 & WBS 작성        :done, sub2, 2025-06-10, 0.4h
    └─ 와이어프레임 작성           :done, sub3, 2025-06-10, 0.5h

    section 백엔드 환경 설정
    Python, FastAPI, DB, CORS      :active, task2, 2025-06-10 1.5h
    ├─ 가상환경 + FastAPI 세팅     :sub4, 2025-06-10, 0.5h
    ├─ DB 모델 설계 및 마이그레이션 :sub5, 2025-06-10, 0.5h
    └─ CORS 설정                   :sub6, 2025-06-10, 0.5h

    section API 및 인증 기능 설계
    API 구조 정리                 :task3, 2025-06-10, 1h
    ├─ 엔드포인트 목록 작성        :sub7, 2025-06-10, 0.5h
    └─ OpenAPI 문서 확인          :sub8, 2025-06-10, 0.5h

    section 로그인/회원가입 기능
    JWT 기반 인증 구현            :task4, 2025-06-11, 4h
    ├─ 비밀번호 해시 및 검증      :sub9, 2025-06-11, 0.5h
    ├─ JWT 토큰 생성/검증        :sub10, 2025-06-11, 1h
    ├─ /register 엔드포인트 구현  :sub11, 2025-06-11, 0.5h
    ├─ /login 엔드포인트 구현     :sub12, 2025-06-11, 0.5h
    ├─ 인증 데코레이터 구성       :sub13, 2025-06-11, 0.5h
    └─ /me, /chat 보호 설정       :sub14, 2025-06-11, 1h

```
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


