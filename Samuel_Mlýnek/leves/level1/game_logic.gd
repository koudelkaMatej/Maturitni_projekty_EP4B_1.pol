extends Node
#game logic script

var grid := {}  # {Vector2i(q, r): true}

const MAP_PATH := "user://maps/level1.json"
@onready var hex_overlay := get_parent().get_node("HexOverlay")
@onready var ui = get_parent().get_node("UI")
@onready var city_button = ui.get_node("CityButton")
@onready var city_menu_layer = ui.get_node("CityMenuLayer")
@onready var options_layer = ui.get_node("OptionLayer")
@export var unit_scene: PackedScene
@export var city_menu_scene : PackedScene
@export var options_menu : PackedScene
var units = []
var reachable_hexes = []
var selected_unit = null
var selected_city_hex : Vector2i
var player_gold = 10
var enemy_gold = 10

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

	var poll = Vector2(40, 40)
	unit.initialize(hex, poll)
	
	unit.unit_owner = "player"

	unit.position = hex_overlay.hex_to_pixel(hex)

	units.append(unit)

	grid[hex]["unit"] = unit

func select_unit(unit):
	
	selected_unit = unit
	show_movement_range(unit)

func show_movement_range(unit):

	reachable_hexes.clear()

	for hex in grid.keys():

		var dist = hex_overlay.hex_distance(unit.hex_position, hex)

		if dist <= unit.max_mov:
			reachable_hexes.append(hex)

	hex_overlay.highlight_hexes(reachable_hexes)

func on_hex_clicked(hex: Vector2i):

	if not grid.has(hex):
		return

	# --- click on unit ---
	if grid[hex]["unit"] != null:
		hide_city_button()
		select_unit(grid[hex]["unit"])
		return

	# --- move selected unit first ---
	if selected_unit != null:
		
		# deselect if outside movement range
		if not reachable_hexes.has(hex):
			selected_unit = null
			hex_overlay.highlight_hexes([])
			return
		
		# move unit
		if grid[hex]["unit"] == null:
			
			if grid[hex]["city"]:
				grid[hex]["city_owner"] = selected_unit.owner
				hex_overlay.queue_redraw()
			
			var old_hex = selected_unit.hex_position

			grid[old_hex]["unit"] = null
			grid[hex]["unit"] = selected_unit

			selected_unit.hex_position = hex
			selected_unit.position = hex_overlay.hex_to_pixel(hex)

			selected_unit = null
			hex_overlay.highlight_hexes([])

			return

	# --- city interaction AFTER movement ---
	if grid[hex]["city"]:
		show_city_button(hex)
		return

	hide_city_button()

func get_step_toward(start_hex: Vector2i, target_hex: Vector2i):

	var neighbors = get_neighbors(start_hex)

	var best_hex = start_hex
	var best_dist = 999999

	for n in neighbors:

		# don't walk into other units
		if grid[n]["unit"] != null:
			continue

		var d = hex_overlay.hex_distance(n, target_hex)

		if d < best_dist:
			best_dist = d
			best_hex = n

	return best_hex
# -------- Running thingie and map generating and stuff ---------#

func _ready() -> void:
	if map_file_exists():
		load_map()
	else:
		generate_grid()
		save_map()

	city_button.visible = false
	hex_overlay.queue_redraw()

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

	var file = FileAccess.open(MAP_PATH, FileAccess.READ)
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
			"terrain": null,
			"owner":null
		}
func _on_load_button_pressed() -> void:
	load_game()
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
			"terrain": null,
			"owner": null
		})
	DirAccess.make_dir_recursive_absolute("user://maps")
	
	var file = FileAccess.open(MAP_PATH, FileAccess.WRITE)
	file.store_string(JSON.stringify(data))
	file.close()
func _on_save_button_pressed() -> void:
	save_game()
func map_file_exists():
	return FileAccess.file_exists(MAP_PATH)

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
	current_turn = turn_type
	
	process_income()
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

func _on_turn_button_pressed() -> void:
	if current_turn == Turn.PLAYER:
		start_turn(Turn.ENEMY)
		do_enemy_turn()
	else:
		start_turn(Turn.PLAYER)
		
func do_enemy_turn():
	
	for unit in turn_order:

		if unit.has_moved:
			continue

		var target = find_nearest_player_or_city(unit)

		if target == null:
			continue

		var step = get_step_toward(unit.hex_position, target)

		move_unit_to(unit, step)

		unit.has_moved = true

	start_turn(Turn.PLAYER)

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

	units.append(unit)

	grid[hex]["unit"] = unit

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

	var player_cities = 0
	var enemy_cities = 0

	for h in grid.keys():
		if grid[h]["city"]:
			if grid[h]["owner"] == "player":
				player_cities += 1
			elif grid[h]["owner"] == "enemy":
				enemy_cities += 1

	if enemy_cities == 0:
		print("PLAYER WINS")

	if player_cities == 0:
		print("ENEMY WINS")
