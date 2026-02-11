extends Control


func _on_return_button_button_up() -> void:
	get_tree().change_scene_to_file("res://start.tscn")


func _on_level_1_button_up() -> void:
	get_tree().change_scene_to_file("res://leves/level1/level_1.tscn")


func _on_level_2_button_up() -> void:
	pass # Replace with function body.


func _on_level_3_button_up() -> void:
	pass # Replace with function body.
