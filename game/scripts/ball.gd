extends RigidBody3D

## The bowling ball. Held frozen at the start position until launched, then it
## rolls down the lane. The controller reads is_settled() to end the roll.

var launched := false


func reset_to(transform: Transform3D) -> void:
	global_transform = transform
	linear_velocity = Vector3.ZERO
	angular_velocity = Vector3.ZERO
	launched = false
	freeze = true


func launch(direction: Vector3, speed: float, spin: float = 0.0) -> void:
	freeze = false
	launched = true
	linear_velocity = direction.normalized() * speed
	angular_velocity = Vector3(0.0, spin, 0.0)


func is_settled() -> bool:
	return launched and not freeze \
		and linear_velocity.length() < 0.2 \
		and angular_velocity.length() < 1.0
