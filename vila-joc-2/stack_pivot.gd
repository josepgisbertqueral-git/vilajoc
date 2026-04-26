extends Node2D
class_name StackPivot
@export var max_speed := 150.0
@export var limit := 250.0

var direction := 1
var speed := 100.0
var change_timer := 0.0

func _ready():
	randomize()
	reset_timer()

func _process(delta):
	change_timer -= delta

	if change_timer <= 0:
		randomize_movement()

	position.x += direction * speed * delta

	# límits perquè no marxi massa
	if abs(position.x) > limit:
		direction *= -1

func randomize_movement():
	direction = [-1, 1].pick_random()
	speed = randf_range(60, max_speed)
	reset_timer()

func reset_timer():
	change_timer = randf_range(0.5, 2.0)
