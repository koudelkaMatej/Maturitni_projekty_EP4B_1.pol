extends Control
#login screen script
@onready var http = $HTTPRequest
var game_scene = "res://start.tscn"

func _ready():
	http.request_completed.connect(_on_request_completed)
	
func _on_guest_pressed():
	global.is_guest = true
	get_tree().change_scene_to_file("res://start.tscn")
	
func _on_log_in_pressed():

	var username = $VBoxContainer/Username.text
	var password = $VBoxContainer/Password.text

	var url = "http://127.0.0.1:5000/game/login"
	var headers = [
	"Content-Type: application/json",
	"X-Auth-Token: " + global.player_token
	]
	
	var body = JSON.stringify({
		"username": username,
		"password": password
	})

	http.request(url, headers, HTTPClient.METHOD_POST, body)

	
func _on_request_completed(result, response_code, headers, body):
	var text = body.get_string_from_utf8()
	print("Server response:", text)

	var data = JSON.parse_string(text)

	if data == null:
		print("ERROR: could not parse server response")
		return

	if response_code == 200 and data["status"] == "ok":
		global.is_guest = false
		global.player_token = data["token"]
		global.username = data["username"]
		print("Logged in as:", global.username)
		get_tree().change_scene_to_file(game_scene)  # scene change AFTER we have the token
	else:
		print("Login failed:", text)
