extends Control

func _ready():
	$VBoxContainer/Start_button.pressed.connect(_on_start_pressed)
	$VBoxContainer/Options_button.pressed.connect(_on_options_pressed)
	$VBoxContainer/Quit_button.pressed.connect(_on_quit_pressed)
	$VBoxContainer/Load_button.pressed.connect(_on_load_pressed)
	
	if global.is_guest:
		$VBoxContainer/Load_button.visible = not global.is_guest
		$Menu_texture.size = Vector2(1278, 924.14)
		$Menu_texture.position = Vector2(375, 314)

func _on_start_pressed():
	print("You have ventured into battle Commander") #later add game scene
	get_tree().change_scene_to_file("res://UI_control_scenes/campain_menu.tscn")

func _on_options_pressed():
	if $OptionLayer.get_child_count() == 0:
		print("adjusting battle condicions Commander")
		var options = load("res://UI_control_scenes/Options.tscn").instantiate()
		$OptionLayer.add_child(options)

func _on_quit_pressed():
	get_tree().quit()

func _on_load_pressed():
	print("Loading previous battle Commander")
	global.current_level = 1
	global.load_save = true   # ← tell the game to load from server
	get_tree().change_scene_to_file("res://leves/level1/level_1.tscn")
