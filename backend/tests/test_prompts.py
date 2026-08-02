from app.models import CreativeBrief
from app.services.prompts import build_initial_prompt


def test_build_initial_prompt_preserves_required_copy() -> None:
    brief = CreativeBrief(
        purpose="poster",
        width=1080,
        height=1350,
        primary_copy="오늘 점심은 갈비탕",
        secondary_copy="오늘 점심은 갈비탕\n평일 점심 한정 9,900원",
        mood_keywords=["따뜻한", "깔끔한"],
    )

    prompt = build_initial_prompt(brief, menu_image_count=1, has_logo_images=True, reference_image_count=1)

    assert "오늘 점심은 갈비탕" in prompt
    assert "9,900원" in prompt
    assert "메뉴 사진" in prompt
    assert "로고를 새로 그리거나" in prompt
    assert "절대 복사하지 않는다" in prompt
    assert "실제 음식은 메뉴 사진만 사용" in prompt
    assert "누락하면 실패" in prompt
    assert "gpt-image-2" not in prompt
