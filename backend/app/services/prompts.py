from app.models import CreativeBrief


def build_initial_prompt(brief: CreativeBrief) -> str:
    mood = ", ".join(brief.mood_keywords or [])
    promotion_text = brief.secondary_copy or brief.primary_copy
    return "\n".join(
        [
            "요식업 홍보물 전문 디자이너처럼 바로 게시 가능한 완성 이미지를 만든다.",
            f"용도: {brief.purpose}",
            f"크기: {brief.width}x{brief.height}",
            f"사용자가 입력한 전체 홍보 문구: {promotion_text}",
            f"가격/혜택 참고: {brief.price_copy or brief.price or '전체 홍보 문구에 포함된 경우 그대로 사용'}",
            f"매장명: {brief.store_name or '없음'}",
            f"메뉴명: {brief.menu_name or '없음'}",
            f"지역/주소: {brief.store_location or '없음'}",
            f"연락처/주문 방법: {brief.contact or '없음'}",
            f"분위기 키워드: {mood or '없음'}",
            f"추가 분위기: {brief.mood_text or '없음'}",
            "첨부된 메뉴 사진이 있으면 음식의 형태, 색감, 질감, 플레이팅을 최대한 살려 핵심 시각 요소로 사용한다.",
            "첨부된 로고 이미지가 있으면 로고의 글자와 형태를 새로 그리거나 바꾸지 말고 선명하게 반영한다.",
            "첨부 이미지를 단순 참고로만 흘려보내지 말고 최종 홍보물의 주요 재료로 사용한다.",
            "한글 텍스트는 정확하고 크게 읽히게 배치한다.",
            "가격, 매장명, 메뉴명, 전화번호를 임의로 바꾸지 않는다.",
            "과도한 네온, 복잡한 장식, 읽기 어려운 글자를 피한다.",
        ]
    )


def build_edit_prompt(base_prompt: str, annotation_lines: list[str], edit_text: str | None = None) -> str:
    notes = "\n".join(annotation_lines)
    free_text = edit_text.strip() if edit_text else ""
    return "\n".join(
        [
            "기준 이미지를 유지하되 아래 메모만 반영해 수정한 완성 홍보 이미지를 만든다.",
            "추가 첨부 이미지가 있으면 기존 결과와 자연스럽게 섞되, 음식 사진과 로고는 최대한 원본성을 유지한다.",
            "포스트잇이나 선택 박스는 최종 이미지에 포함하지 않는다.",
            base_prompt,
            "위치 메모:",
            notes or "- 없음",
            "전체 수정 요청:",
            free_text or "- 없음",
        ]
    )
