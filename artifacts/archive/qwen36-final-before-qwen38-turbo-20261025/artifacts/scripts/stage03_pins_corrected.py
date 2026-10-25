"""Operator-provided correction; assisted continuation, not unaided model output."""
import bpy
import bmesh
from math import cos, sin, pi, sqrt
from typing import cast
from bpy.types import NodeSocketColor, NodeSocketFloat


def run_stage():
    scene=bpy.context.scene
    root=bpy.data.objects['BowlingPair01_ROOT']
    collection=bpy.data.collections['BP01_PINS']
    # radius,height order is deliberate. No zero-radius rings are generated.
    profile=[(.036,0.0),(.041,.004),(.052,.025),(.0605,.060),(.0605,.100),
             (.052,.150),(.040,.200),(.028,.240),(.022,.260),(.022,.270),
             (.022,.276),(.022,.282),(.022,.288),(.022,.294),(.022,.300),
             (.025,.312),(.032,.325),(.036,.340),(.035,.355),(.029,.370),
             (.018,.378),(.008,.380)]
    bands=[(.270,.276),(.288,.294)]
    segments=24; vertices=[]; faces=[]; material_indices=[]
    for radius,height in profile:
        vertices.extend((radius*cos(2*pi*i/segments),radius*sin(2*pi*i/segments),height) for i in range(segments))
    for level in range(len(profile)-1):
        middle=(profile[level][1]+profile[level+1][1])/2
        red=any(low<middle<high for low,high in bands)
        for index in range(segments):
            following=(index+1)%segments
            faces.append((level*segments+index,level*segments+following,(level+1)*segments+following,(level+1)*segments+index))
            material_indices.append(1 if red else 0)
    top=len(vertices); vertices.append((0,0,.381))
    bottom=len(vertices); vertices.append((0,0,0))
    for index in range(segments):
        following=(index+1)%segments
        faces.extend([(top,(len(profile)-1)*segments+index,(len(profile)-1)*segments+following),
                      (bottom,following,index)])
        material_indices.extend([0,0])
    mesh=bpy.data.meshes.new('Pin_Mesh_OperatorCorrected')
    mesh.from_pydata(vertices,[],faces)
    mesh.update()
    assert mesh.validate() is False, 'Generated mesh required structural repair'
    mesh.calc_loop_triangles()
    bm=bmesh.new()
    try:
        bm.from_mesh(mesh)
        assert all(face.calc_area()>1e-12 for face in bm.faces), 'Zero-area pin face'
        assert all(edge.is_manifold for edge in bm.edges), 'Open pin seam/cap'
        volume=bm.calc_volume(signed=True)
        assert volume>0, 'Pin winding is inward'
    finally:
        bm.free()
    def material(name,color):
        result=bpy.data.materials.new(name)
        result.use_nodes=True
        tree=result.node_tree
        assert tree is not None
        tree.nodes.clear()
        output=tree.nodes.new('ShaderNodeOutputMaterial')
        principled=tree.nodes.new('ShaderNodeBsdfPrincipled')
        cast(NodeSocketColor,principled.inputs['Base Color']).default_value=color
        cast(NodeSocketFloat,principled.inputs['Roughness']).default_value=.28
        tree.links.new(principled.outputs['BSDF'],output.inputs['Surface'])
        return result
    mesh.materials.append(material('Mat_PinWhite_Corrected',(.93,.91,.88,1)))
    mesh.materials.append(material('Mat_PinRed_Corrected',(.70,.10,.10,1)))
    for polygon,index in zip(mesh.polygons,material_indices):
        polygon.material_index=index
        polygon.use_smooth=polygon.loop_total==4
    # Remove objects only. Never inspect removed objects or delete their shared data.
    old=list(collection.objects)
    assert all(obj.name.startswith('Pin_') for obj in old)
    for obj in old:
        bpy.data.objects.remove(obj,do_unlink=True)
    created=[]; expected={}
    for side,center in [('L',-.95),('R',.95)]:
        number=1
        for row in range(4):
            for column in range(row+1):
                name=f'Pin_{side}_{number:02d}'
                position=(center+(column-row/2)*.3048,18.288+row*sqrt(3)/2*.3048,0)
                obj=bpy.data.objects.new(name,mesh)
                obj.parent=root
                obj.location=position
                collection.objects.link(obj)
                created.append(obj);expected[name]=position;number+=1
    bpy.context.view_layer.update()
    depsgraph=bpy.context.evaluated_depsgraph_get()
    measurements=[]
    for obj in created:
        evaluated=obj.evaluated_get(depsgraph)
        evaluated_mesh=evaluated.to_mesh()
        try:
            evaluated_mesh.calc_loop_triangles()
            coords=[v.co for v in evaluated_mesh.vertices]
            height=max(v.z for v in coords)-min(v.z for v in coords)
            diameter=2*max(sqrt(v.x*v.x+v.y*v.y) for v in coords)
            assert abs(height-.381)<=.003 and abs(diameter-.121)<=.003
            assert abs(min(v.z for v in coords))<1e-6
            assert len(evaluated_mesh.loop_triangles)<=2500
            assert all(abs(obj.location[i]-expected[obj.name][i])<1e-6 for i in range(3))
            measurements.append({'name':obj.name,'height':height,'diameter':diameter,
                                 'triangles':len(evaluated_mesh.loop_triangles),'position':list(obj.location)})
        finally:
            evaluated.to_mesh_clear()
    assert len(created)==20
    return {'stage':'03','passed':True,'operator_assisted':True,'profile_order':'radius,height',
            'pin_count':len(created),'red_band_intervals':bands,'nonmanifold_edges':0,
            'positive_volume':volume,'measurements':measurements}


report=run_stage()
