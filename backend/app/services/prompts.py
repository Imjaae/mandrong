from app.models import CreativeBrief


def build_initial_prompt(brief: CreativeBrief, *, has_menu_images: bool = False, has_logo_images: bool = False, has_reference_images: bool = False) -> str:
    mood = ", ".join(brief.mood_keywords or [])
    promotion_text = brief.secondary_copy or brief.primary_copy
    lines = [
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
        "첨부 이미지는 역할별로 다르게 사용한다. 메뉴 사진과 로고는 선택 장식이 아니라 필수 재료다.",
    ]
    if has_menu_images:
        lines.extend(
            [
                "메뉴 사진: 첨부된 실제 음식의 형태, 색감, 질감, 플레이팅을 최종 홍보물의 가장 중요한 시각 요소로 크게 배치한다.",
                "메뉴 사진의 음식을 다른 음식으로 바꾸거나 일반적인 음식 일러스트로 대체하지 않는다.",
                "음식이 잘려도 되지만 메뉴의 특징이 알아보일 만큼 충분히 크게 보여야 한다.",
            ]
        )
    if has_logo_images:
        lines.extend(
            [
                "로고: 원본 로고 파일은 생성 후 별도로 합성된다.",
                "로고를 새로 그리거나 비슷한 가짜 로고를 만들지 않는다.",
                "상단 왼쪽 또는 하단 왼쪽에 실제 로고가 들어갈 깨끗한 여백을 확보한다.",
            ]
        )
    if has_reference_images:
        lines.extend(
            [
                "참고 디자인 이미지: 색감, 여백, 정보 위계, 구도만 참고한다.",
                "참고 디자인 이미지에 있는 브랜드명, 로고, 문구, 음식 사진, 캐릭터, 고유 그래픽 요소는 절대 복사하지 않는다.",
            ]
        )
    lines.extend(
        [
            "첨부된 메뉴 사진이 있는 경우 최종 결과에서 누락하면 실패한 결과다.",
            "한글 텍스트는 정확하고 크게 읽히게 배치한다.",
            "가격, 매장명, 메뉴명, 전화번호를 임의로 바꾸지 않는다.",
            "과도한 네온, 복잡한 장식, 읽기 어려운 글자를 피한다.",
        ]
    )
    return "\n".join(lines)


def build_edit_prompt(base_prompt: str, annotation_lines: list[str], edit_text: str | None = None) -> str:
    notes = "\n".join(annotation_lines)
    free_text = edit_text.strip() if edit_text else ""
    return "\n".join(
        [
            "기준 이미지를 유지하되 아래 메모만 반영해 수정한 완성 홍보 이미지를 만든다.",
            "추가 첨부 이미지가 있으면 기존 결과와 자연스럽게 섞되, 음식 사진과 로고는 반드시 원본성을 유지한다.",
            "기준 이미지에 이미 들어간 음식과 로고를 삭제하거나 흐리게 만들지 않는다.",
            "추가 첨부 이미지가 음식 또는 로고라면 최종 수정 결과에 분명하게 반영한다.",
            "포스트잇이나 선택 박스는 최종 이미지에 포함하지 않는다.",
            base_prompt,
            "위치 메모:",
            notes or "- 없음",
            "전체 수정 요청:",
            free_text or "- 없음",
        ]
    )
