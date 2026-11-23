extends Node3D

## Single-lane bowling demo built on the BowlingPair01 GLB asset.
##
## The left lane's pins are read from the imported asset at runtime (so the
## glTF Y-up conversion is handled for us), replaced with dynamic RigidBody3D
## pins, and bowled at with an aim + charge control. Scoring follows standard
## ten-pin rules via BowlingScoring.

const PIN_SCENE := preload("res://scenes/Pin.tscn")
const BALL_SCENE := preload("res://scenes/Ball.tscn")
const ALLEY_PATH := "res://assets/models/BowlingPair01.glb"
const LEFT_PIN_COUNT := 10

const MIN_SPEED := 4.5
const MAX_SPEED := 9.0
const MAX_AIM := 0.18          # radians of lateral aim
const CHARGE_RATE := 0.9       # power units per second
const ROLL_TIMEOUT := 8.0
const SETTLE_TIMEOUT := 3.0

enum State { AIMING, CHARGING, ROLLING, SETTLING, RESOLVING }

@onready var alley: Node3D = $Alley
@onready var pins_root: Node3D = $Pins
@onready var ball_spawn: Node3D = $BallSpawn
@onready var camera: Camera3D = $Camera3D
@onready var light: DirectionalLight3D = $DirectionalLight3D
@onready var hud: CanvasLayer = $HUD

var scoring := BowlingScoring.new()
var pins: Array[RigidBody3D] = []
var ball: RigidBody3D = null
var aim_indicator: MeshInstance3D = null

var state: State = State.AIMING
var aim_angle := 0.0
var power := 0.0
var charge_dir := 1.0
var settle_timer := 0.0

var frame := 1
var ball_number := 1
var standing_before_ball := 10
var _rolls_at_frame_start := 0

var lane_center_x := 0.0
var head_pin_z := 0.0
var ball_start := Transform3D.IDENTITY

var lbl_frame: Label
var lbl_score: Label
var lbl_msg: Label
var lbl_power: Label


func _ready() -> void:
	_register_input()
	_setup_environment()
	_build_alley()
	_build_lane_collider()
	_spawn_pins()
	_spawn_ball()
	_setup_camera()
	_build_hud()
	_start_frame(1)


# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

func _register_input() -> void:
	_add_key("aim_left", KEY_LEFT)
	_add_key("aim_right", KEY_RIGHT)
	_add_key("charge", KEY_SPACE)
	_add_key("reset_frame", KEY_R)
	_add_key("reset_game", KEY_N)


func _add_key(action: String, keycode: Key) -> void:
	if not InputMap.has_action(action):
		InputMap.add_action(action)
	var ev := InputEventKey.new()
	ev.physical_keycode = keycode
	InputMap.action_add_event(action, ev)


func _setup_environment() -> void:
	light.rotation_degrees = Vector3(-52.0, -28.0, 0.0)
	light.light_energy = 1.25
	var sky_mat := ProceduralSkyMaterial.new()
	var sky := Sky.new()
	sky.sky_material = sky_mat
	var env := Environment.new()
	env.sky = sky
	env.background_mode = Environment.BG_SKY
	env.ambient_light_source = Environment.AMBIENT_SOURCE_SKY
	var we := WorldEnvironment.new()
	we.environment = env
	add_child(we)


func _build_alley() -> void:
	var packed := load(ALLEY_PATH) as PackedScene
	var instance := packed.instantiate()
	alley.add_child(instance)
	# Hide the asset's own left pins and balls; we drive dynamic copies instead.
	for i in range(1, LEFT_PIN_COUNT + 1):
		var p := _find(instance, "Pin_L_%02d" % i) as GeometryInstance3D
		if p:
			p.visible = false
	for i in range(1, 4):
		var b := _find(instance, "Ball_0%d" % i) as GeometryInstance3D
		if b:
			b.visible = false


func _collect_pin_homes() -> Array[Transform3D]:
	var homes: Array[Transform3D] = []
	for i in range(1, LEFT_PIN_COUNT + 1):
		var p := _find(alley.get_child(0), "Pin_L_%02d" % i) as Node3D
		if p:
			homes.append(p.global_transform)
	return homes


func _build_lane_collider() -> void:
	var homes := _collect_pin_homes()
	if homes.is_empty():
		push_warning("No left-lane pins found in the imported alley.")
		return
	var sum_x := 0.0
	var head := homes[0]
	for h in homes:
		sum_x += h.origin.x
		if h.origin.z > head.origin.z:  # closest to camera = head pin
			head = h
	lane_center_x = sum_x / homes.size()
	head_pin_z = head.origin.z

	var start_z := head_pin_z + 18.0
	ball_start = Transform3D(Basis.IDENTITY, Vector3(lane_center_x, 0.108, start_z))

	var z_near := start_z + 2.0
	var z_far := head_pin_z - 2.5
	var length := z_near - z_far
	var mid_z := (z_near + z_far) * 0.5

	var body := StaticBody3D.new()
	body.name = "LaneCollider"
	_add_box(body, Vector3(1.7, 0.2, length), Vector3(lane_center_x, -0.1, mid_z))
	_add_box(body, Vector3(0.12, 0.35, length), Vector3(lane_center_x - 0.56, 0.12, mid_z))
	_add_box(body, Vector3(0.12, 0.35, length), Vector3(lane_center_x + 0.56, 0.12, mid_z))
	add_child(body)


func _add_box(parent: Node, size: Vector3, center: Vector3) -> void:
	var cs := CollisionShape3D.new()
	var box := BoxShape3D.new()
	box.size = size
	cs.shape = box
	cs.position = center
	parent.add_child(cs)


func _spawn_pins() -> void:
	for h in _collect_pin_homes():
		var p := PIN_SCENE.instantiate() as RigidBody3D
		pins_root.add_child(p)
		p.setup(h)
		pins.append(p)


func _spawn_ball() -> void:
	ball = BALL_SCENE.instantiate() as RigidBody3D
	ball_spawn.add_child(ball)
	ball.reset_to(ball_start)
	# Aim indicator: a thin bar in front of the ball showing launch direction.
	aim_indicator = MeshInstance3D.new()
	var mesh := BoxMesh.new()
	mesh.size = Vector3(0.03, 0.01, 3.0)
	aim_indicator.mesh = mesh
	var mat := StandardMaterial3D.new()
	mat.albedo_color = Color(0.2, 0.9, 1.0, 0.7)
	mat.emission_enabled = true
	mat.emission = Color(0.2, 0.9, 1.0)
	aim_indicator.material_override = mat
	add_child(aim_indicator)


func _setup_camera() -> void:
	camera.position = Vector3(lane_center_x, 1.7, ball_start.origin.z + 3.2)
	camera.look_at(Vector3(lane_center_x, 0.25, head_pin_z))


func _build_hud() -> void:
	lbl_frame = _make_label("", Vector2(20, 14), 26)
	lbl_score = _make_label("", Vector2(1010, 14), 26)
	lbl_msg = _make_label("", Vector2(0, 60), 44, Color(1, 0.9, 0.4))
	lbl_msg.set_anchors_preset(Control.PRESET_CENTER_TOP)
	lbl_msg.offset_left = -320
	lbl_msg.offset_right = 320
	lbl_msg.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	lbl_power = _make_label("", Vector2(20, 676), 24)


func _make_label(text: String, pos: Vector2, size: int, color := Color.WHITE) -> Label:
	var l := Label.new()
	l.text = text
	l.position = pos
	l.add_theme_font_size_override("font_size", size)
	l.add_theme_color_override("font_color", color)
	hud.add_child(l)
	return l


# ---------------------------------------------------------------------------
# Frame / ball flow
# ---------------------------------------------------------------------------

func _start_frame(f: int) -> void:
	frame = f
	ball_number = 1
	standing_before_ball = LEFT_PIN_COUNT
	_rolls_at_frame_start = scoring.rolls.size()
	_rack_new_pins()
	_ready_ball()
	_update_hud()


func _advance_frame() -> void:
	if frame >= 10:
		_game_over()
		return
	_start_frame(frame + 1)


func _ready_ball() -> void:
	ball.reset_to(ball_start)
	aim_angle = 0.0
	power = 0.0
	charge_dir = 1.0
	state = State.AIMING
	aim_indicator.visible = true
	_update_hud()


func _rack_new_pins() -> void:
	for p in pins:
		p.reset_to_home()


func _sweep_fallen_pins() -> void:
	for p in pins:
		if not p.is_standing():
			p.visible = false
			p.freeze = true
			p.global_position = Vector3(p.global_position.x, -50.0, p.global_position.z)


func _game_over() -> void:
	state = State.RESOLVING
	aim_indicator.visible = false
	lbl_msg.text = "Game over!  Final score: %d   (N = new game)" % scoring.total()


# ---------------------------------------------------------------------------
# Input + per-frame logic
# ---------------------------------------------------------------------------

func _process(delta: float) -> void:
	_handle_global_input()
	match state:
		State.AIMING:
			aim_angle = clampf(
				aim_angle + Input.get_axis("aim_left", "aim_right") * delta * 0.7,
				-MAX_AIM, MAX_AIM)
			_update_aim_indicator()
			if Input.is_action_just_pressed("charge"):
				state = State.CHARGING
				power = 0.0
				charge_dir = 1.0
		State.CHARGING:
			power += charge_dir * delta * CHARGE_RATE
			if power >= 1.0:
				power = 1.0
				charge_dir = -1.0
			elif power <= 0.0:
				power = 0.0
				charge_dir = 1.0
			_update_power()
			if Input.is_action_just_released("charge"):
				_launch()
		State.ROLLING:
			settle_timer += delta
			if ball.is_settled() or ball.global_position.z < head_pin_z - 2.5 \
					or settle_timer > ROLL_TIMEOUT:
				state = State.SETTLING
				settle_timer = 0.0
		State.SETTLING:
			settle_timer += delta
			if _all_pins_settled() or settle_timer > SETTLE_TIMEOUT:
				state = State.RESOLVING
				_resolve_roll()
		State.RESOLVING:
			pass


func _handle_global_input() -> void:
	if Input.is_action_just_pressed("reset_game"):
		scoring.reset()
		_start_frame(1)
	elif Input.is_action_just_pressed("reset_frame") and state != State.ROLLING \
			and state != State.SETTLING:
		# Rewind scoring to the start of this frame and re-rack.
		while scoring.rolls.size() > _rolls_at_frame_start:
			scoring.rolls.pop_back()
		_start_frame(frame)


func _launch() -> void:
	var dir := Vector3(sin(aim_angle), 0.0, -cos(aim_angle))
	var speed := lerpf(MIN_SPEED, MAX_SPEED, power)
	aim_indicator.visible = false
	ball.launch(dir, speed)
	state = State.ROLLING
	settle_timer = 0.0


func _all_pins_settled() -> bool:
	for p in pins:
		if not p.visible:
			continue
		if p.linear_velocity.length() > 0.1 or p.angular_velocity.length() > 0.5:
			return false
	return true


func _count_standing() -> int:
	var n := 0
	for p in pins:
		if p.visible and p.is_standing():
			n += 1
	return n


func _resolve_roll() -> void:
	var standing_now := _count_standing()
	var knocked := standing_before_ball - standing_now
	scoring.add_roll(knocked)
	_show_result(knocked, standing_now)

	if frame < 10:
		if ball_number == 1 and knocked == LEFT_PIN_COUNT:
			_advance_frame()
		elif ball_number == 1:
			ball_number = 2
			standing_before_ball = standing_now
			_sweep_fallen_pins()
			_ready_ball()
		else:
			_advance_frame()
		_update_hud()
		return

	# Tenth frame: bonus balls for a strike or spare.
	if ball_number == 1:
		if knocked == LEFT_PIN_COUNT:
			ball_number = 2
			_rack_new_pins()
			standing_before_ball = LEFT_PIN_COUNT
		else:
			ball_number = 2
			standing_before_ball = standing_now
			_sweep_fallen_pins()
		_ready_ball()
	elif ball_number == 2:
		var first := scoring.rolls[scoring.rolls.size() - 2]
		var bonus := first == LEFT_PIN_COUNT or first + knocked == LEFT_PIN_COUNT
		if not bonus:
			_update_hud()
			_game_over()
			return
		ball_number = 3
		if first == LEFT_PIN_COUNT and knocked < LEFT_PIN_COUNT:
			standing_before_ball = standing_now
			_sweep_fallen_pins()
		else:
			_rack_new_pins()
			standing_before_ball = LEFT_PIN_COUNT
		_ready_ball()
	else:
		_update_hud()
		_game_over()
	_update_hud()


func _show_result(knocked: int, standing_now: int) -> void:
	if knocked == LEFT_PIN_COUNT and ball_number == 1:
		lbl_msg.text = "Strike!"
	elif standing_now == 0 and ball_number == 2:
		lbl_msg.text = "Spare!"
	elif knocked == 0:
		lbl_msg.text = "Gutter / miss"
	else:
		lbl_msg.text = "%d down" % knocked


func _update_hud() -> void:
	lbl_frame.text = "Frame %d   Ball %d" % [frame, ball_number]
	lbl_score.text = "Score  %d" % scoring.total()


func _update_aim_indicator() -> void:
	if aim_indicator == null:
		return
	aim_indicator.position = Vector3(lane_center_x, 0.02, ball_start.origin.z - 1.6)
	aim_indicator.rotation = Vector3(0.0, -aim_angle, 0.0)


func _update_power() -> void:
	lbl_power.text = "Power  %d%%" % int(round(power * 100.0))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

func _find(node: Node, name: String) -> Node:
	if node.name == name:
		return node
	for c in node.get_children():
		var r := _find(c, name)
		if r != null:
			return r
	return null
