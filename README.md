# MANDRONG

만드롱(MANDRONG)은 디자인을 모르는 요식업 자영업자가 메뉴 사진과 홍보 문구를 입력해 AI 홍보 이미지를 생성, 수정, 재구성, 다운로드하는 웹 서비스다.

## 개발 환경

- Web: Vue 3, Vite, TypeScript, Pinia, Vue Router, Tailwind CSS
- API: Python 3.12, FastAPI, SQLAlchemy 2, Alembic, Pydantic 2
- DB: SQLite for local development, PostgreSQL optional
- AI: OpenAI `gpt-image-2`

## 실행

```bash
yarn install
cd backend
python3.12 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --port 8000
```

다른 터미널에서:

```bash
yarn dev
```

- Web: http://localhost:5173
- API: http://localhost:8000
- Local DB: `backend/mandrong.db`

## 환경 변수

`.env.example`을 참고해 `backend/.env`를 설정한다. `OPENAI_API_KEY`는 서버에서만 사용하고 프론트엔드에는 노출하지 않는다.

Docker 없이 바로 실행하려면 `DATABASE_URL=sqlite:///./mandrong.db`를 사용한다. PostgreSQL로 전환할 때만 `docker compose up -d`와 `alembic upgrade head`를 사용한다.
