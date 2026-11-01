import re
from datetime import date
from pathlib import Path

from backend.app.fixtures.sample_plans import (
    create_preset_cyberpunk_birthday,
    create_preset_diwali_mela,
    create_preset_meadow_wedding,
)


def test_no_hardcoded_dates_in_production_code():
    """Scans backend/app and frontend/src for YYYY-MM-DD date literals unless commented # allow-date."""
    root = Path(__file__).resolve().parent.parent.parent
    date_regex = re.compile(r"20\d{2}-[01]\d-[0-3]\d")

    target_dirs = [root / "backend" / "app", root / "frontend" / "src"]
    matches = []

    for target_dir in target_dirs:
        for file_path in target_dir.rglob("*"):
            if "__tests__" in file_path.parts:
                continue
            if file_path.suffix in (".py", ".ts", ".tsx"):
                content = file_path.read_text(encoding="utf-8")
                for line_no, line in enumerate(content.splitlines(), start=1):
                    if "# allow-date" in line or "// allow-date" in line:
                        continue
                    if date_regex.search(line):
                        matches.append(f"{file_path.relative_to(root)}:{line_no}: {line.strip()}")

    assert not matches, "Found hardcoded dates in production code:\n" + "\n".join(matches)


def test_preset_without_date_gets_future_event_date_and_milestones():
    """Preset plan generated with default arguments must have a future event_date and no past milestones."""
    today = date.today()
    for preset_builder in [create_preset_meadow_wedding, create_preset_cyberpunk_birthday, create_preset_diwali_mela]:
        plan = preset_builder()
        assert plan.event_date is not None
        ev_dt = date.fromisoformat(plan.event_date)
        assert ev_dt > today, f"Event date {plan.event_date} should be in the future"

        assert plan.planning_milestones
        for ms in plan.planning_milestones:
            ms_dt = date.fromisoformat(ms.due_date)
            assert ms_dt >= today, f"Milestone {ms.id} has past due date {ms.due_date}"
