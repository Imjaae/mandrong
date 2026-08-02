# AGENTS.md

## 프로젝트

프로젝트명은 만드롱(MANDRONG)이다. 디자인을 모르는 요식업 자영업자가 메뉴 사진과 홍보 문구를 입력하면 AI가 포스터, 배너, 메뉴판, SNS 홍보 이미지를 완성해주는 웹 서비스다.

## 작업 원칙

- 사용자는 전문 디자인 편집기처럼 요소를 직접 편집하지 않는다.
- UI는 매우 간단하고 정갈해야 한다.
- 한 화면에서 한 가지 행동에 집중한다.
- 생성된 홍보물이 가장 중요한 화면 요소다.
- 모든 UI 문구는 한국어로 작성한다.
- 과도한 그라데이션, 네온, 장식, 카드 남발을 금지한다.
- 모바일보다 데스크톱을 우선하되 반응형으로 구현한다.

## 필수 기술 스택

### Frontend

- Vue 3
- Vite
- TypeScript
- Pinia
- Vue Router
- Tailwind CSS
- Yarn
- Composition API
- `script setup`
- Vitest

### Backend

- Python 3.12 이상
- FastAPI
- SQLAlchemy 2
- Alembic
- Pydantic 2
- PostgreSQL
- Uvicorn
- Pytest

### E2E

- Playwright

### AI

- OpenAI API
- 이미지 생성 및 수정 모델은 `gpt-image-2`
- OpenAI API 호출은 반드시 FastAPI 서버에서만 수행한다.
- API 키를 프론트엔드에 절대 노출하지 않는다.

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

## 패키지 관리

- JavaScript/TypeScript는 Yarn workspace를 사용한다.
- Python 패키지는 `backend/requirements.txt` 하나로 관리한다.
- `backend/pyproject.toml`과 `requirements.txt`를 혼용하지 않는다.

## 개발 서버

- Vue Vite: `http://localhost:5173`
- FastAPI: `http://localhost:8000`
- PostgreSQL: `localhost:5432`

## 구현 순서 기준

1. 저장소 구조와 워크스페이스 설정
2. Docker Compose PostgreSQL
3. FastAPI 기본 앱, 설정, DB 연결
4. Alembic과 SQLAlchemy 모델
5. 프로젝트/브리프/자산 API
6. Vue 앱, 라우터, Pinia 기본 상태
7. 새 작업 생성 화면
8. 파일 업로드 화면
9. 이미지 생성 작업 API와 상태 폴링
10. 결과 화면과 히스토리
11. 포스트잇 메모 수정 플로우
12. 비율 재구성
13. PNG/JPEG/PDF 내보내기
14. Vitest, Pytest, Playwright 테스트

## 문서 우선순위

구현 전 다음 문서를 기준으로 삼는다.

- `docs/product-spec.md`
- `docs/screen-flow.md`
- `docs/architecture.md`
- `docs/database.md`
- `docs/api-spec.md`
- `docs/image-generation-flow.md`
- `docs/annotation-edit-flow.md`
- `docs/design-system.md`

문서와 구현이 충돌하면 먼저 문서를 갱신하고 구현한다.

## OpenAI 연동 주의

- 프론트엔드 코드에 `OPENAI_API_KEY`를 참조하지 않는다.
- 프론트엔드 번들에 OpenAI SDK를 포함하지 않는다.
- OpenAI 요청/응답 원문에 민감 정보가 들어갈 수 있으므로 로그에 전체를 남기지 않는다.
- 테스트에서는 실제 OpenAI API를 호출하지 않는다.

## 파일 저장 주의

- 업로드 원본명은 DB 메타데이터로만 저장한다.
- 실제 저장 파일명은 UUID 기반으로 만든다.
- `storage/uploads`, `storage/generated`, `storage/annotations`, `storage/exports`를 용도별로 분리한다.
- 파일 경로는 API 응답에 내부 경로 그대로 노출하지 않는다.
