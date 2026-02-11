extends Node
#game logic script

var grid := {}  #{ Vector2i(q, r): true}
var units := [] # list of unit nodes
const MAP_PATH := "user://maps/level1.json"
@onready var hex_overlay := get_parent().get_node("HexOverlay")
var selected_unit = null
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


func _ready() -> void:
	generate_grid()
	#if map_file_exists():
		#load_map()
	#else:
		#generate_grid()
		#save_map()

func get_neighbors(h: Vector2i) -> Array:
	var dirs = NEIGHBORS_ODD if h.x % 2 == 1 else NEIGHBORS_EVEN
	var result := []

	for d in dirs:
		var n = h + d
		if grid.has(n):
			result.append(n)

	return result

func generate_grid():
	for q in range(15):
		for r in range(7):
			grid[Vector2i(q, r)] = {
				"q": q,
				"r": r,
				"walkable": true,
				"unit": null
			}

func register_unit(unit):
	units.append(unit)
	grid[unit.hex]["unit"] = unit
	
func spawn_unit(hex: Vector2i):
	var unit = preload("res://leves/level1/units/unit.tscn").instantiate()
	unit.hex = hex
	get_parent().get_node("Units").add_child(unit)
	register_unit(unit)
	
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
			"unit": null
		}

func save_map():
	var data := {}
	data["hexes"] = []
	
	for h in grid.keys():
		data["hexes"].append({
			"q": h.x,
			"r": h.y,
			"walkable": grid[h]["walkable"]
		})
	DirAccess.make_dir_recursive_absolute("user://maps")
	
	var file = FileAccess.open(MAP_PATH, FileAccess.WRITE)
	file.store_string(JSON.stringify(data))
	file.close()
	
func map_file_exists():
	return FileAccess.file_exists(MAP_PATH)
	
func update_unit_pos():
	for unit in units:
		unit.move_to_hex(unit.hex)
		

func clear_selection():
	selected_unit = null
	hex_overlay.reachable_hexes.clear()
	hex_overlay.queue_redraw()
	
func on_hex_clicked(hex: Vector2i):
	var cell = grid[hex]

	# Clicked on a unit → select it
	if cell["unit"]:
		select_unit(cell["unit"])
		return

	# Clicked empty hex while unit selected → move
	if selected_unit:
		try_move_unit(selected_unit, hex)

func select_unit(unit):
	selected_unit = unit
	unit.selected = true
	$HexOverlay.compute_reachable(unit)
	$HexOverlay.queue_redraw()

func try_move_unit(unit, target_hex):
	if not $HexOverlay.reachable_hexes.has(target_hex):
		return

	grid[unit.hex]["unit"] = null
	unit.hex = target_hex
	grid[target_hex]["unit"] = unit
	unit.move_to_hex(target_hex)

	unit.selected = false
	selected_unit = null
	$HexOverlay.reachable_hexes.clear()
	$HexOverlay.queue_redraw()
