extends RigidBody2D
class_name Block

@export var controllable: bool = false
@export var is_static: bool = false
@export var speed := 400.0
@export var id := 1

signal placed_on_stack(block)

func _ready() -> void:
	contact_monitor = true
	max_contacts_reported = 10

	if not body_entered.is_connected(_on_body_entered):
		body_entered.connect(_on_body_entered)

	if is_static:
		make_static()
	else:
		freeze = false

	if controllable:
		gravity_scale = 0.0


func _physics_process(delta: float) -> void:
	if not controllable or is_static:
		return

	var direction := Input.get_axis("move_left", "move_right")
	linear_velocity.x = direction * speed

	if Input.is_action_just_pressed("jump"):
		gravity_scale = 1.0
		linear_velocity.y = -300


func _on_body_entered(body: Node) -> void:
	if is_static:
		return

	if body is Block:
		print("hol2")
		place_on_stack()


func place_on_stack() -> void:
	controllable = false
	is_static = true
	placed_on_stack.emit(self)
	spawn_next()
	make_static()
	

func spawn_next() -> void:
	var nou = load("res://block.tscn").instantiate()
	nou.controllable = true
	nou.is_static = false
	nou.id = id + 1
	nou.position = position + Vector2(0, -350)
	get_parent().call_deferred("add_child", nou)
	var tween = create_tween()
	tween.tween_property(get_viewport().get_camera_2d(), "position:y", get_viewport().get_camera_2d().position.y - 250, 0.4)
	make_static()
	
func make_static() -> void:
	controllable = false
	is_static = true
	linear_velocity = Vector2.ZERO
	angular_velocity = 0.0
	gravity_scale = 0.0
	freeze_mode = RigidBody2D.FREEZE_MODE_STATIC
	freeze = true
