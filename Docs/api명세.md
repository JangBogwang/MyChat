
# 📝 ChatBot API 명세서

본 API는 사용자 대화 기록을 기반으로 챗봇과의 대화 기능 및 대화 기록 조회 기능을 제공합니다.

---

## 📌 API 기본 정보

| 항목 | 값 |
|-------|-------|
| Base URL | `/api/v1/chat` |
| Content-Type | `application/json` |
| 인증 | (선택사항) JWT 토큰 또는 세션 |

---

## 1️⃣ **대화하기 API**

- **URL** : `/api/v1/chat`
- **Method** : `POST`
- **설명** : 사용자의 질문을 입력하면 챗봇의 응답을 반환하고, 대화 내역을 저장합니다.

### ✅ Request Body
```json
{
  "user_id": "string",         
  "message": "string"          
}
```

### ✅ Response
```json
{
  "code": "200",
  "message": "대화 응답 생성 완료",
  "data": {
    "user_id": "string",
    "request": "string",
    "response": "string",
    "timestamp": "ISO8601 string"
  }
}
```

---

## 2️⃣ **대화 기록 불러오기 API**

- **URL** : `/api/v1/chat`
- **Method** : `GET`
- **Query Params** :
  - `user_id` (필수) : 사용자 ID
  - `limit` (선택) : 가져올 최대 대화 수 (기본값 10)
  - `offset` (선택) : 페이징 offset (기본값 0)

### ✅ Response
```json
{
  "code": "200",
  "message": "대화 기록 조회 완료",
  "data": [
    {
      "request": "string",
      "response": "string",
      "timestamp": "ISO8601 string"
    }
  ]
}
```

---

## ⚠️ **에러 응답**
모든 API 공통 에러 형식:
```json
{
  "code": "4xx or 5xx",
  "message": "에러 메시지",
  "data": null
}
```
