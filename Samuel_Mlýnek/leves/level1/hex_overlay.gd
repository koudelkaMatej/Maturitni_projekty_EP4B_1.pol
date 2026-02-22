extends Node2D
#hex_overlay script

const HEX_SIZE := 49
@onready var logic := get_parent().get_node("GameLogic")
var hex_offset_x = 3.0/4.0 * ((3.0/2.0) * HEX_SIZE)
var hex_offset_y =  sqrt(3) * HEX_SIZE
var start_pos = Vector2(HEX_SIZE, ((sqrt(3)* HEX_SIZE) / 2) + 1)
var selected_hex: Vector2i = Vector2i(-999, -999)
var hovered_hex : Vector2i = Vector2i(-999, -999)
var hex_centers := {} # Vector2i -> Vector
var reachable_hexes: Array[Vector2i] = []
const HEX_DIRECTIONS = [
	Vector2i(1, 0),
	Vector2i(1, -1),
	Vector2i(0, -1),
	Vector2i(-1, 0),
	Vector2i(-1, 1),
	Vector2i(0, 1),
]

# --- positioning equations ---#

func get_col_width() -> float:
	return hex_offset_x + hex_offset_x / 3

func get_row_height() -> float:
	return hex_offset_y

func hex_to_pixel(h: Vector2i) -> Vector2:
	var x = start_pos.x + hex_offset_x * h.x + hex_offset_x/3 * h.x
	var y = start_pos.y + hex_offset_y * h.y
	
	if h.x % 2 == 1:
		y += hex_offset_y/2
	
	return Vector2(x, y)

func pixel_to_hex(pos: Vector2) -> Vector2i:
	var px = pos.x - start_pos.x
	var py = pos.y - start_pos.y
	var col = int(round(px / get_col_width()))
	
	if col % 2 == 1:
		py -= hex_offset_y / 2
		
	var row = int(round(py / get_row_height()))
	
	return Vector2i(col, row)

func axial_round(frac: Vector2) -> Vector2i:

	var x = frac.x
	var z = frac.y
	var y = -x - z
	
	var rx = round(x)
	var ry = round(y)
	var rz = round(z)
	
	var x_diff = abs(rx - x)
	var y_diff = abs(ry - y)
	var z_diff = abs(rz - z)
	
	if z_diff > y_diff and x_diff > z_diff:
		rx = -ry - rz
	elif y_diff > z_diff:
		ry = -rx - rz
	else:
		rz = -rx - ry
	
	return Vector2(rx, rz)

func hex_points(center: Vector2) -> PackedVector2Array:
	var pts := PackedVector2Array()
	for i in range(6):
		var angle = deg_to_rad(60 * i)
		var point_x = center.x + HEX_SIZE * cos(angle)
		var point_y = center.y + HEX_SIZE * sin(angle)
		
		pts.append(Vector2(point_x, point_y))
		
	pts.append(pts[0])
	return pts

# --- Unit shit --- #

func get_neighbors(hex: Vector2i) -> Array:
	var result := []
	for dir in HEX_DIRECTIONS:
		var n = hex + dir
		if logic.grid.has(n) and logic.grid[n]["walkable"]:
			result.append(n)
	return result

func compute_reachable(unit):
	reachable_hexes.clear()
	reachable_hexes.append(unit.hex)

	var frontier = [unit.hex]

	for i in range(unit.move_points):
		var new_frontier = []
		for hex in frontier:
			for n in get_neighbors(hex):
				if not reachable_hexes.has(n):
					reachable_hexes.append(n)
					new_frontier.append(n)
		frontier = new_frontier

# --- functional thingies --- #

func _ready() -> void:
	for h in logic.grid.keys():
		hex_centers[h] = hex_to_pixel(h)

func _input(event):
	if event is InputEventMouseButton and event.pressed:
		var mouse_pos = get_global_mouse_position()
		var hex = pixel_to_hex(mouse_pos)
		if logic.grid.has(hex):
			if hex == selected_hex:
				selected_hex = Vector2i(-999, -999)
			else:
				selected_hex = hex
				
			queue_redraw()
			
	if event is InputEventMouseMotion:
		var mouse_pos = get_global_mouse_position()
		var hex = pixel_to_hex(mouse_pos)
		
		if logic.grid.has(hex):
			if hex != hovered_hex:
				hovered_hex = hex
				queue_redraw()
		else:
			if hovered_hex != Vector2i(-999, -999):
				hovered_hex = Vector2i(-999, -999)
				queue_redraw()

func _draw():
	for h in logic.grid.keys():
		var center = hex_to_pixel(h)
		
		var color = Color.WEB_GREEN
		var railing_color = Color.BLACK
		var railing_magnitude = 1
		
		if h == selected_hex:
			color = Color.GOLD
		elif h == hovered_hex:
			railing_color = Color.BLUE
			railing_magnitude = 2
		if reachable_hexes.has(h):
			color = Color.CORNFLOWER_BLUE
			
		draw_polygon(hex_points(center),PackedColorArray([color]))
		draw_polyline(hex_points(center), railing_color, railing_magnitude)
		
	for hex in reachable_hexes:
		var p = hex_to_pixel(hex)
		draw_colored_polygon(
			hex_points(p),
			Color(0.3, 0.6, 1.0, 0.4)
		)
