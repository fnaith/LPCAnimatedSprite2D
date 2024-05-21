extends Node2D

@onready var SpriteParts: LPCAnimatedSprite2D = $"CanvasLayer/GridContainer/Control/SpriteParts"

@onready var OptionRoot: VBoxContainer = $CanvasLayer/Control/VBoxContainer
@onready var AnimationOption: OptionButton = $CanvasLayer/Control/VBoxContainer/AnimationOption

static var BODY_OPTIONS: Array[String] = ["male", "muscular", "female", "pregnant", "teen", "child"]

func load_json(path: String) -> Variant:
	var file: FileAccess = FileAccess.open(path, FileAccess.READ)
	var text: String = file.get_as_text()
	var json: JSON = JSON.new()
	json.parse(text)
	return json.data

static var type_name_to_option_info: Dictionary = {}

func update_spritesheets() -> void:
	var layers: Array = []
	for type_name: String in type_name_to_option_info:
		var option_info: Variant = type_name_to_option_info[type_name]
		var layers_info: Variant = option_info['layers']
		if null == layers_info:
			continue
		var variant: String = option_info['variant']
		for layer: Variant in layers_info:
			layers.append(["res://lpc/" + layer[0] + variant + ".tres", layer[1]])
	layers.sort_custom(func (a: Variant, b: Variant) -> bool:
		return a[1] < b[1])
	SpriteParts.SpriteSheets.clear()
	for layer: Variant in layers:
		#print(layer[0])
		var sprite_sheet: LPCSpriteSheet = load(layer[0])
		SpriteParts.SpriteSheets.append(sprite_sheet)
	SpriteParts.LoadAnimations()
	var animation: LPCAnimatedSprite2D.LPCAnimation = AnimationOption.selected as LPCAnimatedSprite2D.LPCAnimation
	SpriteParts.play(animation)

func generate_option_ui(type_name: String, name_to_spritesheets: Variant) -> void:
	var type_name_label: Label = Label.new()
	var name_option: OptionButton = OptionButton.new()
	var variant_option: OptionButton = OptionButton.new()
	var ui_size: Vector2 = Vector2(200, 20)
	var names: Array[String] = []
	var option_info: Dictionary = {}
	type_name_to_option_info[type_name] = option_info
	option_info['name_index'] = 0
	option_info['variant_index'] = 0
	option_info['variant'] = ''
	option_info['layers'] = null

	var update_variant_option: Callable = func () -> void:
		variant_option.clear()
		var name_index: int = option_info['name_index']
		var part_name: String = names[name_index]
		for variant_info: Variant in name_to_spritesheets[part_name]:
			variant_option.add_item(variant_info[0])
		option_info['variant_index'] = 0
		variant_option.selected = 0

	var update_layers_info: Callable = func () -> void:
		var name_index: int = option_info['name_index']
		var variant_index: int = option_info['variant_index']
		var part_name: String = names[name_index]
		var variant_info: Variant = name_to_spritesheets[part_name][variant_index]
		option_info['variant'] = variant_info[0]
		option_info['layers'] = variant_info[1]

	var on_select_name: Callable = func (index: int) -> void:
		option_info['name_index'] = index
		update_variant_option.call()
		update_layers_info.call()
		update_spritesheets()

	var on_select_variant: Callable = func (index: int) -> void:
		option_info['variant_index'] = index
		update_layers_info.call()
		update_spritesheets()

	type_name_label.size = ui_size
	type_name_label.text = type_name

	name_option.size = ui_size
	for part_name: String in name_to_spritesheets:
		names.append(part_name)
		name_option.add_item(part_name)
	name_option.connect("item_selected", on_select_name)
	on_select_name.call(0)

	variant_option.size = ui_size
	variant_option.connect("item_selected", on_select_variant)

	OptionRoot.add_child(type_name_label)
	OptionRoot.add_child(name_option)
	OptionRoot.add_child(variant_option)

func _ready() -> void:
	for value: String in LPCAnimatedSprite2D.LPCAnimation:
		AnimationOption.add_item(value)

	AnimationOption.select(LPCAnimatedSprite2D.LPCAnimation.WALK_DOWN)

	var spritesheets: Variant = load_json("res://lpc/spritesheets-female.json")
	for type_name: String in ['body', 'head', 'hair', 'apron']:
		var name_to_spritesheets: Variant = spritesheets[type_name]
		generate_option_ui(type_name, name_to_spritesheets)

func _on_animation_option_item_selected(index: int) -> void:
	var animation: LPCAnimatedSprite2D.LPCAnimation = index as LPCAnimatedSprite2D.LPCAnimation
	SpriteParts.play(animation)
