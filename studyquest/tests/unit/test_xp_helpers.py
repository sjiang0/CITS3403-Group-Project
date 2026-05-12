import unittest

from app.xp_helpers import (
    AVATAR_POOL,
    LEVEL_TITLES,
    avatar_emoji,
    level_title,
    xp_into_level,
    xp_to_level,
    xp_to_next_level,
)


class XpHelpersTests(unittest.TestCase):
    """Pure-function tests for the xp_helpers module."""

    def test_xp_to_level_at_zero_returns_one(self):
        self.assertEqual(xp_to_level(0), 1)

    def test_xp_to_level_below_first_threshold_stays_one(self):
        self.assertEqual(xp_to_level(99), 1)

    def test_xp_to_level_at_thresholds_increments(self):
        self.assertEqual(xp_to_level(100), 2)
        self.assertEqual(xp_to_level(500), 6)
        self.assertEqual(xp_to_level(1000), 11)

    def test_xp_to_level_handles_none(self):
        self.assertEqual(xp_to_level(None), 1)

    def test_xp_into_and_to_next_always_sum_to_100(self):
        for xp in (0, 37, 99, 100, 250, 999, 5000):
            self.assertEqual(xp_into_level(xp) + xp_to_next_level(xp), 100)

    def test_level_title_known_levels(self):
        self.assertEqual(level_title(1), "Tiny Sprout")
        self.assertEqual(level_title(4), "Blooming Scholar")
        self.assertEqual(level_title(10), "Grand Herbalist")

    def test_level_title_above_max_clamps(self):
        self.assertEqual(level_title(11), "Grand Herbalist")
        self.assertEqual(level_title(99), "Grand Herbalist")

    def test_avatar_emoji_is_deterministic(self):
        self.assertEqual(avatar_emoji("alice"), avatar_emoji("alice"))
        self.assertEqual(avatar_emoji("bob"), avatar_emoji("bob"))

    def test_avatar_emoji_returns_value_from_pool(self):
        self.assertIn(avatar_emoji("alice"), AVATAR_POOL)
        self.assertIn(avatar_emoji("z"), AVATAR_POOL)

    def test_avatar_emoji_handles_empty_or_none(self):
        self.assertEqual(avatar_emoji(""), "🌸")
        self.assertEqual(avatar_emoji(None), "🌸")

    def test_level_titles_has_ten_entries(self):
        self.assertEqual(set(LEVEL_TITLES.keys()), set(range(1, 11)))


if __name__ == "__main__":
    unittest.main()
