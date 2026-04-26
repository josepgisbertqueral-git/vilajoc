
extends Casteller
class_name Jugador
@export var speed = 400

# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	gravity_scale = 0.0


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta: float) -> void:
	pass


func _physics_process(delta):
	var direction = 0

	if Input.is_action_pressed("move_right"):
		direction += 1
	if Input.is_action_pressed("move_left"):
		direction -= 1
	if Input.is_action_just_pressed("jump"):
		gravity_scale = 1.0
		linear_velocity.y = -300 # impuls cap amunt

	# Mou lateralment (control directe però físic-ish)
	linear_velocity.x = direction * speed


func _on_body_entered(body: Node) -> void:
	print("primer")

	if body is Casteller:
		print("segon")

		var gm = get_tree().current_scene.get_node("GameManager")

		if body == gm.get_top_casteller():
			print("correcte")

			var joint := PinJoint2D.new()
			joint.name = "Joint_%s_%s" % [body.id, id]

			get_tree().current_scene.add_child(joint)

			joint.global_position = $NodeInf.global_position
			joint.node_a = self.get_path()
			joint.node_b = body.get_path()
			joint.disable_collision = true

			gm.add_casteller(self, joint)
