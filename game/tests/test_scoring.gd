extends SceneTree

## Headless scoring checks:  godot --headless --path game -s tests/test_scoring.gd

var _failures := 0


func _init() -> void:
	_perfect_game()
	_all_gutter()
	_strike_bonus()
	_spare_bonus()
	_open_frames()
	_tenth_frame_bonus()
	if _failures == 0:
		print("ALL SCORING TESTS PASSED")
	else:
		print("%d SCORING TEST(S) FAILED" % _failures)
	quit(1 if _failures > 0 else 0)


func _check(label: String, got, want) -> void:
	if got != want:
		_failures += 1
		printerr("FAIL %s: got %s, want %s" % [label, str(got), str(want)])
	else:
		print("ok   %s" % label)


func _perfect_game() -> void:
	var s := BowlingScoring.new()
	for i in range(12):
		s.add_roll(10)
	_check("perfect total", s.total(), 300)
	_check("perfect over", s.is_game_over(), true)


func _all_gutter() -> void:
	var s := BowlingScoring.new()
	for i in range(20):
		s.add_roll(0)
	_check("gutter total", s.total(), 0)
	_check("gutter over", s.is_game_over(), true)


func _strike_bonus() -> void:
	var s := BowlingScoring.new()
	s.add_roll(10)  # frame 1 strike
	s.add_roll(7)
	s.add_roll(2)   # frame 2 = 9
	var t := s.frame_totals()
	_check("strike frame1", t[0], 19)   # 10 + 7 + 2
	_check("strike frame2", t[1], 28)   # 19 + 9


func _spare_bonus() -> void:
	var s := BowlingScoring.new()
	s.add_roll(7)
	s.add_roll(3)   # frame 1 spare
	s.add_roll(4)   # frame 2 first ball
	s.add_roll(5)   # frame 2 = 9
	var t := s.frame_totals()
	_check("spare frame1", t[0], 14)    # 10 + 4
	_check("spare frame2", t[1], 23)    # 14 + 9


func _open_frames() -> void:
	var s := BowlingScoring.new()
	s.add_roll(3)
	s.add_roll(4)   # frame 1 = 7
	s.add_roll(2)
	s.add_roll(1)   # frame 2 = 3
	var t := s.frame_totals()
	_check("open frame1", t[0], 7)
	_check("open frame2", t[1], 10)


func _tenth_frame_bonus() -> void:
	var s := BowlingScoring.new()
	for i in range(9):
		s.add_roll(0)
		s.add_roll(0)  # frames 1-9 all gutter
	s.add_roll(10)     # tenth strike
	s.add_roll(10)
	s.add_roll(10)     # three strikes in tenth = 30
	_check("tenth total", s.total(), 30)
	_check("tenth over", s.is_game_over(), true)
