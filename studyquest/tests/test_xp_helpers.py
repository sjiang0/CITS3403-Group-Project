"""Unit tests for studyquest/app/xp_helpers.py."""
from app.xp_helpers import (
    AVATAR_POOL,
    LEVEL_TITLES,
    avatar_emoji,
    level_title,
    xp_into_level,
    xp_to_level,
    xp_to_next_level,
)


def test_xp_to_level_at_zero_returns_one():
    assert xp_to_level(0) == 1


def test_xp_to_level_just_below_threshold_stays_one():
    assert xp_to_level(99) == 1


def test_xp_to_level_at_thresholds_increments():
    assert xp_to_level(100) == 2
    assert xp_to_level(500) == 6
    assert xp_to_level(1000) == 11


def test_xp_to_level_handles_none_xp():
    assert xp_to_level(None) == 1


def test_xp_into_and_to_next_always_sum_to_100():
    for xp in (0, 37, 99, 100, 250, 999, 5000):
        assert xp_into_level(xp) + xp_to_next_level(xp) == 100


def test_level_title_known_levels():
    assert level_title(1) == "Tiny Sprout"
    assert level_title(4) == "Blooming Scholar"
    assert level_title(10) == "Grand Herbalist"


def test_level_title_above_max_clamps_to_grand_herbalist():
    assert level_title(11) == "Grand Herbalist"
    assert level_title(99) == "Grand Herbalist"


def test_avatar_emoji_is_deterministic_per_username():
    assert avatar_emoji("alice") == avatar_emoji("alice")
    assert avatar_emoji("bob") == avatar_emoji("bob")


def test_avatar_emoji_returns_value_from_pool():
    assert avatar_emoji("alice") in AVATAR_POOL
    assert avatar_emoji("z") in AVATAR_POOL


def test_avatar_emoji_handles_empty_or_none_username():
    assert avatar_emoji("") == "🌸"
    assert avatar_emoji(None) == "🌸"


def test_level_titles_dict_has_ten_entries():
    assert set(LEVEL_TITLES.keys()) == set(range(1, 11))
