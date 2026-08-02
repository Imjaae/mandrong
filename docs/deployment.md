# 배포 가이드

## 권장 임시 배포 구조

- Frontend: Vercel
- Backend: Render 또는 Railway의 Python Web Service
- Database: 배포 서비스의 PostgreSQL
- Storage: 임시 배포는 백엔드 persistent disk/volume 사용

Vercel만으로 전체 기능을 배포하지 않는다. FastAPI에서 OpenAI API를 호출하고 업로드/생성 파일을 저장해야 하므로 백엔드는 별도 서버가 필요하다.

## Backend 환경변수

```env
APP_ENV=production
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:PORT/DB
OPENAI_API_KEY=sk-...
WEB_ORIGINS=https://your-vercel-domain.vercel.app,https://your-production-domain.com
STORAGE_ROOT=/var/data/storage
MAX_UPLOAD_MB=20
```

## Backend 실행 명령

Render/Railway에서 `backend` 디렉터리를 서비스 루트로 지정한다.

Build command:

```bash
pip install -r requirements.txt
```

Start command:

```bash
./start.sh
```

`start.sh`는 서버 시작 전에 `alembic upgrade head`를 실행한다.

## Frontend 환경변수

Vercel 프로젝트의 Root Directory를 `frontend`로 지정한다.

```env
VITE_API_BASE=https://your-api-domain.com
```

Build command와 output은 `frontend/vercel.json`에 정의되어 있다.

## 배포 순서

1. GitHub 저장소에 현재 코드를 push한다.
2. Render/Railway에서 PostgreSQL을 만든다.
3. Render/Railway에서 `backend`를 Python Web Service로 배포한다.
4. 백엔드 환경변수에 `DATABASE_URL`, `OPENAI_API_KEY`, `STORAGE_ROOT`를 설정한다.
5. 백엔드 배포 URL의 `/health`가 `{"status":"ok"}`를 반환하는지 확인한다.
6. Vercel에서 `frontend`를 배포한다.
7. Vercel 환경변수 `VITE_API_BASE`에 백엔드 URL을 넣는다.
8. 백엔드 환경변수 `WEB_ORIGINS`에 Vercel URL을 추가하고 백엔드를 재배포한다.

## 주의사항

- OpenAI API 키는 Vercel에 넣지 않는다.
- 임시 배포에서 백엔드 디스크가 persistent가 아니면 업로드/생성 이미지가 사라진다.
- 장기 운영 전에는 로컬 파일 저장을 S3/R2 같은 오브젝트 스토리지로 바꾸는 것이 좋다.
