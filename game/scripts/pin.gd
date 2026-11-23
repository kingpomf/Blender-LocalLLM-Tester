extends RigidBody3D

## One dynamic bowling pin. The controller places it at a home transform read
## from the imported asset, then watches for it tipping over.

const DOWN_TILT_COS := 0.5      # ~60 deg from upright counts as knocked down
const MAX_SLIDE := 1.2          # metres from home before a pin is "dead"

var standing := true
var _home := Transform3D.IDENTITY


func setup(home: Transform3D) -> void:
	_home = home
	reset_to_home()


func reset_to_home() -> void:
	visible = true
	freeze = false
	global_transform = _home
	linear_velocity = Vector3.ZERO
	angular_velocity = Vector3.ZERO
	standing = true


func is_standing() -> bool:
	return standing


func _physics_process(_delta: float) -> void:
	if not standing:
		return
	var up := global_transform.basis.y
	if up.dot(Vector3.UP) < DOWN_TILT_COS:
		standing = false
	elif global_position.distance_to(_home.origin) > MAX_SLIDE:
		standing = false
