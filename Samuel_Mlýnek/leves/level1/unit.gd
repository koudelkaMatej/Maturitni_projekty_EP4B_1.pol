extends Node2D
@onready var hex_overlay := get_parent().get_node("HexOverlay")
var is_city := false


#example unit
var hex : Vector2i
var move_points = 4
var hp := 10
var selected := false

func _draw():
	if selected:
		draw_circle(Vector2.ZERO, 16, Color.RED)
	draw_circle(Vector2.ZERO, 12, Color.GOLD)
	
func move_to_hex(h: Vector2i, world_pos: Vector2):
	hex = h
	position = world_pos

func set_selected(value: bool):
	selected = value
	queue_redraw()
