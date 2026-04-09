extends Control

func _ready():
	if global.is_guest:
		apply_unlock(get_local_unlocked())
	else:
		fetch_unlocked_from_server()

func get_local_unlocked() -> int:
	if not FileAccess.file_exists("user://progress.json"):
		return 1
	var file = FileAccess.open("user://progress.json", FileAccess.READ)
	var data = JSON.parse_string(file.get_as_text())
	file.close()
	return data.get("highest_unlocked", 1)

func fetch_unlocked_from_server():
	var http = HTTPRequest.new()
	add_child(http)
	http.request_completed.connect(_on_stats_received)
	http.request("http://127.0.0.1:5000/api/stats/" + global.username, [], HTTPClient.METHOD_GET, "")

func _on_return_button_button_up() -> void:
	get_tree().change_scene_to_file("res://start.tscn")

func _on_stats_received(result, response_code, headers, body):
	var data = JSON.parse_string(body.get_string_from_utf8())
	if data and data["status"] == "ok":
		# count how many levels are completed
		var completed = 0
		for lvl in data["levels"]:
			if lvl["completed"] == 1:
				completed += 1
		# unlocked = completed levels + 1 (next one), capped at 3
		apply_unlock(min(completed + 1, 3))
	else:
		apply_unlock(1)  # fallback

func apply_unlock(unlocked: int):
	global.highest_unlocked = unlocked
	$level_1_button.disabled = false
	$level_2_button.disabled = unlocked < 2
	$level_3_button.disabled = unlocked < 3

func _on_level_1_button_up() -> void:
	global.current_level = 1
	global.load_save = false  # ← fresh start
	get_tree().change_scene_to_file("res://leves/level1/level_1.tscn")

func _on_level_2_button_up() -> void:
	global.current_level = 2
	global.load_save = false
	get_tree().change_scene_to_file("res://leves/level1/level_1.tscn")

func _on_level_3_button_up() -> void:
	global.current_level = 3
	global.load_save = false
	get_tree().change_scene_to_file("res://leves/level1/level_1.tscn")
