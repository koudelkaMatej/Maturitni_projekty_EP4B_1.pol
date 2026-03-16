extends Node2D
@onready var hex_overlay := get_parent().get_parent().get_node("HexOverlay")


#example unit
var hex_pos : Vector2i
var move_points: int = 3
var max_mov: int = 3

var hp: int = 10
var attack: int = 3

var has_moved: bool = false

func initialize(start_hex: Vector2i, hex_to_pixel: Callable):
	set_hex_position(start_hex, hex_to_pixel)

func set_hex_position(new_hex: Vector2i, hex_to_pixel: Callable):
	hex_pos = new_hex
	position = hex_to_pixel.call(new_hex)
	
func reset_turn():
	move_points = max_mov
	has_moved = false
