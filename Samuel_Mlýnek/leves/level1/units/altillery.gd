class_name Artillery
extends Node2D

@onready var hp_bar = $ProgressBar
@onready var sprite = $Sprite2D
var hex_position : Vector2i
var pixel_position : Vector2
var max_mov: int = 1       # slow
var move_points : int = 1
var hp: int = 15           # tanky
var dmg: int = 6           # hits hard
var unit_owner: String = "null"
var has_moved = false
var has_attacked = false
var attack_range: int = 2
var ignores_terrain: bool =true

var texture_player = preload("res://assests/cannon_player.png")
var texture_enemy  = preload("res://assests/cannon_enemy.png")

func initialize(hex: Vector2i, pixel: Vector2):
	hex_position = hex
	pixel_position = pixel
	position = pixel

	hp_bar.max_value = 15
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
