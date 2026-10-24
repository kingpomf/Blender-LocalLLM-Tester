"""Read-only measured Blender acceptance. Never repairs geometry during validation.

Local render/receipt validation is merged separately by scripts/validate_checkpoint.py.
Unresolved qualitative evidence is explicit and cannot produce a stage PASS.
"""
import bpy
import bmesh
import hashlib
import json
import math
from collections import Counter
from itertools import combinations
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view


def scene_fingerprint():
    rows=[]
    for obj in sorted(bpy.context.scene.objects,key=lambda o:o.name):
        row={'name':obj.name,'type':obj.type,'matrix':[list(r) for r in obj.matrix_world],
             'parent':obj.parent.name if obj.parent else None,'hide_render':obj.hide_render,
             'collections':sorted(c.name for c in obj.users_collection)}
        if obj.type=='MESH':
            row.update(vertices=[list(v.co) for v in obj.data.vertices],
                       polygons=[list(p.vertices) for p in obj.data.polygons],
                       material_indices=[p.material_index for p in obj.data.polygons],
                       materials=[m.name if m else None for m in obj.data.materials])
        rows.append(row)
    return hashlib.sha256(json.dumps(rows,sort_keys=True).encode()).hexdigest()


def run_validation():
    scene=bpy.context.scene
    before=scene_fingerprint()
    depsgraph=bpy.context.evaluated_depsgraph_get()
    checks=[]
    facts={}
    geometry={}
    bvhs={}
    def record(stage,key,expected,observed,passed,tolerance='',objects=(),status=None):
        checks.append({'id':f'S{stage:02d}_{key}','stage':f'{stage:02d}','expected':expected,
            'observed':observed,'tolerance':tolerance,'objects':list(objects),
            'status':status or ('PASS' if passed else 'FAIL'),'passed':bool(passed)})
    def near(a,b,tol):
        return abs(a-b)<=tol+1e-6
    def collection(name):
        col=bpy.data.collections.get(name)
        return list(col.objects) if col else []
    def mesh_objects(name):
        return [o for o in collection(name) if o.type=='MESH']
    def find(prefix):
        return next((o for o in scene.objects if o.name==prefix),None) or next((o for o in scene.objects if o.name.startswith(prefix+'.')),None)
    def ancestor(obj,root):
        current=obj.parent
        while current:
            if current==root:return True
            current=current.parent
        return False
    def color(material):
        if material and material.use_nodes and material.node_tree:
            output=next((n for n in material.node_tree.nodes if n.type=='OUTPUT_MATERIAL' and n.is_active_output),None)
            links=output.inputs['Surface'].links if output else []
            node=links[0].from_node if links else None
            if node and node.type=='BSDF_PRINCIPLED':
                return list(node.inputs['Base Color'].default_value)
        return list(material.diffuse_color) if material else None
    for obj in scene.objects:
        if obj.type!='MESH':continue
        evaluated=obj.evaluated_get(depsgraph)
        mesh=evaluated.to_mesh()
        try:
            mesh.calc_loop_triangles()
            local=[v.co.copy() for v in mesh.vertices]
            world=[obj.matrix_world@v for v in local]
            polygons=[list(p.vertices) for p in mesh.polygons]
            bm=bmesh.new()
            try:
                bm.from_mesh(mesh)
                areas=[f.calc_area() for f in bm.faces]
                boundary=sum(e.is_boundary for e in bm.edges)
                nonmanifold=sum(not e.is_manifold for e in bm.edges)
                volume=bm.calc_volume(signed=True) if bm.faces else 0
            finally:
                bm.free()
            lo=[min((v[i] for v in world),default=0) for i in range(3)]
            hi=[max((v[i] for v in world),default=0) for i in range(3)]
            local_lo=[min((v[i] for v in local),default=0) for i in range(3)]
            local_hi=[max((v[i] for v in local),default=0) for i in range(3)]
            materials=[color(m) for m in mesh.materials]
            faces=[{'vertices':list(p.vertices),'center':list(p.center),'material':p.material_index} for p in mesh.polygons]
            fact={'minimum':lo,'maximum':hi,'dimensions':[hi[i]-lo[i] for i in range(3)],
                  'local_center':[(local_lo[i]+local_hi[i])/2 for i in range(3)],
                  'local_minimum':local_lo,'local_maximum':local_hi,
                  'triangles':len(mesh.loop_triangles),'faces':len(mesh.polygons),
                  'degenerate_faces':sum(a<1e-12 for a in areas),'boundary_edges':boundary,
                  'nonmanifold_edges':nonmanifold,'signed_volume':volume,
                  'material_colors':materials,'material_face_counts':dict(Counter(str(p.material_index) for p in mesh.polygons)),
                  'scale':list(obj.scale),'modifiers':[m.type for m in obj.modifiers if m.show_viewport],
                  'finite':all(math.isfinite(v) for co in local for v in co)}
            facts[obj.name]=fact
            geometry[obj.name]={'local':local,'world':world,'polygons':polygons,'faces':faces}
            if world and polygons:bvhs[obj.name]=BVHTree.FromPolygons(world,polygons)
        finally:
            evaluated.to_mesh_clear()  # Ownership belongs to evaluated object, never Mesh.
    root=find('BowlingPair01_ROOT')
    required=['BP01_STATIC','BP01_PINS','BP01_BALLS','BP01_COLLISION','BP01_PRESENTATION']
    record(0,'units',{'system':'METRIC','scale':1}, {'system':scene.unit_settings.system,'scale':scene.unit_settings.scale_length},
           scene.unit_settings.system=='METRIC' and near(scene.unit_settings.scale_length,1,1e-6))
    record(0,'root','identity EMPTY',{'type':root.type,'location':list(root.location),'rotation':list(root.rotation_euler),'scale':list(root.scale)} if root else None,
           root is not None and root.type=='EMPTY' and root.location.length<1e-6 and sum(abs(v) for v in root.rotation_euler)<1e-6 and all(near(v,1,1e-6) for v in root.scale))
    record(0,'collections',required,[c.name for c in scene.collection.children],all(name in bpy.data.collections for name in required))
    visual=mesh_objects('BP01_STATIC')+mesh_objects('BP01_PINS')+mesh_objects('BP01_BALLS')
    record(0,'hierarchy','all visual meshes descend from root',[o.name for o in visual if not ancestor(o,root)],all(ancestor(o,root) for o in visual))
    for side,x in [('L',-.95),('R',.95)]:
        lane=find('Lane_'+side+'_Surface'); approach=find('Approach_'+side)
        for obj,ylo,yhi,label in [(lane,0,19.20,'lane'),(approach,-4.572,0,'approach')]:
            f=facts.get(obj.name) if obj else None
            record(1,label+'_'+side,{'width':1.0668,'center_x':x,'y':[ylo,yhi],'surface_z':0},f,
                bool(f) and near(f['dimensions'][0],1.0668,.005) and near((f['minimum'][0]+f['maximum'][0])/2,x,.005)
                and near(f['minimum'][1],ylo,.01) and near(f['maximum'][1],yhi,.01) and near(f['maximum'][2],0,.002), 'meters', [obj.name] if obj else [])
        for prefix,count,y in [('ArrowTri_',7,4.57),('Dot_',7,-1.0),('Foul_',1,0)]:
            found=[o for o in visual if o.name.startswith(prefix+side) and o.name in facts]
            observed=[{'name':o.name,'bounds':[facts[o.name]['minimum'],facts[o.name]['maximum']]} for o in found]
            ok=len(found)==count and all(abs(facts[o.name]['minimum'][2])<=.002001 and abs(facts[o.name]['maximum'][2])<=.002001
                    and abs((facts[o.name]['minimum'][1]+facts[o.name]['maximum'][1])/2-y)<=.100001 for o in found)
            record(1,prefix+side,{'count':count,'y':y,'surface_z':0},observed,ok,'0.002m surface /0.10m y')
            if prefix=='Foul_' and len(found)==1:
                record(1,'foul_width_'+side,'0.02..0.05m longitudinal',facts[found[0].name]['dimensions'][1],.02-1e-6<=facts[found[0].name]['dimensions'][1]<=.05+1e-6)
    gutters=[o for o in mesh_objects('BP01_STATIC') if o.name.startswith('Gutter_')]
    record(2,'gutter_count',4,len(gutters),len(gutters)==4)
    for obj in gutters:
        f=facts[obj.name]; coords=geometry[obj.name]['world']; mid=(f['minimum'][0]+f['maximum'][0])/2
        central=[v.z for v in coords if abs(v.x-mid)<.02]
        record(2,obj.name,{'width':[.22,.25],'y':[0,19.2],'trough_z':[-.12,-.08],'lip_z_max':.005},
            {'bounds':[f['minimum'],f['maximum']],'center_section_z':central},
            .22-1e-6<=f['dimensions'][0]<=.25+1e-6 and near(f['minimum'][1],0,.01) and near(f['maximum'][1],19.2,.01)
            and -.12-1e-6<=f['minimum'][2]<=-.08+1e-6 and f['maximum'][2]<=.005001 and bool(central) and min(central)<-.079999)
        side='L' if '_L_' in obj.name else 'R'; lane=facts.get('Lane_'+side+'_Surface')
        inner='_Inner' in obj.name
        edge=(lane['maximum'][0] if (side=='L')==inner else lane['minimum'][0]) if lane else None
        lip=f['minimum'][0] if (side=='L')==inner else f['maximum'][0]
        record(2,obj.name+'_adjacency','lane edge gap0..0.01m',{'lane_edge':edge,'gutter_lip':lip},edge is not None and near(edge,lip,.01))
    playable=[facts[o.name] for o in gutters]+[facts[n] for n in ['Lane_L_Surface','Lane_R_Surface'] if n in facts]
    record(2,'pair_envelope','x within[-1.80,1.80]',[min(f['minimum'][0] for f in playable),max(f['maximum'][0] for f in playable)],all(f['minimum'][0]>=-1.800001 and f['maximum'][0]<=1.800001 for f in playable))
    for side in ['L','R']:
        deck=find('PinDeck_'+side); pit=find('Pit_Catch')
        f=facts.get(deck.name) if deck else None
        pins=[o for o in mesh_objects('BP01_PINS') if o.name.startswith('Pin_'+side+'_')]
        coverage=bool(f) and all(f['minimum'][0]-.002<=facts[o.name]['minimum'][0] and f['maximum'][0]+.002>=facts[o.name]['maximum'][0]
            and f['minimum'][1]-.002<=facts[o.name]['minimum'][1] and f['maximum'][1]+.002>=facts[o.name]['maximum'][1] for o in pins)
        record(2,'deck_'+side,'z0±0.002; entire rack footprint',f,bool(f) and coverage and near(f['maximum'][2],0,.002) if f else False)
    pf=facts.get(pit.name) if pit else None
    record(2,'pit','begins19.20; extends≥0.60; recessed',pf,bool(pf) and near(pf['minimum'][1],19.2,.01) and pf['maximum'][1]>=19.799999 and pf['maximum'][2]<0)
    pins=mesh_objects('BP01_PINS')
    expected_names={f'Pin_{side}_{i:02d}' for side in ['L','R'] for i in range(1,11)}
    record(3,'pin_names',sorted(expected_names),sorted(o.name for o in pins),{o.name for o in pins}==expected_names)
    for side,x in [('L',-.95),('R',.95)]:
        number=1
        for row in range(4):
            for column in range(row+1):
                name=f'Pin_{side}_{number:02d}'; obj=find(name); f=facts.get(name)
                expected=[x+(column-row/2)*.3048,18.288+row*math.sqrt(3)/2*.3048,0]
                record(3,name+'_position',expected,list(obj.matrix_world.translation) if obj else None,
                    obj is not None and (obj.matrix_world.translation-Vector(expected)).length<=.003001,'0.003m',[name])
                if f:
                    record(3,name+'_dimensions',{'height':.381,'diameter':.121,'base_z':0,'max_triangles':2500},f,
                        near(f['dimensions'][2],.381,.003) and near(max(f['dimensions'][:2]),.121,.003)
                        and near(f['minimum'][2],0,.002) and f['triangles']<=2500 and abs(f['local_minimum'][2])<=.001001)
                    coords=geometry[name]['local']; neck=[math.hypot(v.x,v.y) for v in coords if .27<=v.z<=.34]
                    max_r=max(math.hypot(v.x,v.y) for v in coords)
                    neck_r=min(neck) if neck else max_r
                    record(3,name+'_neck_ratio','neck/body<0.65',neck_r/max_r if max_r else None,bool(max_r) and neck_r/max_r<.65)
                    red=[]; intervals=[]
                    for face in geometry[name]['faces']:
                        c=f['material_colors'][face['material']] if face['material']<len(f['material_colors']) else None
                        if c and c[0]>.35 and c[0]>2*c[1] and c[0]>2*c[2]:
                            red.append(face['center'][2])
                            zs=[coords[i].z for i in face['vertices']]
                            intervals.append([min(zs),max(zs)])
                    bands=[]
                    for low,high in sorted(intervals):
                        if not bands or low>bands[-1][1]+1e-5:bands.append([low,high])
                        else:bands[-1][1]=max(bands[-1][1],high)
                    record(3,name+'_red_bands','two separated red material bands at neck',{'red_face_count':len(red),'z_intervals':bands},
                           len(bands)==2 and all(.24<=low<high<=.36 for low,high in bands))
                    record(3,name+'_closed_mesh','closed nondegenerate outward surface',{'boundary_edges':f['boundary_edges'],'nonmanifold_edges':f['nonmanifold_edges'],'signed_volume':f['signed_volume']},f['nonmanifold_edges']==0 and f['degenerate_faces']==0 and f['signed_volume']>0)
                number+=1
    balls=mesh_objects('BP01_BALLS')
    record(4,'ball_names',['Ball_01','Ball_02','Ball_03'],sorted(o.name for o in balls),{o.name for o in balls}=={'Ball_01','Ball_02','Ball_03'})
    for obj in balls:
        f=facts[obj.name]; coords=geometry[obj.name]['local']; radii=[v.length for v in coords]; radius=max(radii,default=0)
        record(4,obj.name+'_diameter',.216,2*radius,near(2*radius,.216,.003),'±0.003m',[obj.name])
        record(4,obj.name+'_pivot',0,f['local_center'],Vector(f['local_center']).length<=.001001,'0.001m',[obj.name])
        record(4,obj.name+'_triangles','≤8000',f['triangles'],f['triangles']<=8000)
        recessed={i for i,r in enumerate(radii) if r<=radius-.015}
        graph={i:set() for i in recessed}
        for polygon in geometry[obj.name]['polygons']:
            for a,b in zip(polygon,polygon[1:]+polygon[:1]):
                if a in graph and b in graph:graph[a].add(b);graph[b].add(a)
        components=[]; remaining=set(recessed)
        while remaining:
            stack=[remaining.pop()]; group=[]
            while stack:
                i=stack.pop();group.append(i)
                for j in graph[i]&remaining:remaining.remove(j);stack.append(j)
            components.append(group)
        deep_regions=[group for group in components if len(group)>=3]
        record(4,obj.name+'_recess_geometry','3 connected recessed regions≥0.015m below exterior',
            {'radius':radius,'max_radial_depth':radius-min(radii,default=radius),'deep_regions':len(deep_regions),'region_sizes':[len(g) for g in components]},
            len(deep_regions)==3 and f['degenerate_faces']==0)
        record(4,obj.name+'_holes_visual','visible open grip sockets in actual props render','Requires render-based inspection; depth vertices alone do not prove usable openings',False,status='UNRESOLVED')
    for a,b in combinations(balls,2):
        ra=max(v.length for v in geometry[a.name]['local']);rb=max(v.length for v in geometry[b.name]['local'])
        gap=(a.matrix_world.translation-b.matrix_world.translation).length-ra-rb
        record(4,a.name+'_'+b.name+'_gap','≥0.005m exterior separation',gap,gap>=.005-1e-6)
    return_objs=[o for o in visual if o.name.startswith(('Hood','ReturnRack','ReturnFrame'))]
    record(5,'return_bounds',{'x':[-.4,.4],'y':[-4.3,-.3]},
        {o.name:[facts[o.name]['minimum'],facts[o.name]['maximum']] for o in return_objs},bool(return_objs) and all(
            facts[o.name]['minimum'][0]>=-.400001 and facts[o.name]['maximum'][0]<=.400001 and facts[o.name]['minimum'][1]>=-4.300001 and facts[o.name]['maximum'][1]<=-.299999 for o in return_objs))
    for ball in balls:
        center=ball.matrix_world.translation; radius=max(v.length for v in geometry[ball.name]['local'])
        distances=[bvhs[o.name].find_nearest(center)[3] for o in return_objs if o.name in bvhs]
        nearest=min(distances,default=None)
        record(5,ball.name+'_rack_contact','surface contact within0.005m and no penetration',{'nearest_rack_distance':nearest,'ball_radius':radius},nearest is not None and abs(nearest-radius)<=.005001)
    benches=[o for o in visual if o.name.startswith('Bench')]
    record(5,'benches','two seats entirely behind y=-4.572', {o.name:facts[o.name]['maximum'][1] for o in benches},len(benches)==2 and all(facts[o.name]['maximum'][1]<-4.572 for o in benches))
    screens=[o for o in visual if o.name.startswith('Screen_')]
    record(5,'screen_bottoms','two screens bottom z≥2.20',{o.name:facts[o.name]['minimum'][2] for o in screens},len(screens)==2 and all(facts[o.name]['minimum'][2]>=2.20-1e-6 for o in screens))
    wall=find('MaskingWall'); wf=facts.get(wall.name) if wall else None
    pin_top=max((facts[o.name]['maximum'][2] for o in pins),default=0)
    record(5,'masking_clearance','wall bottom≥standing pin tops+0.60',wf,bool(wf) and wf['minimum'][2]-pin_top>=.60-1e-6)
    floor=find('AlleyFloor'); ff=facts.get(floor.name) if floor else None
    record(5,'floor_below_assembly','floor is below z0 and spans approach/seating/lanes',ff,bool(ff) and ff['maximum'][2]<=.000001 and ff['minimum'][1]<=-5.15 and ff['maximum'][1]>=20)
    deco=[o.name for o in visual if o.name.startswith(('Stripe','LightBar','WallPanel'))]
    record(5,'decorations','≥2 original decorative elements',deco,len(deco)>=2)
    for key,expected in [('return_opening','visible hood opening and supporting cradle'),('scoreboard_labels','different readable01/02 and score grid'),('masking_labels','01/02 labels behind racks')]:
        record(5,key,expected,'Requires actual visual/portable label evidence',False,status='UNRESOLVED')
    for obj in visual:
        f=facts[obj.name]
        record(6,obj.name+'_scale','applied positive scale1',f['scale'],all(near(v,1,1e-6) for v in f['scale']))
        record(6,obj.name+'_geometry','finite nondegenerate faces; no unapplied topology modifiers',
            {'finite':f['finite'],'degenerate_faces':f['degenerate_faces'],'modifiers':f['modifiers']},f['finite'] and f['degenerate_faces']==0 and not f['modifiers'])
    total=sum(facts[o.name]['triangles'] for o in visual)
    collision=mesh_objects('BP01_COLLISION'); collision_total=sum(facts[o.name]['triangles'] for o in collision)
    record(6,'visual_triangle_budget','≤150000, all placed instances',total,total<=150000)
    record(6,'collision_triangle_budget','≤10000',collision_total,0<collision_total<=10000)
    record(6,'collision_exclusion','COL_ meshes hidden from beauty render',
        {o.name:o.hide_render for o in collision},bool(collision) and all(o.name.startswith('COL_') and o.hide_render for o in collision))
    for gutter in gutters:
        proxy=find('COL_'+gutter.name); pf=facts.get(proxy.name) if proxy else None; gf=facts[gutter.name]
        record(6,gutter.name+'_collision','concave profile aligns within0.01m; not flat bridge',pf,
            bool(pf) and all(near(pf['minimum'][i],gf['minimum'][i],.01) and near(pf['maximum'][i],gf['maximum'][i],.01) for i in [0,1,2]))
    for side in ['L','R']:
        proxy=find('COL_LaneBed_'+side); pf=facts.get(proxy.name) if proxy else None; lf=facts.get('Lane_'+side+'_Surface')
        record(6,'lane_collision_'+side,'bounds and top align within0.01m',pf,bool(pf) and bool(lf) and near(pf['maximum'][2],lf['maximum'][2],.01)
            and all(near(pf[end][axis],lf[end][axis],.01) for axis in [0,1] for end in ['minimum','maximum']))
    material_ids=sorted({slot.material.name for o in visual for slot in o.material_slots if slot.material})
    record(6,'required_material_identities','wood,pin white/red,3ball colors,gutter/metal,seat,screen',{'material_ids':material_ids,'seat_assignments':{o.name:facts[o.name]['material_colors'] for o in benches}},
        all(any(token.lower() in name.lower() for name in material_ids) for token in ['Wood','PinWhite','PinRed','Ball_01','Ball_02','Ball_03','Gutter','Screen'])
        and bool(benches) and all(bool(facts[o.name]['material_colors']) for o in benches))
    record(6,'normals_and_static_origins','outward surfaces; documented useful static pivots','Topology facts recorded; final visual normals/import guide still required',False,status='UNRESOLVED')
    cameras=['Overview','Player','PinDeck','Props']
    for role in cameras:
        camera=find('CAM_BowlingPair01_'+role)
        targets=visual if role=='Overview' else (pins if role=='PinDeck' else balls if role=='Props' else [o for o in visual if o.name=='Lane_L_Surface'])
        fractions={}
        if camera and camera.type=='CAMERA':
            for obj in targets:
                lo=facts[obj.name]['minimum'];hi=facts[obj.name]['maximum']
                projected=[world_to_camera_view(scene,camera,Vector((x,y,z))) for x in [lo[0],hi[0]] for y in [lo[1],hi[1]] for z in [lo[2],hi[2]]]
                fractions[obj.name]=sum(p.z>0 and 0<=p.x<=1 and 0<=p.y<=1 for p in projected)/8
        record(7,role+'_framing','all required target bounds inside positive camera frustum',fractions,
            bool(fractions) and all(value==1 for value in fractions.values()))
        record(7,role+'_presentation','camera/light not parented to visual root',camera.parent.name if camera and camera.parent else None,camera is not None and not ancestor(camera,root))
    record(7,'local_renders','four verified≥1280x720 distinct same-asset renders','Checked by local artifact validator, not inside /job',False,status='UNRESOLVED')
    record(7,'actual_render_visibility','required assets visible and unobscured','Needs hash-bound local image inspection evidence',False,status='UNRESOLVED')
    unchanged=before==scene_fingerprint()
    record(8,'read_only_validation','source geometry/transforms/material assignments unchanged',unchanged,unchanged)
    results={f'{stage:02d}':('FAIL' if any(c['status']=='FAIL' for c in checks if c['stage']==f'{stage:02d}') else
        'UNRESOLVED' if any(c['status']=='UNRESOLVED' for c in checks if c['stage']==f'{stage:02d}') else 'PASS') for stage in range(8)}
    result={'stage':'08','read_only':unchanged,'source_fingerprint_before':before,'source_fingerprint_after':scene_fingerprint(),
        'passed':all(c['passed'] for c in checks),'checks':checks,'check_count':len(checks),
        'pass_count':sum(c['status']=='PASS' for c in checks),'fail_count':sum(c['status']=='FAIL' for c in checks),
        'unresolved_count':sum(c['status']=='UNRESOLVED' for c in checks),'stage_results':results,
        'facts':facts,'scope':'Geometry findings plus explicit unresolved visual/delivery criteria; no repair or render was executed.'}
    with open('/job/validation.json','w') as file:json.dump(result,file,indent=2)
    return result


report=run_validation()
