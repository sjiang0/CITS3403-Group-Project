LEVEL_TITLES = {
    1: 'Tiny Sprout',         2: 'Little Herb',
    3: 'Wildflower',          4: 'Blooming Scholar',
    5: 'Keeper of the Grove', 6: 'Petal Tender',
    7: 'Moonlit Scholar',     8: 'Elder Bloom',
    9: 'Ancient Herbalist',   10: 'Grand Herbalist',
}

AVATAR_POOL = ['🌸', '🌷', '🌻', '🍃', '🌾', '🌿', '🌹', '🌼', '✨', '🦋', '🌳', '🍀']


def xp_to_level(xp):
    return ((xp or 0) // 100) + 1


def xp_into_level(xp):
    return (xp or 0) % 100


def xp_to_next_level(xp):
    return 100 - ((xp or 0) % 100)


def level_title(level):
    if level >= 10:
        return LEVEL_TITLES[10]
    return LEVEL_TITLES.get(level, 'Scholar')


def avatar_emoji(username):
    if not username:
        return '🌸'
    seed = sum(ord(c) for c in username)
    return AVATAR_POOL[seed % len(AVATAR_POOL)]
