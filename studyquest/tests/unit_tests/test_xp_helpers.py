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
        self.assertEqual(
            xp_to_level(0), 1,
            "A user with 0 XP should be at Level 1"
        )

    def test_xp_to_level_below_first_threshold_stays_one(self):
        self.assertEqual(
            xp_to_level(99), 1,
            "A user with 99 XP should still be at Level 1 (next threshold is 100)"
        )

    def test_xp_to_level_at_thresholds_increments(self):
        self.assertEqual(
            xp_to_level(100), 2,
            "100 XP should put the user at Level 2"
        )
        self.assertEqual(
            xp_to_level(500), 6,
            "500 XP should put the user at Level 6"
        )
        self.assertEqual(
            xp_to_level(1000), 11,
            "1000 XP should put the user at Level 11"
        )

    def test_xp_to_level_handles_none(self):
        self.assertEqual(
            xp_to_level(None), 1,
            "xp_to_level should treat None as 0 XP and return Level 1, not raise"
        )

    def test_xp_into_and_to_next_always_sum_to_100(self):
        for xp in (0, 37, 99, 100, 250, 999, 5000):
            self.assertEqual(
                xp_into_level(xp) + xp_to_next_level(xp), 100,
                f"xp_into_level + xp_to_next_level should equal 100 for any xp (failed at xp={xp})"
            )

    def test_level_title_known_levels(self):
        self.assertEqual(
            level_title(1), "Tiny Sprout",
            "Level 1 should be titled 'Tiny Sprout'"
        )
        self.assertEqual(
            level_title(4), "Blooming Scholar",
            "Level 4 should be titled 'Blooming Scholar'"
        )
        self.assertEqual(
            level_title(10), "Grand Herbalist",
            "Level 10 should be titled 'Grand Herbalist'"
        )

    def test_level_title_above_max_clamps(self):
        self.assertEqual(
            level_title(11), "Grand Herbalist",
            "Level 11 should clamp to the max title 'Grand Herbalist'"
        )
        self.assertEqual(
            level_title(99), "Grand Herbalist",
            "Level 99 should clamp to the max title 'Grand Herbalist'"
        )

    def test_avatar_emoji_is_deterministic(self):
        self.assertEqual(
            avatar_emoji("alice"), avatar_emoji("alice"),
            "avatar_emoji should return the same emoji every time for the same username"
        )
        self.assertEqual(
            avatar_emoji("bob"), avatar_emoji("bob"),
            "avatar_emoji should be deterministic for 'bob' across calls"
        )

    def test_avatar_emoji_returns_value_from_pool(self):
        self.assertIn(
            avatar_emoji("alice"), AVATAR_POOL,
            "avatar_emoji output for 'alice' should be a value from AVATAR_POOL"
        )
        self.assertIn(
            avatar_emoji("z"), AVATAR_POOL,
            "avatar_emoji output for 'z' should be a value from AVATAR_POOL"
        )

    def test_avatar_emoji_handles_empty_or_none(self):
        self.assertEqual(
            avatar_emoji(""), "🌸",
            "avatar_emoji should fall back to '🌸' for empty string"
        )
        self.assertEqual(
            avatar_emoji(None), "🌸",
            "avatar_emoji should fall back to '🌸' for None"
        )

    def test_level_titles_has_ten_entries(self):
        self.assertEqual(
            set(LEVEL_TITLES.keys()), set(range(1, 11)),
            "LEVEL_TITLES should have entries for levels 1 through 10"
        )


if __name__ == "__main__":
    unittest.main()
