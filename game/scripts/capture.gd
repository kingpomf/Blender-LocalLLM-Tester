extends Node

## Dev-only hero-shot capture. Run windowed (not --headless):
##   CAPTURE_OUT=/abs/path.png godot --path game res://scenes/Capture.tscn

var _out := ""


func _ready() -> void:
	_out = OS.get_environment("CAPTURE_OUT")
	if _out.is_empty():
		_out = "user://bowling_capture.png"
	var main := (load("res://scenes/Main.tscn") as PackedScene).instantiate()
	add_child(main)
	await get_tree().process_frame
	var cam := _find_cam(main)
	if cam != null:
		var lane_x: float = main.get("lane_center_x")
		var start_z: float = main.get("ball_start").origin.z
		var head_z: float = main.get("head_pin_z")
		cam.look_at_from_position(
			Vector3(lane_x + 2.6, 2.6, start_z + 0.6),
			Vector3(lane_x, 0.5, head_z),
			Vector3.UP)
	for _i in range(40):
		await get_tree().process_frame
	var img := get_viewport().get_texture().get_image()
	var err := img.save_png(_out)
	print("capture saved=%s err=%d path=%s" % [str(err == OK), err, _out])
	get_tree().quit()


func _find_cam(node: Node) -> Camera3D:
	if node is Camera3D:
		return node as Camera3D
	for c in node.get_children():
		var r := _find_cam(c)
		if r != null:
			return r
	return null
