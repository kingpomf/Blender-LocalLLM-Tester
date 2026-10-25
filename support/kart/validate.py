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
