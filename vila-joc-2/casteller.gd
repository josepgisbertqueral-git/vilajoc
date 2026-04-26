extends RigidBody2D
class_name Casteller

@export var id = 0
@export var is_static := false

func _ready() -> void:
	if is_static:
		freeze_mode = RigidBody2D.FREEZE_MODE_STATIC
		freeze = true
	
func _physics_process(delta):
	pass
