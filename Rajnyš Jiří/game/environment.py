from .settings import SEA_LEVEL_Y, PIXELS_PER_METER
import math
def lerp(a, b, t):
    return a + (b - a) * t

def color_lerp(c1, c2, t):
    return (
        int(lerp(c1[0], c2[0], t)),
        int(lerp(c1[1], c2[1], t)),
        int(lerp(c1[2], c2[2], t)),
    )
def get_background_colors(world_y):
    # barvy oblohy a vody
    sky_day = (135, 206, 250)
    surface_water = (80, 180, 220)  # světlejší modrá
    mid_water     = (30, 90, 140)   # střední modrá
    deep_water    = (6, 18, 40)     # temná hloubka
    if world_y < SEA_LEVEL_Y:
        return sky_day, surface_water, 0.0
    depth_px = world_y - SEA_LEVEL_Y
    depth_m = depth_px / PIXELS_PER_METER
    t = min(1.0, depth_m / 500.0)

    if t < 0.5:
            # povrch → střed
        sub_t = t / 0.5
        water_color = color_lerp(surface_water, mid_water, sub_t)
    else:
            # střed → hluboko
        sub_t = (t - 0.5) / 0.5
        water_color = color_lerp(mid_water, deep_water, sub_t)
    fog = min(1.0, depth_m / 800.0)
    return sky_day, water_color, fog
def stone_color(depth_m):
    if depth_m < 50:
        return (120, 110, 100)
    if depth_m < 150:
        return (90, 85, 80)
    if depth_m < 300:
        return (60, 55, 50)
    return (35, 32, 30)
    
