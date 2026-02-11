extends Control

func _ready():
	$VBoxContainer/Start_button.pressed.connect(_on_start_pressed)
	$VBoxContainer/Options_button.pressed.connect(_on_options_pressed)
	$VBoxContainer/Quit_button.pressed.connect(_on_quit_pressed)

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
