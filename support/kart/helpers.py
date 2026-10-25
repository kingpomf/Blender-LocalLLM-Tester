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
