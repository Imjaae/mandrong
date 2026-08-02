# 아키텍처

## 기술 스택

### Frontend

- Vue 3
- Vite
- TypeScript
- Pinia
- Vue Router
- Tailwind CSS
- Yarn workspace
- Composition API
- `script setup`
- Vitest
- Playwright

### Backend

- Python 3.12 이상
- FastAPI
- SQLAlchemy 2
- Alembic
- Pydantic 2
- PostgreSQL
- Uvicorn
- Pytest

### AI

- OpenAI API
- 이미지 생성 및 수정 모델: `gpt-image-2`
- OpenAI API 호출은 FastAPI 서버에서만 수행
- 프론트엔드에는 API 키, OpenAI SDK, OpenAI 엔드포인트를 두지 않는다.

## 저장소 구조

```text
mandrong/
├── frontend/
├── backend/
├── design-references/
├── storage/
│   ├── uploads/
│   ├── generated/
│   ├── annotations/
│   └── exports/
├── docs/
├── scripts/
├── AGENTS.md
├── package.json
├── yarn.lock
├── docker-compose.yml
├── .env.example
└── README.md
```

## 런타임 구성

| 서비스 | 주소 | 역할 |
| --- | --- | --- |
| Web | `http://localhost:5173` | 사용자 화면 |
| API | `http://localhost:8000` | 인증 없는 MVP API, 파일 처리, OpenAI 호출 |
| Local SQLite | `backend/mandrong.db` | Docker 없이 개발할 때 작업, 버전, 주석, 내보내기 메타데이터 저장 |
| PostgreSQL | `localhost:5432` | PostgreSQL 전환 시 작업, 버전, 주석, 내보내기 메타데이터 저장 |

## Frontend 구성

### 디렉터리

```text
frontend/
├── src/
│   ├── app/
│   ├── pages/
│   ├── components/
│   ├── stores/
│   ├── api/
│   ├── router/
│   ├── types/
│   └── styles/
├── index.html
├── vite.config.ts
├── tailwind.config.ts
└── package.json
```

### 책임

- 사용자 입력 수집
- 파일 업로드 요청
- 생성/수정 상태 표시
- 이미지 위 주석 좌표 수집
- 생성 결과 비교 및 적용 요청
- 다운로드 트리거

### 금지

- OpenAI API 직접 호출
- OpenAI API 키 저장
- 클라이언트에서 생성 프롬프트 최종 조립
- 이미지 생성 결과를 클라이언트 로컬 상태에만 저장

## Backend 구성

### 디렉터리

```text
backend/
├── app/
│   ├── main.py
│   ├── api/
│   ├── core/
│   ├── db/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   └── workers/
├── alembic/
├── tests/
└── requirements.txt
```

Python 패키지는 `backend/requirements.txt` 하나만 사용한다. `pyproject.toml`은 패키지 관리 목적으로 만들지 않는다.

### 계층

- `api`: FastAPI 라우터
- `schemas`: Pydantic 2 요청/응답 모델
- `models`: SQLAlchemy 2 ORM 모델
- `services`: 비즈니스 로직, OpenAI 호출, 파일 저장
- `db`: 세션, 마이그레이션 공통 코드
- `core`: 설정, 로깅, 예외, 보안 설정
- `workers`: 긴 작업 실행 함수. MVP에서는 API 프로세스 내부 백그라운드 태스크로 시작하고, 추후 큐로 분리 가능하게 작성한다.

## 데이터 흐름

1. Web이 프로젝트 초안을 API에 저장한다.
2. Web이 메뉴 사진과 참고 이미지를 API에 업로드한다.
3. API가 파일을 `storage/uploads`에 저장하고 DB에 `Asset`을 생성한다.
4. Web이 생성 요청을 보낸다.
5. API가 DB에 `GenerationJob`을 만들고 상태를 `queued`로 저장한다.
6. API 백그라운드 작업이 프롬프트를 조립하고 `gpt-image-2`를 호출한다.
7. API가 결과 이미지를 `storage/generated`에 저장하고 `GenerationVersion`을 만든다.
8. Web이 작업 상태를 조회하고 완료 시 결과 화면으로 이동한다.
9. 수정 요청도 같은 방식으로 새 `GenerationJob`과 새 `GenerationVersion`을 만든다.

## 파일 저장

| 경로 | 내용 |
| --- | --- |
| `storage/uploads` | 사용자 업로드 원본 |
| `storage/generated` | 생성 및 수정 이미지 |
| `storage/annotations` | 주석 스냅샷 JSON, 선택 영역 마스크 |
| `storage/exports` | PNG, JPEG, PDF 결과 |

파일명은 사용자가 올린 원본명을 그대로 사용하지 않는다. 서버가 UUID 기반 이름을 만들고 원본명은 DB에만 저장한다.

## 환경 변수

| 이름 | 필수 | 설명 |
| --- | --- | --- |
| `DATABASE_URL` | 예 | 로컬 개발은 `sqlite:///./mandrong.db`, PostgreSQL 사용 시 PostgreSQL 연결 문자열 |
| `OPENAI_API_KEY` | 예 | 서버 전용 OpenAI API 키 |
| `APP_ENV` | 예 | `local`, `test`, `production` |
| `STORAGE_ROOT` | 예 | 파일 저장 루트 |
| `WEB_ORIGIN` | 예 | CORS 허용 웹 주소 |
| `MAX_UPLOAD_MB` | 아니오 | 기본 20 |

## 오류 처리

API 오류 응답은 항상 같은 형태를 사용한다.

```json
{
  "error": {
    "code": "GENERATION_FAILED",
    "message": "이미지 생성에 실패했어요.",
    "details": {
      "retryable": true
    }
  }
}
```

## 테스트 전략

- Vitest: 입력 폼 검증, Pinia 상태 전이, API 클라이언트 오류 처리
- Pytest: 서비스 로직, DB 모델, API 계약, 파일 저장
- Playwright: 새 작업 생성, 이미지 생성 실패/성공 모의, 메모 수정, 다운로드 플로우

OpenAI 호출은 테스트에서 실제 호출하지 않는다. 서버 서비스 계층을 모킹하고, 응답 파일 저장과 DB 상태 전이를 검증한다.
