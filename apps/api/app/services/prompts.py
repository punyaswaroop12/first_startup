from pathlib import Path

from app.core.config import settings


def load_prompt(relative_path: str) -> str:
    prompt_path = settings.repo_root / "apps" / "api" / "app" / "prompts" / relative_path
    return Path(prompt_path).read_text(encoding="utf-8")

