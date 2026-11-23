class_name BowlingScoring
extends RefCounted

## Standard ten-pin bowling scoring.
## Feed every ball's knocked-pin count with add_roll(); read cumulative
## per-frame totals with frame_totals(). Frames whose bonus rolls have not
## been thrown yet report null (not yet scorable).

const FRAMES := 10

var rolls: Array[int] = []


func reset() -> void:
	rolls.clear()


func add_roll(pins: int) -> void:
	rolls.append(clampi(pins, 0, 10))


## Cumulative score after each frame. Index 0..9. null = not yet scorable.
func frame_totals() -> Array:
	var totals: Array = []
	var i := 0
	var cumulative := 0
	for f in range(FRAMES):
		if i >= rolls.size():
			totals.append(null)
			continue
		if f < FRAMES - 1:
			if rolls[i] == 10:  # strike
				if i + 2 < rolls.size():
					cumulative += 10 + rolls[i + 1] + rolls[i + 2]
					totals.append(cumulative)
				else:
					totals.append(null)
				i += 1
			elif i + 1 < rolls.size():
				var sum := rolls[i] + rolls[i + 1]
				if sum == 10:  # spare
					if i + 2 < rolls.size():
						cumulative += 10 + rolls[i + 2]
						totals.append(cumulative)
					else:
						totals.append(null)
				else:
					cumulative += sum
					totals.append(cumulative)
				i += 2
			else:
				totals.append(null)
				i += 1
		else:  # tenth frame: all remaining rolls belong to it
			if _tenth_complete(i):
				var s := 0
				for k in range(i, rolls.size()):
					s += rolls[k]
				cumulative += s
				totals.append(cumulative)
			else:
				totals.append(null)
			i = rolls.size()
	return totals


func total() -> int:
	var t := frame_totals()
	for k in range(t.size() - 1, -1, -1):
		if t[k] != null:
			return t[k]
	return 0


func is_game_over() -> bool:
	var t := frame_totals()
	return t.size() == FRAMES and t[FRAMES - 1] != null


func _tenth_complete(i: int) -> bool:
	var n := rolls.size() - i
	if n >= 3:
		return true
	if n == 2:
		if rolls[i] == 10:
			return false  # strike earns two bonus rolls
		if rolls[i] + rolls[i + 1] == 10:
			return false  # spare earns one bonus roll
		return true  # open frame
	return false
