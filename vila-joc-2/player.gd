extends Casteller
class_name Player

@export var speed = 400
@export var is_controlled := true
@onready var sprite: AnimatedSprite2D = $AnimatedSprite2D
@onready var background: InfiniteBackground = $"../Background"
var facing_right := true
var is_jumping := false

func _ready() -> void:
	contact_monitor = true
	max_contacts_reported = 10

	if is_controlled:
		gravity_scale = 0.0
		sprite.play("default")
	else:
		gravity_scale = 1.0
	if is_static:
		freeze_mode = RigidBody2D.FREEZE_MODE_STATIC
		freeze = true

func _physics_process(delta):
	if not is_controlled:
		return
	var direction = 0

	if Input.is_action_pressed("move_right"):
		direction += 1
	if Input.is_action_pressed("move_left"):
		direction -= 1

	if direction > 0:
		facing_right = true
		if not is_jumping:
			sprite.play("dreta")
	elif direction < 0:
		facing_right = false
		if not is_jumping:
			sprite.play("esquerra")
			

	if Input.is_action_just_pressed("jump"):
		gravity_scale = 1.0
		linear_velocity.y = -300
		is_jumping = true
		sprite.play("saltar")
		background.move_step()

	linear_velocity.x = direction * speed


func _on_body_entered(body: Node) -> void:
	if body is Casteller:
		is_jumping = false

		if body.id == id - 1:
			print("correcte")
