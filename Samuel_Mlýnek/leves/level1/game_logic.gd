extends Node
#game logic script

var grid := {}  # {Vector2i(q, r): true}

var debug_mode = true

var MAP_LOAD_PATH: String
const MAP_SAVE_PATH := "user://maps/level1.json"
@onready var hex_overlay := get_parent().get_node("HexOverlay")
@onready var ui = get_parent().get_node("UI")
@onready var city_button = ui.get_node("CityButton")
@onready var city_menu_layer = ui.get_node("CityMenuLayer")
@onready var options_layer = ui.get_node("OptionLayer")
@export var unit_scene: PackedScene
@export var city_menu_scene : PackedScene
@export var options_menu : PackedScene
@export var artillery_scene : PackedScene
var units = []
var attackable_hexes = []
var reachable_costs = {}  # hex -> cost
var came_from = {}  # hex -> previous hex
var selected_unit = null
var selected_city_hex : Vector2i
var player_gold = 10
var enemy_gold = 10
var turn_number = 1
var game_over = false
const TERRAIN_COST = {
	"plains": 1,
	"forest": 2,
	"mountain": 3,
	"water": 999  # basically unwalkable
}

const NEIGHBORS_EVEN = [
	Vector2i(+1, 0), Vector2i(+1, -1),
	Vector2i(0, -1), Vector2i(-1, -1),
	Vector2i(-1, 0), Vector2i(0, +1)
]

const NEIGHBORS_ODD = [
	Vector2i(+1, +1), Vector2i(+1, 0),
	Vector2i(0, -1), Vector2i(-1, 0),
	Vector2i(-1, +1), Vector2i(0, +1)
]

# --- unit shit --- #

func spawn_unit(hex: Vector2i):
	var unit = unit_scene.instantiate()
	add_child(unit)

	unit.unit_owner = "player"
	var poll = Vector2(40, 40)
	unit.initialize(hex, poll)
	unit.position = hex_overlay.hex_to_pixel(hex)
	
	unit.has_moved = true
	unit.has_attacked = true
	unit.move_points = 0

	units.append(unit)
	grid[hex]["unit"] = unit

func select_unit(unit):
	selected_unit = unit
	show_movement_range(unit)
	update_attackable(unit)

func build_path(to_hex):

	var path = []
	var current = to_hex

	while current != null:
		path.push_front(current)
		current = came_from[current]

	return path

func show_movement_range(unit):

	reachable_costs.clear()
	came_from.clear()

	var frontier = [unit.hex_position]

	reachable_costs[unit.hex_position] = 0
	came_from[unit.hex_position] = null

	while frontier.size() > 0:
		var current = frontier.pop_front()

		for n in get_neighbors(current):
			
			if grid[n]["terrain"] == "water":
				continue

			if grid[n]["unit"] != null:
				continue

			var terrain = grid[n]["terrain"]
			var move_cost = 1
			if not unit.ignores_terrain:
				move_cost = TERRAIN_COST.get(terrain, 1)

			var new_cost = reachable_costs[current] + move_cost

			if new_cost > unit.move_points:
				continue

			if not reachable_costs.has(n):
				reachable_costs[n] = new_cost
				came_from[n] = current
				frontier.append(n)

	hex_overlay.highlight_hexes(reachable_costs.keys())

func show_attack_range(unit):

	var tiles = []

	for n in get_neighbors(unit.hex_position):
		var u = grid[n]["unit"]

		if u != null and u.unit_owner != unit.unit_owner:
			tiles.append(n)

	hex_overlay.set_attack_highlight(tiles)

func on_hex_clicked(hex: Vector2i):

	if not grid.has(hex):
		return

	var clicked_unit = grid[hex]["unit"]

	# -------------------------
	# 1. CLICKED A UNIT
	# -------------------------
	if clicked_unit != null:

		# 🟥 enemy clicked
		if clicked_unit.unit_owner != "player":

			if selected_unit != null:

				# ONLY allow attack if in attack range
				if attackable_hexes.has(hex):

					attack_unit(selected_unit, clicked_unit)

					selected_unit.has_attacked = true
					selected_unit.has_moved = true

					selected_unit = null
					hex_overlay.highlight_hexes([])
					hex_overlay.set_attack_highlight([])

			return

		# 🟦 player unit clicked
		if clicked_unit.unit_owner == "player":

			# prevent reusing moved unit
			if clicked_unit.has_moved:
				return

			select_unit(clicked_unit)
			return

	# -------------------------
	# 2. MOVE
	# -------------------------
	if selected_unit != null:

		# already used turn
		if selected_unit.has_moved:
			return

		# clicked same tile → deselect
		if hex == selected_unit.hex_position:
			selected_unit = null
			hex_overlay.highlight_hexes([])
			hex_overlay.set_attack_highlight([])
			return

		# not reachable → deselect
		if not reachable_costs.has(hex):
			selected_unit = null
			hex_overlay.highlight_hexes([])
			hex_overlay.set_attack_highlight([])
			return

		var path = build_path(hex)
		path.pop_front()  # remove current tile

		for step in path:

			grid[selected_unit.hex_position]["unit"] = null
			grid[step]["unit"] = selected_unit

			selected_unit.hex_position = step
			selected_unit.position = hex_overlay.hex_to_pixel(step)

			var terrain = grid[step]["terrain"]
			var cost = TERRAIN_COST.get(terrain, 1)
			
			selected_unit.move_points -= cost

		# capture city
		if grid[hex]["city"]:
			grid[hex]["owner"] = selected_unit.unit_owner
			check_victory()  # ← add this!
			hex_overlay.queue_redraw()
			
		# 🔒 lock unit after move
		selected_unit.has_moved = true

		# check if there's anything to attack nearby
		update_attackable(selected_unit)
		if attackable_hexes.size() > 0:
			# stay selected so player can attack
			hex_overlay.highlight_hexes([])  # clear move highlights
			hex_overlay.set_attack_highlight(attackable_hexes)  # show attack options
		else:
			# nothing to attack, deselect
			selected_unit = null
			hex_overlay.highlight_hexes([])
			hex_overlay.set_attack_highlight([])

		return

	# -------------------------
	# 3. CITY INTERACTION
	# -------------------------
	if grid[hex]["city"] and grid[hex]["owner"] == "player":
		show_city_button(hex)
	else:
		hide_city_button()

func get_step_toward(start_hex: Vector2i, target_hex: Vector2i, unit) -> Vector2i:

	var neighbors = get_neighbors(start_hex)
	var best_hex = start_hex
	var best_score = 999999

	for n in neighbors:
		if grid[n]["unit"] != null:
			continue
		if grid[n]["terrain"] == "water":
			continue

		var terrain_cost = 1
		if not unit.ignores_terrain:
			terrain_cost = TERRAIN_COST.get(grid[n]["terrain"], 1)

		var dist = hex_overlay.hex_distance(n, target_hex)
		var score = dist + terrain_cost  # prefer closer AND cheaper terrain

		if score < best_score:
			best_score = score
			best_hex = n

	return best_hex
# -------- Running thingie and map generating and stuff ---------#

func _ready() -> void:
	MAP_LOAD_PATH = "res://maps/level%d.json" % global.current_level
	
	if map_file_exists():
		load_map()
	else:
		generate_grid()
		save_map()
	
	update_ui()
	city_button.visible = false
	hex_overlay.queue_redraw()
	level_preset_units(global.current_level)
	
	if global.load_save and not global.is_guest:
		await get_tree().create_timer(0.1).timeout
		load_from_server()
		global.load_save = false

func get_neighbors(h: Vector2i) -> Array:
	var dirs = NEIGHBORS_ODD if h.x % 2 == 1 else NEIGHBORS_EVEN
	var result := []

	for d in dirs:
		var n = h + d
		if grid.has(n):
			result.append(n)

	return result

func generate_grid():
	for q in range(14):
		for r in range(7):
			grid[Vector2i(q, r)] = {
				"q": q,
				"r": r,
				"walkable": true,
				"unit": null,
				"city": false,
				"terrain": "plains",
				"owner": null
			}

#--- Map Load/ Save ---#

func load_map():
	grid.clear()

	var file = FileAccess.open(MAP_LOAD_PATH, FileAccess.READ)
	var data = JSON.parse_string(file.get_as_text())
	file.close()

	for hex_data in data["hexes"]:
		var h = Vector2i(hex_data["q"], hex_data["r"])
		grid[h] = {
			"q": h.x,
			"r": h.y,
			"walkable": hex_data["walkable"],
			"unit": null,
			"city": hex_data["city"],
			"terrain": hex_data["terrain"],
			"owner": hex_data["owner"]
		}

func _on_load_button_pressed() -> void:
	if global.is_guest:
		load_game()  # local file
	else:
		load_from_server()

func save_map():
	var data := {}
	data["hexes"] = []
	
	for h in grid.keys():
		data["hexes"].append({
			"q": h.x,
			"r": h.y,
			"walkable": grid[h]["walkable"],
			"unit": null,
			"city": grid[h]["city"],
			"terrain": grid[h]["terrain"],
			"owner": grid[h]["owner"]
		})
	DirAccess.make_dir_recursive_absolute(MAP_SAVE_PATH)
	
	var file = FileAccess.open(MAP_SAVE_PATH, FileAccess.WRITE)
	file.store_string(JSON.stringify(data))
	file.close()
	
func _on_save_button_pressed() -> void:
	save_game()
	if !global.is_guest:
		send_save_to_server()
		
func map_file_exists():
	return FileAccess.file_exists(MAP_LOAD_PATH)

#--- GAME Load/ save ---#

func save_game():

	var data = {}
	data["turn"] = current_turn
	data["player_gold"] = player_gold
	data["enemy_gold"] = enemy_gold

	data["cities"] = []
	data["units"] = []

	for h in grid.keys():

		if grid[h]["city"]:
			data["cities"].append({
				"q": h.x,
				"r": h.y,
				"owner": grid[h]["owner"]
			})

	for unit in units:

		data["units"].append({
			"q": unit.hex_position.x,
			"r": unit.hex_position.y,
			"owner": unit.unit_owner,
			"hp": unit.hp
		})

	var file = FileAccess.open("user://savegame.json", FileAccess.WRITE)
	file.store_string(JSON.stringify(data))
	file.close()

func load_game():

	if not FileAccess.file_exists("user://savegame.json"):
		return

	var file = FileAccess.open("user://savegame.json", FileAccess.READ)
	var data = JSON.parse_string(file.get_as_text())
	file.close()

	current_turn = data["turn"]
	player_gold = data["player_gold"]
	enemy_gold = data["enemy_gold"]
	
	for h in grid.keys():
		grid[h]["unit"] = null

	for unit in units:
		unit.queue_free()

	units.clear()

	for u in data["units"]:

		var hex = Vector2i(u["q"],u["r"])

		var unit = unit_scene.instantiate()
		add_child(unit)

		unit.initialize(hex, Vector2(40,40))
		unit.unit_owner = u["owner"]
		unit.hp = u["hp"]

		unit.position = hex_overlay.hex_to_pixel(hex)

		grid[hex]["unit"] = unit
		units.append(unit)

	for c in data["cities"]:

		var h = Vector2i(c["q"],c["r"])
		grid[h]["owner"] = c["owner"]

	hex_overlay.queue_redraw()
#--- UI ---#
func update_ui():
	ui.get_node("GoldLabel").text = "Gold: " + str(player_gold)
	ui.get_node("TurnLabel").text = "Turn: " + str(turn_number)

func _on_city_button_pressed() -> void:
	var menu = city_menu_scene.instantiate()
	city_menu_layer.add_child(menu)
	menu.setup(selected_city_hex, self)
	city_button.visible = false

func show_city_button(hex):
	selected_city_hex = hex
	city_button.visible = true

func hide_city_button():
	city_button.visible = false

func _on_options_pressed() -> void:
	if options_layer.get_child_count() == 0:
		var options = options_menu.instantiate()
		options_layer.add_child(options)

#--- TURN SYSTEM BLIAT ---#

enum Turn {PLAYER, ENEMY}
var current_turn = Turn.PLAYER
var turn_order = []  # All units in the turn, can be filtered by owner
var turn_index = 0

func start_turn(turn_type):
	
	if turn_type == Turn.PLAYER:
		turn_number += 1
		process_income()
		
	current_turn = turn_type
	update_ui()
	check_victory()
	# select units of this turn
	turn_order = []
	for unit in units:
		if unit.unit_owner == ("player" if turn_type == Turn.PLAYER else "enemy"):
			turn_order.append(unit)
			
	# reset movement/attack flags
	for unit in turn_order:
		unit.has_moved = false
		unit.has_attacked = false
		unit.move_points = unit.max_mov

func _on_turn_button_pressed() -> void:
	if current_turn != Turn.PLAYER:
		return

	var idle_units = []
	for unit in units:
		if unit.unit_owner == "player":
			update_attackable(unit)  # fills attackable_hexes for this unit
			if not unit.has_moved or (not unit.has_attacked and attackable_hexes.size() > 0):
				idle_units.append(unit)

	# clear highlights after checking
	attackable_hexes.clear()
	hex_overlay.set_attack_highlight([])

	if idle_units.size() > 0:
		var picked = idle_units[randi() % idle_units.size()]
		select_unit(picked)
		return

	# all done, proceed
	selected_unit = null
	hex_overlay.highlight_hexes([])
	hex_overlay.set_attack_highlight([])
	start_turn(Turn.ENEMY)
	do_enemy_turn()
	start_turn(Turn.PLAYER)
		
func do_enemy_turn():
	
	enemy_spawn_logic()
	
	for unit in turn_order:

		if unit.has_moved:
			continue

		# 🔴 check neighbors for player
		var found_target = false
		for n in get_hexes_in_range(unit.hex_position, unit.attack_range):
			var target = grid[n]["unit"]

			if target != null and target.unit_owner == "player":
				attack_unit(unit, target)
				unit.has_moved = true
				unit.has_attacked = true
				found_target = true
				break

		if found_target:
			continue

		# 🟡 otherwise move
		var target = find_nearest_player_or_city(unit)

		if target == null:
			continue

		var steps = unit.move_points

		for i in range(steps):

			var step = get_step_toward(unit.hex_position, target, unit)

			# can't move further
			if step == unit.hex_position:
				break

			move_unit_to(unit, step)

			# 🟥 check attack AFTER each step
			for n in get_neighbors(unit.hex_position):
				var enemy = grid[n]["unit"]

				if enemy != null and enemy.unit_owner == "player":
					attack_unit(unit, enemy)
					unit.has_moved = true
					break

			if unit.has_moved:
				break

func attack_unit(attacker, defender):

	defender.hp -= attacker.dmg
	defender.update_hp()

	if defender.hp <= 0:

		grid[defender.hex_position]["unit"] = null
		units.erase(defender)
		defender.queue_free()

func find_nearest_player_or_city(unit):

	var best_target = null
	var best_distance = 999999

	for h in grid.keys():

		# target player cities
		if grid[h]["city"] and grid[h]["owner"] == "player":

			var d = hex_overlay.hex_distance(unit.hex_position, h)

			if d < best_distance:
				best_distance = d
				best_target = h

		# target player units
		var other_unit = grid[h]["unit"]

		if other_unit != null and other_unit.unit_owner == "player":

			var d = hex_overlay.hex_distance(unit.hex_position, h)

			if d < best_distance:
				best_distance = d
				best_target = h

	return best_target
	
func move_unit_to(unit, target_hex):

	if target_hex == null:
		return

	var current_hex = unit.hex_position

	# remove from old tile
	grid[current_hex]["unit"] = null

	# move unit
	unit.hex_position = target_hex

	# place on new tile
	grid[target_hex]["unit"] = unit

	# capture city
	if grid[target_hex]["city"]:
		grid[target_hex]["owner"] = unit.unit_owner
		check_victory()  # ← add this!
		hex_overlay.queue_redraw()
		
	# update position visually
	unit.position = hex_overlay.hex_to_pixel(target_hex)

	# redraw map
	hex_overlay.queue_redraw()

func process_income():

	for h in grid.keys():

		if grid[h]["city"]:

			if grid[h]["owner"] == "player":
				player_gold += 3

			elif grid[h]["owner"] == "enemy":
				enemy_gold += 3

func spawn_enemy_unit(hex: Vector2i):
	var unit = unit_scene.instantiate()
	add_child(unit)

	unit.initialize(hex, Vector2(40,40))
	unit.unit_owner = "enemy"

	unit.position = hex_overlay.hex_to_pixel(hex)
	
	unit.has_moved = true
	unit.has_attacked = true
	unit.move_points = 0

	units.append(unit)
	grid[hex]["unit"] = unit

func enemy_spawn_logic():

	for h in grid.keys():

		if not grid[h]["city"]:
			continue

		if grid[h]["owner"] != "enemy":
			continue

		# check if player unit is within 3 tiles
		var danger = false

		for h2 in grid.keys():
			var u = grid[h2]["unit"]

			if u != null and u.unit_owner == "player":
				var dist = hex_overlay.hex_distance(h, h2)

				if dist <= 3:
					danger = true
					break

		if not danger:
			continue

		# check gold
		if enemy_gold < 10:
			continue

		# spawn if free
		if grid[h]["unit"] == null:
			spawn_enemy_unit(h)
			enemy_gold -= 10
#--- Faztorio ---#
func produce_unit(hex):

	if player_gold < 10:
		return

	if grid[hex]["unit"] != null:
		return

	player_gold -= 10

	spawn_unit(hex)

func _on_main_menu_button_pressed() -> void:
	get_tree().change_scene_to_file("res://start.tscn")
	
func check_victory():

	if game_over:
		return

	var player_cities = 0
	var enemy_cities = 0

	for h in grid.keys():
		if grid[h]["city"]:
			if grid[h]["owner"] == "player":
				player_cities += 1
			elif grid[h]["owner"] == "enemy":
				enemy_cities += 1

	if enemy_cities == 0:
		game_over = true
		unlock_next_level()
		get_tree().change_scene_to_file("res://UI_control_scenes/victoryScreen.tscn")
		send_result("win")

	if player_cities == 0:
		game_over = true
		get_tree().change_scene_to_file("res://UI_control_scenes/loseScreen.tscn")
		send_result("lose")
		
func update_attackable(unit):
	attackable_hexes.clear()

	# get all hexes within attack range
	var in_range = get_hexes_in_range(unit.hex_position, unit.attack_range)

	for h in in_range:
		var u = grid[h]["unit"]
		if u != null and u.unit_owner != unit.unit_owner:
			attackable_hexes.append(h)

	hex_overlay.set_attack_highlight(attackable_hexes)

func get_hexes_in_range(start: Vector2i, range_val: int) -> Array:
	var result = []
	var visited = {start: true}
	var frontier = [start]

	for i in range(range_val):
		var next = []
		for h in frontier:
			for n in get_neighbors(h):
				if not visited.has(n):
					visited[n] = true
					result.append(n)
					next.append(n)
		frontier = next

	return result

func send_result(result_type):

	if global.is_guest:
		return

	var http = HTTPRequest.new()
	add_child(http)

	var url = "http://127.0.0.1:5000/game/result"
	var headers = [
	"Content-Type: application/json",
	"X-Auth-Token: " + global.player_token
	]

	var body = JSON.stringify({
			"token": global.player_token,
			"turns": turn_number,
			"result": result_type
		})

	http.request(url, headers, HTTPClient.METHOD_POST, body)
	
func send_save_to_server():

	if global.is_guest:
		return

	var http = HTTPRequest.new()
	add_child(http)

	var url = "http://127.0.0.1:5000/game/save"
	var headers = [
	"Content-Type: application/json",
	"X-Auth-Token: " + global.player_token
	]

	var save_data = {
		"turn": current_turn,
		"player_gold": player_gold,
		"enemy_gold": enemy_gold,
		"turn_number": turn_number,
		"units": [],
		"cities": []
	}

	# save units
	for unit in units:
		save_data["units"].append({
			"q": unit.hex_position.x,
			"r": unit.hex_position.y,
			"owner": unit.unit_owner,
			"hp": unit.hp,
			"type": "artillery" if unit.get_script().get_path().contains("artillery") else "infantry"
		})

	# save cities
	for h in grid.keys():
		if grid[h]["city"]:
			save_data["cities"].append({
				"q": h.x,
				"r": h.y,
				"owner": grid[h]["owner"]
			})

	var body = JSON.stringify({
		"level_id": global.current_level,
		"score": player_gold,
		"save": save_data
	})

	http.request(url, headers, HTTPClient.METHOD_POST, body)

# ----------------HTTP requests and database meow ---------------------------#

func load_from_server():

	var http = HTTPRequest.new()
	add_child(http)

	http.request_completed.connect(_on_load_completed)

	var url = "http://127.0.0.1:5000/game/load"
	var headers = [
	"Content-Type: application/json",
	"X-Auth-Token: " + global.player_token
	]
	
	var body = JSON.stringify({
		"username": global.username,
		"level_id": global.current_level
	})

	http.request(url, headers, HTTPClient.METHOD_POST, body)

func _on_load_completed(result, response_code, headers, body):

	var data = JSON.parse_string(body.get_string_from_utf8())

	if data["status"] == "ok":
		load_from_dict(data["save"])
	else:
		print("No save found or load failed")

func load_from_dict(data):

	current_turn = data["turn"]
	player_gold = int(data["player_gold"])
	enemy_gold = int(data["enemy_gold"])
	turn_number = int(data["turn_number"])

	# clear units
	for h in grid.keys():
		grid[h]["unit"] = null
	for unit in units:
		unit.queue_free()
	units.clear()

	# recreate units
	for u in data["units"]:
		var hex = Vector2i(u["q"], u["r"])
		var unit

		# pick the right scene based on saved type
		if u.get("type", "infantry") == "artillery":
			unit = artillery_scene.instantiate()
		else:
			unit = unit_scene.instantiate()

		add_child(unit)
		unit.unit_owner = u["owner"]   # ← BEFORE initialize!
		unit.initialize(hex, Vector2(40, 40))
		unit.hp = int(u["hp"])
		unit.position = hex_overlay.hex_to_pixel(hex)
		grid[hex]["unit"] = unit
		units.append(unit)

	# restore cities
	for c in data["cities"]:
		var h = Vector2i(c["q"], c["r"])
		grid[h]["owner"] = c["owner"]

	update_ui()
	hex_overlay.queue_redraw()

func unlock_next_level():
	var new_highest = min(global.current_level + 1, 3)

	if global.is_guest:
		# save locally
		var file = FileAccess.open("user://progress.json", FileAccess.WRITE)
		file.store_string(JSON.stringify({"highest_unlocked": new_highest}))
		file.close()
	else:
		send_completion_to_server()
		

func send_completion_to_server():
	var http = HTTPRequest.new()
	add_child(http)

	var url = "http://127.0.0.1:5000/game/save"
	var headers = [
		"Content-Type: application/json",
		"X-Auth-Token: " + global.player_token
	]

	var body = JSON.stringify({
		"level_id": global.current_level,
		"score": player_gold,
		"save": {
			"player_gold": player_gold,
			"enemy_gold": enemy_gold,
			"turn_number": turn_number,
			"completed": 1,   # ← marks this level as done
			"units": [],
			"cities": []
			}
		})

	http.request(url, headers, HTTPClient.METHOD_POST, body)

func level_preset_units(level_num):
	if level_num == 1:
		spawn_artillery(Vector2(3, 3))
		spawn_enemy_artillery(Vector2(11, 1))
		spawn_enemy_unit(Vector2(12, 0))
		spawn_enemy_unit(Vector2(11, 5))
		spawn_unit(Vector2(1, 0))
		spawn_enemy_artillery(Vector2(13, 4))
		spawn_unit(Vector2(0, 5))
		

func produce_artillery(hex):
	if player_gold < 15:
		return

	if grid[hex]["unit"] != null:
		return

	player_gold -= 15
	spawn_artillery(hex)

func spawn_artillery(hex: Vector2i):
	var unit = artillery_scene.instantiate()
	add_child(unit)

	unit.unit_owner = "player"   # ← before initialize!
	unit.initialize(hex, Vector2(40, 40))
	unit.position = hex_overlay.hex_to_pixel(hex)

	unit.has_moved = true
	unit.has_attacked = true
	unit.move_points = 0

	units.append(unit)
	grid[hex]["unit"] = unit

func spawn_enemy_artillery(hex: Vector2i):
	var unit = artillery_scene.instantiate()
	add_child(unit)

	unit.unit_owner = "enemy"
	unit.initialize(hex, Vector2(40, 40))
	unit.position = hex_overlay.hex_to_pixel(hex)

	unit.has_moved = true
	unit.has_attacked = true
	unit.move_points = 0

	units.append(unit)
	grid[hex]["unit"] = unit
