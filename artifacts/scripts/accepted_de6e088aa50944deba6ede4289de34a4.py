import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector

ROOT_NAME = "BowlingPair01_ROOT"
PRES = "BP01_PRESENTATION"

OVERVIEW_POS = (0.0, -20.0, 24.0)
OVERVIEW_TARGET = (0.0, 7.0, 0.5)
PLAYER_POS = (-0.95, -3.20, 1.55)
PLAYER_TARGET = (-0.95, 19.20, 0.0)
PINDECK_POS = (0.0, 9.00, 4.20)
PINDECK_TARGET = (0.0, 18.75, 0.15)
PROPS_POS = (0.75, -0.55, 1.40)
PROPS_TARGET = (0.0, -2.70, 0.58)


def obj_bounds(ob):
    mw = ob.matrix_world
    xs, ys, zs = [], [], []
    for v in ob.data.vertices:
        w = mw @ v.co
        xs.append(w.x)
        ys.append(w.y)
        zs.append(w.z)
    return (min(xs), max(xs), min(ys), max(ys), min(zs), max(zs))


def corner_set(b):
    return [Vector((x, y, z))
            for x in (b[0], b[1]) for y in (b[2], b[3]) for z in (b[4], b[5])]


def min_fraction(scene, cam, points):
    worst = 1.0
    for p in points:
        co = world_to_camera_view(scene, cam, p)
        inside = co.z > 0.0 and 0.0 <= co.x <= 1.0 and 0.0 <= co.y <= 1.0
        if not inside:
            return -1.0
        margin = min(co.x, 1.0 - co.x, co.y, 1.0 - co.y)
        worst = min(worst, margin)
    return worst


def visual_names():
    names = []
    for cname in ("BP01_STATIC", "BP01_PINS", "BP01_BALLS"):
        for ob in bpy.data.collections[cname].objects:
            if ob.type == 'MESH':
                names.append(ob.name)
    return names


def make_camera(scene, coll, name, pos, target):
    cd = bpy.data.cameras.new(name)
    cd.clip_start = 0.01
    cd.clip_end = 400.0
    cam = bpy.data.objects.new(name, cd)
    cam.location = pos
    direction = Vector(target) - Vector(pos)
    cam.rotation_euler = direction.to_track_quat('Z', 'Y').to_euler()
    coll.objects.link(cam)
    return cam


def fit_perspective(scene, cam, points, max_lens):
    lens = max_lens
    while lens >= 15.0 - 1e-9:
        cam.data.lens = lens
        margin = min_fraction(scene, cam, points)
        if margin > 0.004:
            return round(lens, 3), round(margin, 4)
        lens -= 1.0
    cam.data.lens = 15.0
    return None, round(min_fraction(scene, cam, points), 4)


def fit_ortho(scene, cam, points):
    scale = 10.0
    while scale <= 80.0 + 1e-9:
        cam.data.type = 'ORTHO'
        cam.data.ortho_scale = scale
        margin = min_fraction(scene, cam, points)
        if margin > 0.004:
            return round(scale, 3), round(margin, 4)
        scale += 1.0
    return None, round(min_fraction(scene, cam, points), 4)


def add_light(coll, name, kind, location, target, energy, size=1.0):
    ld = bpy.data.lights.new(name, kind)
    setattr(ld, "energy", energy)
    if kind == 'AREA':
        setattr(ld, "size", size)
    ob = bpy.data.objects.new(name, ld)
    ob.location = location
    direction = Vector(target) - Vector(location)
    ob.rotation_euler = direction.to_track_quat('Z', 'Y').to_euler()
    coll.objects.link(ob)
    return ob


def run():
    scene = bpy.context.scene
    root = bpy.data.objects[ROOT_NAME]
    pres = bpy.data.collections[PRES]

    world = scene.world or bpy.data.worlds.new("BP01_World")
    scene.world = world
    world.use_nodes = True
    wnt = world.node_tree
    if wnt is not None:
        bg = wnt.nodes.get("Background")
        if bg is not None:
            bg.inputs[0].default_value = (0.05, 0.055, 0.065, 1.0)  # type: ignore[attr-defined]
            bg.inputs[1].default_value = 0.55  # type: ignore[attr-defined]

    targets = {
        "Overview": [obj_bounds(bpy.data.objects[n]) for n in visual_names()],
        "Player": [obj_bounds(bpy.data.objects["Lane_L_Surface"])],
        "PinDeck": [obj_bounds(bpy.data.objects["Pin_%s_%02d" % (s, i)])
                    for s in ("L", "R") for i in range(1, 11)],
        "Props": [obj_bounds(bpy.data.objects["Ball_0%d" % i]) for i in (1, 2, 3)],
    }
    points = {}
    for role, boxes in targets.items():
        pts = []
        for b in boxes:
            pts.extend(corner_set(b))
        points[role] = pts

    specs = {
        "Overview": (OVERVIEW_POS, OVERVIEW_TARGET, "ortho"),
        "Player": (PLAYER_POS, PLAYER_TARGET, "persp"),
        "PinDeck": (PINDECK_POS, PINDECK_TARGET, "persp"),
        "Props": (PROPS_POS, PROPS_TARGET, "persp"),
    }
    caps = {"Player": 30.0, "PinDeck": 40.0, "Props": 45.0}

    report = {}
    for role, (pos, tgt, kind) in specs.items():
        name = "CAM_BowlingPair01_" + role
        existing = bpy.data.objects.get(name)
        if existing is not None:
            bpy.data.objects.remove(existing, do_unlink=True)
        cam = make_camera(scene, pres, name, pos, tgt)
        if kind == "ortho":
            value, margin = fit_ortho(scene, cam, points[role])
        else:
            value, margin = fit_perspective(scene, cam, points[role], caps[role])
        if value is None:
            raise ValueError("%s framing failed, margin=%s" % (role, margin))
        report[role] = {
            "camera": name,
            "type": ("ORTHO" if kind == "ortho" else "PERSP"),
            "lens_or_ortho_scale": value,
            "corner_margin_min": margin,
            "position": [round(v, 3) for v in cam.location],
            "rotation_euler": [round(v, 4) for v in cam.rotation_euler],
            "parent": cam.parent.name if cam.parent else None,
            "corner_count": len(points[role]),
        }

    lights = []
    lights.append(add_light(pres, "Light_Sun", 'SUN', (6.0, -6.0, 12.0), (0.0, 6.0, 0.0), 2.2))
    lights.append(add_light(pres, "Light_Approach_L", 'AREA', (-0.95, -2.0, 3.30),
                            (-0.95, -1.0, 0.0), 320.0, 2.2))
    lights.append(add_light(pres, "Light_Approach_R", 'AREA', (0.95, -2.0, 3.30),
                            (0.95, -1.0, 0.0), 320.0, 2.2))
    lights.append(add_light(pres, "Light_PinDeck", 'AREA', (0.0, 15.0, 3.60),
                            (0.0, 18.6, 0.2), 420.0, 3.0))
    lights.append(add_light(pres, "Light_Return", 'AREA', (0.0, -1.2, 2.40),
                            (0.0, -2.8, 0.6), 140.0, 1.2))

    report["lights"] = sorted(l.name for l in lights)
    report["presentation_objects"] = sorted(o.name for o in pres.objects)
    report["root_children"] = len(root.children)
    report["stage"] = "07"
    report["revision"] = "rev12-cameras-lights"
    return report


if __name__ == '__blender_author__':
    report = run()
