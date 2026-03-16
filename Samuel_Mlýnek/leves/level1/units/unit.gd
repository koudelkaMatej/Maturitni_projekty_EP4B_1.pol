extends Node2D
#unit script
@onready var hp_bar = $ProgressBar

var hex_position : Vector2i
var pixel_position : Vector2
var max_mov: int = 3
var hp: int = 10
var dmg: int = 3
var unit_owner: String = "null"
var has_moved = false
var has_attacked = false

func initialize(hex: Vector2i, pixel: Vector2):
	hex_position = hex
	pixel_position = pixel
	position = pixel

func move_to_hex(hex: Vector2i, pixel: Vector2):
	hex_position = hex
	position = pixel
	
func update_hp():
	hp_bar.value = hp
