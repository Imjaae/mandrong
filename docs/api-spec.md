# API 명세

## 기본

- Base URL: `http://localhost:8000/api/v1`
- 요청/응답은 JSON을 기본으로 한다.
- 파일 업로드는 `multipart/form-data`를 사용한다.
- 인증은 MVP 범위에서 제외한다.
- 모든 OpenAI 호출은 API 서버 내부 서비스 계층에서만 수행한다.

## 공통 오류 응답

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "입력값을 확인해주세요.",
    "details": {
      "field": "primary_copy"
    }
  }
}
```

## 오류 코드

| 코드 | HTTP | 의미 |
| --- | --- | --- |
| `VALIDATION_ERROR` | 422 | 요청 검증 실패 |
| `PROJECT_NOT_FOUND` | 404 | 작업 없음 |
| `VERSION_NOT_FOUND` | 404 | 버전 없음 |
| `ASSET_NOT_FOUND` | 404 | 파일 없음 |
| `UPLOAD_TOO_LARGE` | 413 | 파일 크기 초과 |
| `UNSUPPORTED_FILE_TYPE` | 415 | 지원하지 않는 파일 형식 |
| `GENERATION_FAILED` | 502 | 이미지 생성 실패 |
| `OPENAI_POLICY_BLOCKED` | 400 | 생성 정책 거절 |
| `EXPORT_FAILED` | 500 | 내보내기 실패 |

## 프로젝트

### `POST /projects`

새 작업과 브리프 초안을 만든다.

요청:

```json
{
  "title": "점심 신메뉴 포스터",
  "brief": {
    "purpose": "poster",
    "width": 1080,
    "height": 1350,
    "primary_copy": "오늘 점심은 따뜻한 갈비탕",
    "secondary_copy": "진한 국물과 푸짐한 고기",
    "price_copy": "9,900원",
    "notice_copy": "평일 점심 한정",
    "store_name": "만드롱 식당",
    "menu_name": "갈비탕",
    "price": "9,900원",
    "store_location": "제주시",
    "contact": "064-000-0000",
    "mood_keywords": ["따뜻한", "깔끔한"],
    "mood_text": "동네 식당 느낌이지만 정갈하게"
  }
}
```

크기 제약:

- `width`, `height`는 각각 256 이상 4096 이하
- `width`, `height`는 각각 16의 배수
- 프론트엔드는 직접 입력값을 가까운 올림 16px 단위로 자동 조정한다.

응답 `201`:

```json
{
  "id": "uuid",
  "title": "점심 신메뉴 포스터",
  "status": "draft",
  "current_version_id": null,
  "created_at": "2026-08-02T00:00:00Z"
}
```

### `GET /projects`

최근 작업 목록을 조회한다.

쿼리:

- `limit`: 기본 20, 최대 50
- `cursor`: 선택

### `GET /projects/{project_id}`

작업 상세, 브리프, 자산, 현재 버전을 조회한다.

### `PATCH /projects/{project_id}/brief`

브리프를 수정한다. 생성이 시작된 뒤에도 새 생성 요청 전까지 수정 가능하다.

## 자산

### `POST /projects/{project_id}/assets`

메뉴 사진 또는 참고 이미지를 업로드한다.

요청:

- `type`: `menu_photo` 또는 `reference_image`
- `file`: JPG, PNG, WEBP

응답 `201`:

```json
{
  "id": "uuid",
  "type": "menu_photo",
  "original_filename": "menu.jpg",
  "mime_type": "image/jpeg",
  "size_bytes": 1200000,
  "width": 1600,
  "height": 1200,
  "url": "/api/v1/assets/uuid/file"
}
```

### `GET /assets/{asset_id}/file`

파일을 반환한다. 내부 `storage_path`는 응답하지 않는다.

## 이미지 생성

### `POST /projects/{project_id}/generations`

최초 이미지를 생성한다.

요청:

```json
{
  "menu_asset_ids": ["uuid"],
  "reference_asset_ids": ["uuid"]
}
```

응답 `202`:

```json
{
  "job_id": "uuid",
  "status": "queued"
}
```

### `GET /generation-jobs/{job_id}`

생성 작업 상태를 조회한다.

응답:

```json
{
  "id": "uuid",
  "project_id": "uuid",
  "type": "initial",
  "status": "succeeded",
  "version_id": "uuid",
  "error": null
}
```

## 주석 수정

### `POST /versions/{version_id}/annotations`

수정 메모를 저장한다.

요청:

```json
{
  "annotations": [
    {
      "note": "가격을 9,900원으로 더 크게 보여주세요",
      "x": 0.62,
      "y": 0.71,
      "width": 0.2,
      "height": 0.12,
      "color": "yellow"
    }
  ]
}
```

응답 `201`:

```json
{
  "annotation_ids": ["uuid"]
}
```

### `POST /versions/{version_id}/edits`

주석을 바탕으로 수정 이미지를 생성한다.

요청:

```json
{
  "annotation_ids": ["uuid"]
}
```

응답 `202`:

```json
{
  "job_id": "uuid",
  "status": "queued"
}
```

## 버전

### `GET /projects/{project_id}/versions`

작업의 모든 버전을 최신순으로 조회한다.

### `GET /versions/{version_id}`

버전 상세를 조회한다.

### `POST /versions/{version_id}/apply`

해당 버전을 현재 적용 버전으로 지정한다.

응답:

```json
{
  "project_id": "uuid",
  "current_version_id": "uuid"
}
```

## 비율 재구성

### `POST /versions/{version_id}/reframes`

현재 이미지를 다른 비율로 재구성한다.

요청:

```json
{
  "target": {
    "purpose": "sns_story",
    "width": 1080,
    "height": 1920
  },
  "keep": {
    "copy": true,
    "menu_photo": true,
    "price": true,
    "mood": true
  }
}
```

응답 `202`:

```json
{
  "job_id": "uuid",
  "status": "queued"
}
```

## 내보내기

### `POST /versions/{version_id}/exports`

PNG, JPEG, PDF 파일을 만든다.

요청:

```json
{
  "format": "jpeg",
  "quality": 90
}
```

응답 `202`:

```json
{
  "export_job_id": "uuid",
  "status": "queued"
}
```

### `GET /export-jobs/{export_job_id}`

내보내기 작업 상태를 조회한다.

### `GET /exports/{asset_id}/download`

내보내기 파일을 다운로드한다.
