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
