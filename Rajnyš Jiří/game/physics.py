from .settings import *

def move_and_collide(player, obstacles):
    # POHYB po ose X
    player.world_x += player.velocity_x
    rect = player.rect()

    for o in obstacles:
        if rect.colliderect(o):
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

def resolve_collisions(player, obstacles):
    rect = player.rect()
    for o in obstacles:
        if rect.colliderect(o):
            if player.velocity_x > 0:
                player.world_x = o.left - player.w
            elif player.velocity_x < 0:
                player.world_x = o.right

            player.velocity_x *= 0.25
            rect = player.rect()
    rect = player.rect()
    for o in obstacles:
        if rect.colliderect(o):
            if player.velocity_y > 0:
                player.world_y = o.top - player.h
            elif player.velocity_y < 0:
                player.world_y = o.bottom

            player.velocity_y *= 0.25
            rect = player.rect()
