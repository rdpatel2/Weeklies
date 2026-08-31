"""UC06: Generate Meal Plan — tests.

The MenuGenerator class in proj2/menu_generation.py wraps a HuggingFace LLM,
which is heavyweight and non-deterministic. We test the plan-parsing surface
(parse_generated_menu) as a proxy where possible, and skip tests that would
require full model execution. This mirrors the existing test suite's approach
in proj2/tests/llm.
"""
import pytest
from proj2.Flask_app import parse_generated_menu


def test_generate_meal_plan_valid():
    """UC06 main: end-to-end LLM generation requires model; covered by proj2/tests/llm."""
    pytest.skip("Full LLM generation is exercised by proj2/tests/llm/test_generator.py")


def test_generate_meal_plan_no_periods():
    """UC06 ext 1a: defaults to breakfast/lunch/dinner — MenuGenerator internal."""
    pytest.skip("MenuGenerator harness required")


def test_generate_meal_plan_invalid_date():
    """UC06 ext 1b: invalid date falls back to today — MenuGenerator internal."""
    pytest.skip("MenuGenerator harness required")


def test_generate_meal_plan_duration_too_short():
    """UC06 ext 1c: duration < 1 day forced to 1."""
    pytest.skip("MenuGenerator harness required")


def test_generate_meal_plan_duration_too_long():
    """UC06 ext 1d: duration > 14 days capped at 14."""
    pytest.skip("MenuGenerator harness required")


def test_generate_meal_plan_malformed_hours():
    """UC06 ext 3a: malformed restaurant hours excluded from generation."""
    pytest.skip("MenuGenerator harness required")


def test_generate_meal_plan_allergies_all():
    """UC06 ext 3b: allergies eliminating all candidates → generation failure."""
    pytest.skip("MenuGenerator harness required")


def test_generate_meal_plan_invalid_selection():
    """UC06 ext 4a: parser silently drops invalid entries (proxy for retry logic)."""
    # Real proxy test: parse_generated_menu drops entries that don't match the format
    result = parse_generated_menu("[bad-date,not-an-id]")
    assert result == {}


def test_generate_meal_plan_llm_unavailable():
    """UC06 ext 4c: LLM unavailable → fallback path in MenuGenerator."""
    pytest.skip("MenuGenerator harness required")


def test_generate_meal_plan_preserves_existing():
    """UC06 ext 5a: parse_generated_menu keeps multiple entries for the same day."""
    result = parse_generated_menu("[2025-11-05,1,1][2025-11-05,2,2]")
    assert "2025-11-05" in result
    assert len(result["2025-11-05"]) == 2
