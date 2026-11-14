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

"""Requires helpers.py; installs only the named review rig."""
setup()
scene = bpy.context.scene
names = ['CAM_Kart01_'+v.title() for v in VIEWS] + ['LIGHT_Kart01_'+v for v in ('Key','Fill','Rim')] + ['Kart01_Ground']
for name in names:
    obj = bpy.data.objects.get(name)
    if obj:
        data = obj.data
        bpy.data.objects.remove(obj, do_unlink=True)
        if data and data.users == 0:
            if isinstance(data,bpy.types.Mesh): bpy.data.meshes.remove(data)
            elif isinstance(data,bpy.types.Camera): bpy.data.cameras.remove(data)
            elif isinstance(data,bpy.types.Light): bpy.data.lights.remove(data)
box('Kart01_Ground',(0,0,-.025),(200,200,.05),material('MAT_Ground',(.3,.3,.3)),presentation=True)
target = Vector((0,0,.45))
for view,pos in zip(VIEWS,[(2.8,-3.6,2.5),(0,-4,.45),(4,0,.45),(0,4,.45)]):
    name = 'CAM_Kart01_'+view.title()
    data = bpy.data.cameras.new(name)
    data.type='ORTHO'
    data.ortho_scale=2.5
    obj=bpy.data.objects.new(name,data)
    collection('KART01_PRESENTATION').objects.link(obj)
    obj.location=pos
    obj.rotation_euler=(target-obj.location).to_track_quat('-Z','Y').to_euler()
    frame=VIEWS.index(view)+1
    for marker in list(scene.timeline_markers):
        if marker.name == 'Kart01_'+view: scene.timeline_markers.remove(marker)
    marker=scene.timeline_markers.new('Kart01_'+view,frame=frame)
    marker.camera=obj
scene.camera=bpy.data.objects['CAM_Kart01_Perspective']
for label,pos,power in [('Key',(3,-4,5),900),('Fill',(-3,-2,3),500),('Rim',(0,4,4),700)]:
    name='LIGHT_Kart01_'+label
    data=bpy.data.lights.new(name,'AREA'); data.energy=power; data.shape='DISK'; data.size=4
    obj=bpy.data.objects.new(name,data); collection('KART01_PRESENTATION').objects.link(obj)
    obj.location=pos; obj.rotation_euler=(target-obj.location).to_track_quat('-Z','Y').to_euler()
scene.render.resolution_x=512; scene.render.resolution_y=512; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.frame_start=1; scene.frame_end=4; scene.frame_set(1)

"""Measurement only. Requires helpers.py. Worker success is not acceptance."""
import re
from bpy_extras.object_utils import world_to_camera_view
checks=[]
def check(name, actual, expected, ok):
    checks.append(dict(name=name,actual=actual,expected=expected,passed=bool(ok)))
def near(name,a,b,tol): check(name,a,dict(value=b,tolerance=tol),abs(a-b)<=tol)
required = ['Chassis','Floor','Bumper_Front','Bumper_Rear','SidePod_L','SidePod_R',
            'Axle_Front','Axle_Rear','Wheel_FL','Wheel_FR','Wheel_RL','Wheel_RR',
            'Seat','SteeringColumn','SteeringWheel','Pedal_L','Pedal_R']
root=bpy.data.objects.get('Kart01_Root')
check('root',root.type if root else None,'EMPTY',root is not None and root.type=='EMPTY')
def descendant(obj):
    parent=obj.parent
    while parent:
        if parent==root: return True
        parent=parent.parent
    return False
if root:
    near('root location',root.location.length,0,.001)
    near('root rotation',root.rotation_euler.to_quaternion().angle,0,.001)
    check('root scale',list(root.scale),[1,1,1],all(abs(v-1)<.001 for v in root.scale))
asset=[o for o in bpy.context.scene.objects if root and descendant(o)]
meshes=[o for o in asset if o.type=='MESH']
for suffix in required:
    obj=bpy.data.objects.get('Kart01_'+suffix)
    check('required '+suffix,obj.type if obj else None,'asset MESH',obj is not None and obj.type=='MESH' and obj in meshes)
check('four wheels',[o.name for o in meshes if o.name.startswith('Kart01_Wheel_')],4,
      len([o for o in meshes if o.name.startswith('Kart01_Wheel_')])==4)
points={}; triangles=0
deps=bpy.context.evaluated_depsgraph_get()
for obj in meshes:
    ev=obj.evaluated_get(deps); data=ev.to_mesh()
    try:
        data.calc_loop_triangles(); triangles+=len(data.loop_triangles)
        points[obj.name]=[ev.matrix_world@v.co for v in data.vertices]
    finally: ev.to_mesh_clear()
    check('scale '+obj.name,list(obj.scale),[1,1,1],all(abs(v-1)<.001 for v in obj.scale))
    check('material '+obj.name,[m.name if m else None for m in obj.data.materials], 'assigned materials on all faces',
          bool(obj.data.materials) and all(m for m in obj.data.materials) and all(f.material_index<len(obj.data.materials) for f in obj.data.polygons))
check('triangle budget',triangles,4500,0<triangles<=4500)
allpts=[v for ps in points.values() for v in ps]
if allpts:
    extent=[max(v[i] for v in allpts)-min(v[i] for v in allpts) for i in range(3)]
    check('envelope',extent,list(DIM['envelope']),all(a<=b+.00001 for a,b in zip(extent,DIM['envelope'])))
else: check('geometry',0,'nonempty',False)
centers={}
for suffix in ('FL','FR','RL','RR'):
    name='Kart01_Wheel_'+suffix; ps=points.get(name,[])
    if not ps: continue
    lo=[min(v[i] for v in ps) for i in range(3)]; hi=[max(v[i] for v in ps) for i in range(3)]
    centers[suffix]=[(a+b)/2 for a,b in zip(lo,hi)]
    near(name+' contact',lo[2],0,.01)
    for axis,target_dim in enumerate((DIM['wheel_width'],DIM['diameter'],DIM['diameter'])):
        near(name+' dimension '+str(axis),hi[axis]-lo[axis],target_dim,.01)
    axis=bpy.data.objects[name].matrix_world.to_3x3()@Vector((1,0,0))
    check(name+' spin axis',list(axis),'parallel world X',abs(axis.normalized().x)>.999)
if len(centers)==4:
    for a,b,target_dim in [('FL','FR',DIM['front_track']),('RL','RR',DIM['rear_track'])]:
        near(a+b+' track',abs(centers[a][0]-centers[b][0]),target_dim,.02)
        near(a+b+' symmetry',centers[a][0]+centers[b][0],0,.001)
        near(a+b+' alignment',centers[a][1]-centers[b][1],0,.001)
    for a,b in [('FL','RL'),('FR','RR')]: near(a+b+' wheelbase',centers[b][1]-centers[a][1],DIM['wheelbase'],.02)
for obj in bpy.context.scene.objects:
    check('name '+obj.name,obj.name,'no numeric suffix',re.search(r'\.\d{3}$',obj.name) is None)
    expected='KART01_ASSET' if obj==root or obj in asset else 'KART01_PRESENTATION'
    check('collection '+obj.name,[c.name for c in obj.users_collection],[expected],
          len(obj.users_collection)==1 and obj.users_collection[0].name==expected)
for name in ['MAT_Kart_Red','MAT_Rubber_Dark','MAT_Metal_Dark','MAT_Rim_Silver','MAT_Seat_Black']:
    mat=bpy.data.materials.get(name)
    check('material exists '+name,bool(mat),True,bool(mat and mat.use_nodes and mat.node_tree.nodes.get('Principled BSDF')))
    if mat and mat.use_nodes and name=='MAT_Rubber_Dark':
        n=mat.node_tree.nodes.get('Principled BSDF')
        check('rubber roughness',n.inputs['Roughness'].default_value if n else None,'>=.65',n is not None and n.inputs['Roughness'].default_value>=.65)
for data in list(bpy.data.meshes)+list(bpy.data.materials):
    check('datablock '+data.name,data.users,'used, no suffix',data.users>0 and re.search(r'\.\d{3}$',data.name) is None)
for view in VIEWS:
    cam=bpy.data.objects.get('CAM_Kart01_'+view.title())
    check('camera '+view,cam.type if cam else None,'CAMERA',cam is not None and cam.type=='CAMERA')
    if cam and cam.type=='CAMERA' and allpts:
        coords=[world_to_camera_view(bpy.context.scene,cam,v) for v in allpts]
        check('framing '+view,len(coords),'all vertices within 5% margin',all(.05<=v.x<=.95 and .05<=v.y<=.95 and v.z>0 for v in coords))
    markers=[m for m in bpy.context.scene.timeline_markers if m.frame==VIEWS.index(view)+1 and m.camera==cam]
    check('marker '+view,len(markers),1,cam is not None and len(markers)==1)
for label in ('Key','Fill','Rim'):
    obj=bpy.data.objects.get('LIGHT_Kart01_'+label)
    check('light '+label,obj.type if obj else None,'LIGHT',obj is not None and obj.type=='LIGHT' and obj.data.energy>0)
scene=bpy.context.scene
check('units',(scene.unit_settings.system,scene.unit_settings.scale_length),('METRIC',1),scene.unit_settings.system=='METRIC' and abs(scene.unit_settings.scale_length-1)<1e-6)
chassis=points.get('Kart01_Chassis',[])
check('chassis clearance',min((v.z for v in chassis),default=None),'>=.17',bool(chassis) and min(v.z for v in chassis)>=.17-.00001)
report=dict(passed=all(c['passed'] for c in checks),checks=checks,triangles=triangles,
            visual_review_required=['tapered nose','mirrored pods','seat base/back and rear placement','steering and pedals','supports and wheel clearance','material assignments and appearance','four distinct views'],
            scope='Objective scene checks only; visual, delivery, and GLB round-trip evidence required separately')
