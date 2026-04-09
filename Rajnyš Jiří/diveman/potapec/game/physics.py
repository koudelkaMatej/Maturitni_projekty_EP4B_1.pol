from .settings import *
import pygame

def move_and_collide(player, obstacles, game=None):
    # POHYB po ose X
    player.world_x += player.velocity_x
    rect = player.rect()

    for o in obstacles:
        if game and o is game.starting_cliff:
            if game.cliff_mask:
                # mask kolize pro útes
                player_frame = player.get_current_frame()
                if player_frame:
                    player_mask = pygame.mask.from_surface(player_frame)
                    offset = (int(o.x - player.world_x), int(o.y - player.world_y))
                    if player_mask.overlap(game.cliff_mask, offset):
                        if player.velocity_x > 0:
                            player.world_x = o.left - player.w
                            player.velocity_x = 0
                        elif player.velocity_x < 0:
                            player.world_x = o.right
                            player.velocity_x = 0
                        player.velocity_x *= 0.25
                        rect = player.rect()
            # pokud není maska, žádná X kolize pro počáteční útes
        else:
            # normální rect kolize
            if rect.colliderect(o):
                if o.x == -EDGE_WALL_PAD or o.x == SCREEN_W:
                    if player.velocity_x > 0:
                        player.world_x = o.left
                    elif player.velocity_x < 0:
                        player.world_x = o.right
                else:
                    if player.velocity_x > 0:
                        player.world_x = o.left - player.w
                        # zastavit horizontální klouzání při nárazu do zdi
                        player.velocity_x = 0
                    elif player.velocity_x < 0:
                        player.world_x = o.right
                        # zastavit horizontální klouzání při nárazu do zdi
                        player.velocity_x = 0

                player.velocity_x *= 0.25
                rect = player.rect()

    # POHYB po ose Y 
    player.world_y += player.velocity_y
    rect = player.rect()

    for o in obstacles:
        if game and o is game.starting_cliff and game.cliff_mask:
            # mask kolize pro útes
            player_frame = player.get_current_frame()
            if player_frame:
                player_mask = pygame.mask.from_surface(player_frame)
                offset = (int(o.x - player.world_x), int(o.y - player.world_y))
                if player_mask.overlap(game.cliff_mask, offset):
                    if player.velocity_y > 0:
                        player.world_y = o.top - player.h
                    elif player.velocity_y < 0:
                        player.world_y = o.bottom
                    player.velocity_y *= 0.4
                    rect = player.rect()
        else:
            # normální rect kolize
            if rect.colliderect(o):
                if player.velocity_y > 0:
                    player.world_y = o.top - player.h
                elif player.velocity_y < 0:
                    player.world_y = o.bottom

                player.velocity_y *= 0.4
                rect = player.rect()
    player.velocity_x *= 0.85
    if abs(player.velocity_x) < 0.03:
        player.velocity_x = 0.2
    try:
        from .settings import SEA_LEVEL_Y
        if player.world_y >= SEA_LEVEL_Y:
            if player.velocity_y > 0:
                player.velocity_y *= 0.80
            else:
                player.velocity_y *= 0.90
        else:
            player.velocity_y *= 0.995
    except Exception:
        player.velocity_y *= 0.995
    if player.velocity_y > 30:
        player.velocity_y = 30

