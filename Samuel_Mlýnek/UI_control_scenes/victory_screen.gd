extends Control

func _on_next_battle_button_pressed() -> void:
	global.current_level += 1
	global.load_save = false
	get_tree().change_scene_to_file("res://leves/level1/level_1.tscn")

func _on_main_menu_button_pressed() -> void:
	get_tree().change_scene_to_file("res://start.tscn")
