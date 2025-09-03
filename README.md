# MyChat: 나만의 카카오톡 챗봇

## 📝 프로젝트 개요

**MyChat**은 사용자의 카카오톡 대화 내용을 기반으로 개인화된 챗봇을 만들어주는 서비스입니다. RAG(Retrieval-Augmented Generation) 기술을 활용하여, 저장된 대화 데이터를 기반으로 사용자와 자연스럽게 대화하는 AI 챗봇을 경험할 수 있습니다.

<br>

## ✨ 주요 기능

- **💬 카카오톡 대화 분석 및 임베딩**: 사용자의 카카오톡 대화 파일을 전처리하고 벡터 데이터베이스에 저장합니다.
- **🤖 개인화된 AI 챗봇**: 저장된 대화 내용을 기반으로 사용자의 말투와 경험을 학습한 챗봇과 대화할 수 있습니다.
- **📖 대화 기록 조회**: 챗봇과 나눈 대화의 기록을 확인하고 관리할 수 있습니다.
- **🐳 Docker 기반 간편한 실행**: Docker Compose를 사용하여 한 번의 명령어로 전체 서비스를 손쉽게 구축하고 실행할 수 있습니다.

<br>

## 🛠️ 기술 스택

| 구분 | 기술 |
| --- | --- |
| **Backend** | Python, FastAPI, SQLAlchemy |
| **Frontend** | HTML, CSS, JavaScript |
| **Database** | MySQL, Qdrant (Vector DB) |
| **LLM** | OpenAI GPT |
| **Infrastructure** | Docker, Nginx |

<br>

## 🚀 설치 및 실행

1.  **프로젝트 클론**
    ```bash
    git clone https://github.com/your-username/MyChat.git
    cd MyChat
    ```

2.  **.env 파일 설정**
    -   프로젝트 루트 디렉토리에 `.env` 파일을 생성합니다.
    -   `Docs/환경변수 양식.md` 파일을 참고하여 아래와 같이 환경 변수를 설정합니다.
        ```env
        # 챗봇으로 만들고 싶은 발화자의 이름
        MAIN_SENDER=your_name

        # OpenAI API 키
        OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

        # DB 정보
        DB_HOST=mysql
        DB_PORT=3306
        DB_USER=your_db_user
        DB_PASSWORD=your_db_password
        DB_NAME=your_db_name

        # Qdrant 정보
        QDRANT_HOST=qdrant
        QDRANT_PORT=6333
        ```

3.  **카카오톡 대화 파일 준비**
    -   `Preprocessing/kakao_data/` 디렉토리 안에 분석할 카카오톡 대화 내용이 담긴 `chats.txt` 파일을 위치시킵니다.

4.  **Docker Compose 실행**
    -   프로젝트 루트 디렉토리에서 아래 명령어를 실행하여 모든 서비스를 빌드하고 실행합니다.
        ```bash
        docker-compose up --build -d
        ```
    -   최초 실행 시 `kakao-preprocess` 서비스가 대화 내용을 분석하고 Qdrant에 저장합니다. 이 과정은 데이터 크기에 따라 시간이 소요될 수 있습니다.

5.  **서비스 접속**
    -   모든 컨테이너가 정상적으로 실행되면 웹 브라우저에서 `http://localhost` 로 접속하여 챗봇 서비스를 이용할 수 있습니다.

<br>

## 💻 사용 방법

-   `http://localhost` 로 접속하면 챗봇과 대화할 수 있는 메인 화면이 나타납니다.
-   하단의 입력창에 메시지를 입력하여 자유롭게 대화를 시작할 수 있습니다.
-   챗봇은 `chats.txt` 에 담긴 대화 내용을 기반으로 답변을 생성합니다.

<br>

## 📄 API 문서

-   자세한 API 명세는 [Docs/api명세.md](./Docs/api명세.md) 파일에서 확인할 수 있습니다.

<br>
