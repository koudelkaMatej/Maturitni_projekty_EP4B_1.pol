extends Node
#game logic script

var grid := {}  #{ Vector2i(q, r): true}
const MAP_PATH := "user://maps/level1.json"
@onready var hex_overlay := get_parent().get_node("HexOverlay")
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

# ------------------------ # 

# -------- Running thingie and map generating and stuff ---------#
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

#--- Map Load/ Safe ---#

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
