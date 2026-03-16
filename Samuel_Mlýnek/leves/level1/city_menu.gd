extends Control
var city_hex : Vector2i
var logic

func setup(hex, game_logic):
	city_hex = hex
	logic = game_logic

func _on_spawn_unit_button_pressed() -> void:
	logic.spawn_unit(city_hex)

	queue_free()


func _on_cancle_button_pressed() -> void:
	queue_free()
