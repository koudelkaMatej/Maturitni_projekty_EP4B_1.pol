class_name Infantry
extends Node2D
#unit script
@onready var hp_bar = $ProgressBar
@onready var sprite = $Sprite2D

var hex_position : Vector2i
var pixel_position : Vector2
var max_mov: int = 3
var move_points : int = 3
var hp: int = 10
var dmg: int = 3
var unit_owner: String = "null"
var has_moved = false
var has_attacked = false
var attack_range: int = 1
var ignores_terrain: bool = false

var texture_player = preload("res://assests/player_infantrie.png")
var texture_enemy  = preload("res://assests/enemy_infantrie.png")

func initialize(hex: Vector2i, pixel: Vector2):
	hex_position = hex
	pixel_position = pixel
	position = pixel
	
	hp_bar.max_value = 10
	hp_bar.value = hp
	if unit_owner == "player":
		sprite.texture = texture_player
	else:
		sprite.texture = texture_enemy

func move_to_hex(hex: Vector2i, pixel: Vector2):
	hex_position = hex
	position = pixel
	
func update_hp():
	hp_bar.value = hp
	
	if hp <= 0:
		queue_free()
