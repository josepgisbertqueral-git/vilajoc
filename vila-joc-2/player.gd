extends RigidBody2D

@export var speed = 400
@export var port = 4242

var server := PacketPeerUDP.new()
var last_direction = 0
var last_squat = false

func _ready() -> void:
	gravity_scale = 0.0
	# Intentem escoltar al port 4242 en totes les interfícies de xarxa
	var err = server.bind(port)
	if err == OK:
		print("Escoltant UDP al port: ", port)
	else:
		print("Error en binding del port UDP")

func _process(_delta: float) -> void:
	# Comprovem si han arribat paquets nous
	while server.get_available_packet_count() > 0:
		var packet = server.get_packet()
		var data_string = packet.get_string_from_utf8()
		_handle_udp_data(data_string)

func _handle_udp_data(json_str: String):
	var json = JSON.new()
	var error = json.parse(json_str)
	
	if error == OK:
		var data = json.data # Això serà un Array segons el teu codi Python
		if data.size() > 0:
			# Agafem la informació de la primera persona (id 0)
			var person = data[0]
			
			# Gestió de la Direcció
			match person.get("direction"):
				"RIGHT":
					last_direction = 1
				"LEFT":
					last_direction = -1
				"—":
					last_direction = 0
			
			# Gestió del Salt (Squat)
			var is_squatting = person.get("squat", false)
			# Si detectem un canvi: de NO ajupit a AJUPIT, saltem
			if is_squatting and not last_squat:
				_jump()
			
			last_squat = is_squatting
	else:
		print("Error parsejant JSON de Python")

func _jump():
	gravity_scale = 1.0
	linear_velocity.y = -400 # Impuls cap amunt
	print("Salt detectat per moviment!")

func _physics_process(_delta: float) -> void:
	# Apliquem la velocitat lateral basada en l'última dada rebuda per UDP
	linear_velocity.x = last_direction * speed
