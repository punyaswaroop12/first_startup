from app.services.reports import render_markdown


def test_render_markdown_contains_all_sections() -> None:
    markdown = render_markdown(
        title="Weekly Ops Summary",
        top_themes=["Theme 1"],
        risks=["Risk 1"],
        action_items=["Action 1"],
        notable_updates=["Update 1"],
    )

    assert "# Weekly Ops Summary" in markdown
    assert "## Top themes" in markdown
    assert "## Risks/issues" in markdown
    assert "## Action items" in markdown
    assert "## Notable updates" in markdown
