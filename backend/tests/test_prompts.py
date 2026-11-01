import pytest

from backend.app.prompts.loader import load_prompt


def test_prompt_loader_reads_template() -> None:
    prompt = load_prompt("plan_generation.v1.md")
    assert "Aura Vision & Planning Engine" in prompt
    assert "Bill of Quantities" in prompt


def test_prompt_loader_copilot_template() -> None:
    prompt = load_prompt("copilot_system.v1.md")
    assert "AuraPulse Co-Pilot" in prompt
    assert "scale_budget" in prompt


def test_prompt_loader_missing_raises() -> None:
    with pytest.raises(FileNotFoundError):
        load_prompt("non_existent_template_xyz.md")
