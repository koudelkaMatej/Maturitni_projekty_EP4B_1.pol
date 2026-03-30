import pygame

def resolve_aabb(player, rect):
    px, py = player.world_x, player.world_y
    pw, ph = player.w, player.h

    ox, oy, ow, oh = rect

    dx = (px + pw/2) - (ox + ow/2)
    dy = (py + ph/2) - (oy + oh/2)

    overlap_x = (pw/2 + ow/2) - abs(dx)
    overlap_y = (ph/2 + oh/2) - abs(dy)

    if overlap_x <= 0 or overlap_y <= 0:
        return

    if overlap_x < overlap_y:
        if dx > 0:
            player.world_x += overlap_x
        else:
            player.world_x -= overlap_x
        player.velocity_x = 0
    else:
        if dy > 0:
            player.world_y += overlap_y
        else:
            player.world_y -= overlap_y
        player.velocity_y = 0
