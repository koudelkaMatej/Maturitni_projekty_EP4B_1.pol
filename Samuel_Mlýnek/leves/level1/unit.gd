extends Node2D
@onready var hex_overlay := get_parent().get_node("HexOverlay")
var is_city := false


#example unit
var hex : Vector2i
var move_points = 4
var hp := 10
var selected := false
