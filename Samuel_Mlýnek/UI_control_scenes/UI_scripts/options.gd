extends Control

const CONFIG_PATH := "user://settings/settings.cfg"

func _ready() -> void:
	load_settings()

func _on_button_pressed() -> void:
	queue_free()


func _on_master_volume_value_changed(value: float) -> void:
	AudioServer.set_bus_volume_db(
		AudioServer.get_bus_index("Master"),
		value
	)
	

func _on_music_value_changed(value: float) -> void:
	AudioServer.set_bus_volume_db(
		AudioServer.get_bus_index("Music"),
		value
	)


func _on_sfx_value_changed(value: float) -> void:
	AudioServer.set_bus_volume_db(
		AudioServer.get_bus_index("SFX"), 
		value
		)


func _on_confirm_pressed() -> void:
	save_settings()
	queue_free()
	
	
func save_settings():
	DirAccess.make_dir_recursive_absolute("user://settings")
	
	var cfg := ConfigFile.new()
		
	cfg.set_value("audio", "master", $Panel/master_volume.value)
	cfg.set_value("audio", "music", $Panel/music.value)
	cfg.set_value("audio", "sfx", $Panel/SFX.value)
	cfg.set_value("audio", "music_mute", $Panel/mute_music.button_pressed)
	
	var err = cfg.save(CONFIG_PATH)
	print("Save result: ", err)
	
func load_settings():
	var cfg := ConfigFile.new()
	if cfg.load(CONFIG_PATH) != OK:
		return
	$Panel/master_volume.value = cfg.get_value("audio", "master", 0)
	$Panel/music.value = cfg.get_value("audio", "music", 0)
	$Panel/SFX.value = cfg.get_value("audio", "sfx", 0)
	$Panel/mute_music.button_pressed = cfg.get_value("audio", "music_mute", false)
	
	_on_master_volume_value_changed($Panel/master_volume.value)
	_on_music_value_changed($Panel/music.value)
	_on_sfx_value_changed($Panel/SFX.value)
	_on_mute_music_toggled($Panel/mute_music.button_pressed)

func _on_mute_music_toggled(toggled_on: bool) -> void:
	var music_bus := AudioServer.get_bus_index("Music")
	if toggled_on:
		AudioServer.set_bus_volume_db(music_bus, -80)
	else:
		_on_music_value_changed($Panel/music.value)
