# 데이터베이스 설계

## 전제

- DB는 PostgreSQL을 사용한다.
- ORM은 SQLAlchemy 2를 사용한다.
- 마이그레이션은 Alembic으로 관리한다.
- 파일 바이너리는 DB에 저장하지 않고 `storage/` 하위 파일 경로만 저장한다.
- 시간 컬럼은 UTC 기준 `TIMESTAMP WITH TIME ZONE`을 사용한다.

## Enum

### `project_status`

- `draft`
- `generating`
- `generated`
- `editing`
- `ready`
- `exporting`
- `failed`

### `asset_type`

- `menu_photo`
- `reference_image`
- `generated_image`
- `edited_image`
- `export_file`

### `generation_job_type`

- `initial`
- `edit`
- `reframe`

### `job_status`

- `queued`
- `running`
- `succeeded`
- `failed`
- `cancelled`

### `export_format`

- `png`
- `jpeg`
- `pdf`

## 테이블

## `projects`

| 컬럼 | 타입 | 제약 | 설명 |
| --- | --- | --- | --- |
| `id` | UUID | PK | 작업 ID |
| `title` | VARCHAR(120) | NOT NULL | 작업 제목 |
| `status` | project_status | NOT NULL | 작업 상태 |
| `current_version_id` | UUID | FK nullable | 현재 적용된 버전 |
| `created_at` | TIMESTAMPTZ | NOT NULL | 생성 시각 |
| `updated_at` | TIMESTAMPTZ | NOT NULL | 수정 시각 |

인덱스:

- `idx_projects_created_at`
- `idx_projects_status`

## `creative_briefs`

| 컬럼 | 타입 | 제약 | 설명 |
| --- | --- | --- | --- |
| `id` | UUID | PK | 브리프 ID |
| `project_id` | UUID | FK unique | 작업 ID |
| `purpose` | VARCHAR(40) | NOT NULL | 홍보물 유형 |
| `width` | INTEGER | NOT NULL | 출력 너비 |
| `height` | INTEGER | NOT NULL | 출력 높이 |
| `primary_copy` | VARCHAR(80) | NOT NULL | 전체 홍보 문구에서 자동 추출한 대표 문구 |
| `secondary_copy` | TEXT | nullable | 사용자가 입력한 전체 홍보 문구 |
| `price_copy` | VARCHAR(120) | nullable | 호환용 가격/혜택 문구. 신규 UI에서는 직접 입력하지 않음 |
| `notice_copy` | VARCHAR(240) | nullable | 안내 문구 |
| `store_name` | VARCHAR(120) | nullable | 매장명 |
| `menu_name` | VARCHAR(120) | nullable | 메뉴명 |
| `price` | VARCHAR(80) | nullable | 가격 |
| `store_location` | VARCHAR(160) | nullable | 지역/주소 |
| `contact` | VARCHAR(120) | nullable | 전화번호/주문 방법 |
| `mood_keywords` | JSONB | NOT NULL | 분위기 키워드 배열 |
| `mood_text` | TEXT | nullable | 자유 분위기 설명 |
| `created_at` | TIMESTAMPTZ | NOT NULL | 생성 시각 |
| `updated_at` | TIMESTAMPTZ | NOT NULL | 수정 시각 |

검증:

- `width > 0`
- `height > 0`
- `primary_copy`는 빈 문자열 불가

## `assets`

| 컬럼 | 타입 | 제약 | 설명 |
| --- | --- | --- | --- |
| `id` | UUID | PK | 자산 ID |
| `project_id` | UUID | FK nullable | 관련 작업 |
| `version_id` | UUID | FK nullable | 관련 버전 |
| `type` | asset_type | NOT NULL | 자산 유형 |
| `original_filename` | VARCHAR(255) | nullable | 업로드 원본명 |
| `storage_path` | TEXT | NOT NULL | 서버 내부 경로 |
| `public_path` | TEXT | nullable | API로 제공할 경로 |
| `mime_type` | VARCHAR(100) | NOT NULL | MIME 타입 |
| `size_bytes` | BIGINT | NOT NULL | 파일 크기 |
| `width` | INTEGER | nullable | 이미지 너비 |
| `height` | INTEGER | nullable | 이미지 높이 |
| `checksum` | VARCHAR(128) | nullable | 중복 확인용 해시 |
| `created_at` | TIMESTAMPTZ | NOT NULL | 생성 시각 |

인덱스:

- `idx_assets_project_id`
- `idx_assets_version_id`
- `idx_assets_type`

## `generation_jobs`

| 컬럼 | 타입 | 제약 | 설명 |
| --- | --- | --- | --- |
| `id` | UUID | PK | 생성 작업 ID |
| `project_id` | UUID | FK | 작업 ID |
| `source_version_id` | UUID | FK nullable | 수정/재구성 기준 버전 |
| `type` | generation_job_type | NOT NULL | 작업 유형 |
| `status` | job_status | NOT NULL | 작업 상태 |
| `request_payload` | JSONB | NOT NULL | 서버가 구성한 요청 요약 |
| `prompt_text` | TEXT | NOT NULL | 최종 프롬프트 |
| `error_code` | VARCHAR(80) | nullable | 실패 코드 |
| `error_message` | TEXT | nullable | 실패 메시지 |
| `started_at` | TIMESTAMPTZ | nullable | 시작 시각 |
| `finished_at` | TIMESTAMPTZ | nullable | 종료 시각 |
| `created_at` | TIMESTAMPTZ | NOT NULL | 생성 시각 |

인덱스:

- `idx_generation_jobs_project_id`
- `idx_generation_jobs_status`

## `generation_versions`

| 컬럼 | 타입 | 제약 | 설명 |
| --- | --- | --- | --- |
| `id` | UUID | PK | 버전 ID |
| `project_id` | UUID | FK | 작업 ID |
| `job_id` | UUID | FK | 생성 작업 ID |
| `parent_version_id` | UUID | FK nullable | 이전 버전 |
| `image_asset_id` | UUID | FK | 결과 이미지 자산 |
| `version_number` | INTEGER | NOT NULL | 프로젝트 내 버전 번호 |
| `width` | INTEGER | NOT NULL | 이미지 너비 |
| `height` | INTEGER | NOT NULL | 이미지 높이 |
| `summary` | VARCHAR(240) | nullable | 변경 요약 |
| `is_applied` | BOOLEAN | NOT NULL | 현재 적용 여부 |
| `created_at` | TIMESTAMPTZ | NOT NULL | 생성 시각 |

제약:

- `(project_id, version_number)` unique
- 현재 버전은 프로젝트당 하나만 `is_applied = true`

## `annotations`

| 컬럼 | 타입 | 제약 | 설명 |
| --- | --- | --- | --- |
| `id` | UUID | PK | 주석 ID |
| `project_id` | UUID | FK | 작업 ID |
| `version_id` | UUID | FK | 대상 버전 |
| `note` | VARCHAR(300) | NOT NULL | 수정 메모 |
| `x` | NUMERIC(6,5) | NOT NULL | 정규화 좌표 |
| `y` | NUMERIC(6,5) | NOT NULL | 정규화 좌표 |
| `width` | NUMERIC(6,5) | nullable | 선택 영역 너비 |
| `height` | NUMERIC(6,5) | nullable | 선택 영역 높이 |
| `color` | VARCHAR(20) | NOT NULL | 포스트잇 색상 |
| `created_at` | TIMESTAMPTZ | NOT NULL | 생성 시각 |

검증:

- `x`, `y`, `width`, `height`는 0 이상 1 이하
- `note`는 빈 문자열 불가

## `export_jobs`

| 컬럼 | 타입 | 제약 | 설명 |
| --- | --- | --- | --- |
| `id` | UUID | PK | 내보내기 작업 ID |
| `project_id` | UUID | FK | 작업 ID |
| `version_id` | UUID | FK | 대상 버전 |
| `format` | export_format | NOT NULL | 파일 형식 |
| `status` | job_status | NOT NULL | 작업 상태 |
| `asset_id` | UUID | FK nullable | 결과 파일 |
| `error_code` | VARCHAR(80) | nullable | 실패 코드 |
| `error_message` | TEXT | nullable | 실패 메시지 |
| `created_at` | TIMESTAMPTZ | NOT NULL | 생성 시각 |
| `finished_at` | TIMESTAMPTZ | nullable | 종료 시각 |

## 삭제 정책

- MVP에서는 하드 삭제를 제공하지 않는다.
- 추후 삭제 기능 추가 시 프로젝트 삭제는 관련 파일 삭제 작업과 DB 삭제를 하나의 서비스 계층에서 처리한다.

## 상태 전이

```text
draft -> generating -> generated -> ready
ready -> editing -> ready
ready -> exporting -> ready
any -> failed
failed -> generating
failed -> editing
```

작업 실패 시 `projects.status = failed`로 저장하고 실패한 `generation_jobs` 또는 `export_jobs`에 상세 오류를 남긴다.
