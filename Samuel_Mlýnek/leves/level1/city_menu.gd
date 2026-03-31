extends Control
var city_hex : Vector2i
var logic

func setup(hex, game_logic):
	city_hex = hex
	logic = game_logic

func _on_spawn_unit_button_pressed() -> void:
	logic.produce_unit(city_hex)
	logic.update_ui()
	queue_free()


func _on_cancle_button_pressed() -> void:
	queue_free()


func _on_swn_artillery_pressed() -> void:
	logic.produce_artillery(city_hex)
	logic.update_ui()
	queue_free()
