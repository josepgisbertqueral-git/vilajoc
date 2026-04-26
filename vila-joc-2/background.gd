extends Node2D
class_name InfiniteBackground

@export var step_amount := 80.0
@export var move_duration := 1.5

@onready var backgrounds: Array[Sprite2D] = [
	$Bg1,
	$Bg2,
	$Bg3
]

var bg_height := 0.0
var is_moving := false

func _ready() -> void:
	bg_height = abs(backgrounds[1].global_position.y - backgrounds[0].global_position.y)


func move_step() -> void:
	if is_moving:
		return

	is_moving = true

	var tween := create_tween()
	tween.set_parallel(true)

	for bg in backgrounds:
		tween.tween_property(
			bg,
			"global_position:y",
			bg.global_position.y + step_amount,
			move_duration
		)

	tween.finished.connect(func():
		_recycle()
		is_moving = false
	)


func _recycle() -> void:
	backgrounds.sort_custom(func(a, b): return a.global_position.y < b.global_position.y)

	var top = backgrounds[0]

	for bg in backgrounds:
		if bg.global_position.y >= top.global_position.y + bg_height * 3:
			bg.global_position.y -= bg_height * 3
