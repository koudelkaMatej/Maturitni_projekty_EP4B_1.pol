def world_to_screen(wx, wy, camera_y, screen_h):
    sx = int(wx)
    sy = int(wy - camera_y + screen_h//2)
    return sx, sy
