from app.schemas.project import CreativeBriefIn


def test_creative_brief_rounds_non_16px_size() -> None:
    brief = CreativeBriefIn(
        purpose="poster",
        width=600,
        height=1800,
        primary_copy="오늘 점심은 갈비탕",
        mood_keywords=["따뜻한"],
    )

    assert brief.width == 608
    assert brief.height == 1808


def test_creative_brief_accepts_16px_size() -> None:
    brief = CreativeBriefIn(
        purpose="poster",
        width=608,
        height=1808,
        primary_copy="오늘 점심은 갈비탕",
        mood_keywords=["따뜻한"],
    )

    assert brief.width == 608
    assert brief.height == 1808
