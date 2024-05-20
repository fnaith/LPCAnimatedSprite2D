extends Node2D

@onready var SpriteParts: LPCAnimatedSprite2D = $"CanvasLayer/GridContainer/Control/SpriteParts"

@onready var AnimationOption: OptionButton = $CanvasLayer/Control/VBoxContainer/AnimationOption
@onready var BodyOption: OptionButton = $CanvasLayer/Control/VBoxContainer/BodyOption
@onready var BodyVariant: OptionButton = $CanvasLayer/Control/VBoxContainer/BodyVariant

static var BODY_OPTIONS: Array[String] = ["male", "muscular", "female", "pregnant", "teen", "child"]
static var BODY_VARIANTS: Array[String] = ["light", "amber", "olive", "taupe", "bronze",\
											"brown", "black", "lavender", "blue", "zombie_green",\
											"green", "pale_green", "bright_green", "dark_green", "fur_black",\
											"fur_brown", "fur_tan", "fur_copper", "fur_gold", "fur_grey",\
											"fur_white"]

@onready var body: LPCSpriteSheet = preload("res://lpc/body/bodies/female/light.tres")
@onready var head: LPCSpriteSheet = preload("res://lpc/head/heads/human_female/light.tres")
@onready var hair: LPCSpriteSheet = preload("res://lpc/hair/long_messy/female/purple.tres")
@onready var torso: LPCSpriteSheet = preload("res://lpc/torso/aprons/apron_full/female/white.tres")

func _ready() -> void:
	for value: String in LPCAnimatedSprite2D.LPCAnimation:
		AnimationOption.add_item(value)
	for value: String in BODY_OPTIONS:
		BodyOption.add_item(value)
	for value: String in BODY_VARIANTS:
		BodyVariant.add_item(value)

	AnimationOption.select(LPCAnimatedSprite2D.LPCAnimation.WALK_DOWN)
	BodyOption.select(0)
	BodyVariant.select(0)

	SpriteParts.SpriteSheets.append(body)
	SpriteParts.SpriteSheets.append(head)
	SpriteParts.SpriteSheets.append(hair)
	SpriteParts.SpriteSheets.append(torso)
	SpriteParts.LoadAnimations()

func _on_animation_option_item_selected(index: int) -> void:
	var animation: LPCAnimatedSprite2D.LPCAnimation = index as LPCAnimatedSprite2D.LPCAnimation
	SpriteParts.play(animation)

func _on_body_option_item_selected(_index: int) -> void:
	BodyVariant.clear()
	for value: String in BODY_VARIANTS:
		BodyVariant.add_item(value)
	_update_body_sprite_sheet()

func _on_body_variant_item_selected(_index: int) -> void:
	_update_body_sprite_sheet()

func _update_body_sprite_sheet() -> void:
	var body_option: String = BODY_OPTIONS[BodyOption.selected]
	var body_variant: String = BODY_VARIANTS[BodyVariant.selected]
	var sprite_sheet: LPCSpriteSheet = load("res://lpc/body/bodies/%s/%s.tres" % [body_option, body_variant])
	SpriteParts.SpriteSheets[0] = sprite_sheet
	SpriteParts.LoadAnimations()
