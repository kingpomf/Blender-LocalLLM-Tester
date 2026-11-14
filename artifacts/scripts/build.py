"""Concatenate into worker code before the agent's construction body."""
import bpy
import math
from mathutils import Vector
DIM = dict(envelope=(1.20, 1.80, 1.05), wheelbase=1.10,
           front_track=.92, rear_track=.96, diameter=.34, wheel_width=.14)
VIEWS = ('perspective', 'front', 'side', 'rear')

def collection(name):
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(c)
    return c

def setup():
    s = bpy.context.scene
    s.unit_settings.system = 'METRIC'
    s.unit_settings.scale_length = 1
    collection('KART01_ASSET')
    collection('KART01_PRESENTATION')
    root = bpy.data.objects.get('Kart01_Root')
    if root is None:
        root = bpy.data.objects.new('Kart01_Root', None)
        collection('KART01_ASSET').objects.link(root)
    return root

def material(name, rgb, roughness=.5, metallic=0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    n = m.node_tree.nodes.get('Principled BSDF')
    n.inputs['Base Color'].default_value = (*rgb, 1)
    n.inputs['Roughness'].default_value = roughness
    n.inputs['Metallic'].default_value = metallic
    return m

def mesh(name, vertices, faces, mat, parent=None, presentation=False):
    if bpy.data.objects.get(name):
        raise ValueError('Object already exists: ' + name)
    data = bpy.data.meshes.new(name + '_Mesh')
    data.from_pydata(vertices, [], faces)
    data.update()
    obj = bpy.data.objects.new(name, data)
    collection('KART01_PRESENTATION' if presentation else 'KART01_ASSET').objects.link(obj)
    if mat:
        data.materials.append(mat)
    obj.parent = parent
    return obj

def box(name, center, size, mat, parent=None, bevel=0, presentation=False):
    verts = [(x*size[0]/2, y*size[1]/2, z*size[2]/2)
             for x,y,z in [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),
                           (1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]]
    obj = mesh(name, verts, [(0,4,6,2),(1,3,7,5),(0,1,5,4),
                            (2,6,7,3),(0,2,3,1),(4,5,7,6)], mat, parent, presentation)
    obj.location = center
    if bevel:
        mod = obj.modifiers.new('EdgeBevel','BEVEL')
        mod.width = bevel
        mod.segments = 1
    return obj

def tube(name, start, end, radius, mat, parent=None, segments=12):
    """Closed cylinder between endpoints; local X is its longitudinal axis."""
    a,b = Vector(start),Vector(end)
    length = (b-a).length
    if length <= 0 or segments < 3:
        raise ValueError('Tube requires length and at least three segments')
    verts = [(x, radius*math.cos(2*math.pi*i/segments), radius*math.sin(2*math.pi*i/segments))
             for x in (-length/2,length/2) for i in range(segments)]
    faces = [tuple(reversed(range(segments))),tuple(range(segments,2*segments))]
    faces += [(i,(i+1)%segments,(i+1)%segments+segments,i+segments) for i in range(segments)]
    obj = mesh(name,verts,faces,mat,parent)
    obj.location = (a+b)/2
    obj.rotation_euler = (b-a).to_track_quat('X','Z').to_euler()
    return obj

def wheel_center(front, left):
    track = DIM['front_track' if front else 'rear_track']
    return ((-1 if left else 1)*track/2,
            (-1 if front else 1)*DIM['wheelbase']/2, DIM['diameter']/2)

# ---------------- build body (authored by qwen38-flash-next) ----------------

root = setup()

red = material('MAT_Kart_Red', (0xC6/255, 0x28/255, 0x28/255), .45)
rubber = material('MAT_Rubber_Dark', (0x17/255, 0x17/255, 0x17/255), .8)
rim = material('MAT_Rim_Silver', (.75, .75, .78), .35, .9)
metal = material('MAT_Metal_Dark', (.16, .16, .18), .5, .8)
seatm = material('MAT_Seat_Black', (.06, .06, .06), .7)

def box_shells(name, shells, mat, parent, bevel=0):
    """One mesh containing multiple closed box shells."""
    if bpy.data.objects.get(name):
        raise ValueError('Object already exists: ' + name)
    verts, faces = [], []
    for center, size in shells:
        base = len(verts)
        verts += [(center[0]+x*size[0]/2, center[1]+y*size[1]/2, center[2]+z*size[2]/2)
                  for x,y,z in [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),
                                (1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]]
        faces += [tuple(base+i for i in idx) for idx in
                  [(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)]]
    data = bpy.data.meshes.new(name + '_Mesh')
    data.from_pydata(verts, [], faces)
    data.update()
    obj = bpy.data.objects.new(name, data)
    collection('KART01_ASSET').objects.link(obj)
    data.materials.append(mat)
    obj.parent = parent
    if bevel:
        mod = obj.modifiers.new('EdgeBevel', 'BEVEL')
        mod.width = bevel
        mod.segments = 1
    return obj

# Chassis tub: bottom exactly .17 m, top .44 m.
box('Kart01_Chassis', (0, .06, .305), (.62, 1.44, .27), red, parent=root, bevel=.018)
# Floor deck sits on the chassis top for feet/pedals.
box('Kart01_Floor', (0, -.24, .45), (.50, .82, .04), red, parent=root, bevel=.005)

# Tapered nose: front bumper narrows and drops toward the front tip.
def tapered_bumper(name):
    verts = [(-.28,-.66,.21),(.28,-.66,.21),(.28,-.66,.43),(-.28,-.66,.43),
             (-.19,-.895,.25),(.19,-.895,.25),(.19,-.895,.38),(-.19,-.895,.38)]
    obj = mesh(name, verts, [(0,1,2,3),(4,7,6,5),(1,2,6,5),(0,4,7,3),(3,7,6,2),(0,1,5,4)],
               red, parent=root)
    mod = obj.modifiers.new('EdgeBevel', 'BEVEL')
    mod.width = .012
    mod.segments = 1
    return obj

tapered_bumper('Kart01_Bumper_Front')
box('Kart01_Bumper_Rear', (0, .835, .30), (.56, .11, .20), red, parent=root, bevel=.012)

# Mirrored side pods: inboard face touches the chassis flank, clear of both wheel arcs.
box('Kart01_SidePod_L', (-.41, -.05, .36), (.20, .58, .24), red, parent=root, bevel=.015)
box('Kart01_SidePod_R', (.41, -.05, .36), (.20, .58, .24), red, parent=root, bevel=.015)

# Axles along local X at wheel-center height .17 m.
tube('Kart01_Axle_Front', (-.46, -.55, .17), (.46, -.55, .17), .035, metal, parent=root, segments=12)
tube('Kart01_Axle_Rear', (-.46, .55, .17), (.46, .55, .17), .035, metal, parent=root, segments=12)

def wheel(name, front, left):
    """One mesh: hollow tire band + two rim discs, slots [rubber, rim], spin axis local X."""
    S, h, R, ri, rr, rd = 12, .07, .17, .11, .105, .055
    verts, OL, OR, IL, IR, DL, DR = [], [], [], [], [], [], []
    for i in range(S):
        th = 2 * math.pi * i / S
        c, s = math.cos(th), math.sin(th)
        OL.append(len(verts)); verts.append((-h, R*c, R*s))
        OR.append(len(verts)); verts.append((h, R*c, R*s))
        IL.append(len(verts)); verts.append((-h, ri*c, ri*s))
        IR.append(len(verts)); verts.append((h, ri*c, ri*s))
        DL.append(len(verts)); verts.append((-rd, rr*c, rr*s))
        DR.append(len(verts)); verts.append((rd, rr*c, rr*s))
    faces = []
    for i in range(S):
        j = (i + 1) % S
        faces += [(OL[i], OL[j], OR[j], OR[i])]          # outer band
        faces += [(IL[i], IR[i], IR[j], IL[j])]          # inner band
        faces += [(OL[i], IL[i], IL[j], OL[j])]          # left annulus
        faces += [(OR[i], OR[j], IR[j], IR[i])]          # right annulus
    faces += [tuple(DR), tuple(reversed(DL))]            # rim discs
    n_tire = 4 * S
    if bpy.data.objects.get(name):
        raise ValueError('Object already exists: ' + name)
    data = bpy.data.meshes.new(name + '_Mesh')
    data.from_pydata(verts, [], faces)
    data.update()
    data.materials.append(rubber)
    data.materials.append(rim)
    for p in data.polygons:
        p.material_index = 1 if p.index >= n_tire else 0
    obj = bpy.data.objects.new(name, data)
    collection('KART01_ASSET').objects.link(obj)
    obj.parent = root
    obj.location = wheel_center(front, left)
    return obj

wheel('Kart01_Wheel_FL', True, True)
wheel('Kart01_Wheel_FR', True, False)
wheel('Kart01_Wheel_RL', False, True)
wheel('Kart01_Wheel_RR', False, False)

# Seat: base + back in one mesh, centered in the rear half.
box_shells('Kart01_Seat', [((0, .38, .465), (.42, .40, .07)),
                           ((0, .565, .685), (.42, .07, .51))], seatm, parent=root, bevel=.012)

# Steering column leans forward-up from the floor to the wheel hub.
tube('Kart01_SteeringColumn', (0, -.42, .47), (0, -.50, .79), .022, metal, parent=root, segments=10)

def steering_wheel(name):
    """Ring + three spokes in one mesh; local X is the ring axis."""
    S, R, ri, hw = 16, .13, .09, .0125
    verts, B, T, b, t = [], [], [], [], []
    for i in range(S):
        th = 2 * math.pi * i / S
        c, s = math.cos(th), math.sin(th)
        B.append(len(verts)); verts.append((-hw, R*c, R*s))
        T.append(len(verts)); verts.append((hw, R*c, R*s))
        b.append(len(verts)); verts.append((-hw, ri*c, ri*s))
        t.append(len(verts)); verts.append((hw, ri*c, ri*s))
    faces = []
    for i in range(S):
        j = (i + 1) % S
        faces += [(B[i], B[j], T[j], T[i])]
        faces += [(b[i], t[i], t[j], b[j])]
        faces += [(B[i], b[i], b[j], B[j])]
        faces += [(T[i], T[j], t[j], t[i])]
    for k in range(3):
        alpha = 2 * math.pi * k / 3 + math.pi / 2
        ca, sa = math.cos(alpha), math.sin(alpha)
        base = len(verts)
        for x, tt, u in [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),
                         (1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]:
            T_, U_ = .051 + tt * .0485, u * .008
            verts.append((x * hw, T_*ca - U_*sa, T_*sa + U_*ca))
        faces += [tuple(base+i for i in idx) for idx in
                  [(0,4,6,2),(1,3,7,5),(0,1,5,4),(2,6,7,3),(0,2,3,1),(4,5,7,6)]]
    if bpy.data.objects.get(name):
        raise ValueError('Object already exists: ' + name)
    data = bpy.data.meshes.new(name + '_Mesh')
    data.from_pydata(verts, [], faces)
    data.update()
    obj = bpy.data.objects.new(name, data)
    collection('KART01_ASSET').objects.link(obj)
    data.materials.append(seatm)
    obj.parent = root
    obj.location = (0, -.50, .78)
    obj.rotation_euler = Vector((0, -.94, .34)).to_track_quat('X', 'Z').to_euler()
    return obj

steering_wheel('Kart01_SteeringWheel')

# Pedals ahead of the seat, resting on the floor deck.
box('Kart01_Pedal_L', (-.13, -.40, .48), (.09, .14, .02), metal, parent=root, bevel=.003)
box('Kart01_Pedal_R', (.13, -.40, .48), (.09, .14, .02), metal, parent=root, bevel=.003)

asset = [o for o in bpy.data.objects if o.name.startswith('Kart01_') and o.name != 'Kart01_Root']
missing = [s for s in ('Chassis','Floor','Bumper_Front','Bumper_Rear','SidePod_L','SidePod_R',
         'Axle_Front','Axle_Rear','Wheel_FL','Wheel_FR','Wheel_RL','Wheel_RR','Seat',
         'SteeringColumn','SteeringWheel','Pedal_L','Pedal_R') if not bpy.data.objects.get('Kart01_'+s)]
report = dict(builder='qwen38-flash-next',
              root='Kart01_Root',
              asset_meshes=sorted(o.name for o in asset),
              missing_parts=missing,
              wheels_multi_slot=[o.name for o in asset
                                 if o.name.startswith('Kart01_Wheel_') and len(o.data.materials)==2],
              materials=sorted(m.name for m in bpy.data.materials))
