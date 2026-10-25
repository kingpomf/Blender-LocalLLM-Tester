import bpy
import bmesh
from mathutils import Vector

def create_box_mesh(name, size=(1,1,1)):
    """Create a box mesh with given dimensions using bmesh."""
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bm.verts.ensure_lookup_table()
    for v in bm.verts:
        v.co = v.co * Vector(size)
    bm.to_mesh(me)
    bm.free()
    return me

# ============================================================
# Fix 1: AlleyFloor - swap dimensions from [78, 0.65, 338] to [78, 338, 0.65]
# ============================================================
floor = bpy.data.objects.get("AlleyFloor")
if floor is not None:
    floor_loc = floor.location[:]
    floor_mesh = floor.data
    floor_parent = floor.parent
    
    bpy.data.objects.remove(floor, do_unlink=True)
    bpy.data.meshes.remove(floor_mesh)
    
    new_mesh = create_box_mesh("AlleyFloor_Mesh", (78.0, 338.0, 0.65))
    new_obj = bpy.data.objects.new("AlleyFloor", new_mesh)
    new_obj.location = floor_loc
    new_obj.parent = floor_parent
    
    scene = bpy.context.scene
    scene.collection.objects.link(new_obj)

# ============================================================
# Fix 2: Hood_Canopy - scale to fit within X=[-0.4,0.4], Y=[-4.3,-0.3]
# ============================================================
hood = bpy.data.objects.get("Hood_Canopy")
if hood is not None:
    hood_loc = hood.location[:]
    hood_parent = hood.parent
    hood_mesh = hood.data
    
    bpy.data.objects.remove(hood, do_unlink=True)
    bpy.data.meshes.remove(hood_mesh)
    
    new_mesh = create_box_mesh("Hood_Canopy_Mesh", (0.8, 4.0, 0.18))
    new_obj = bpy.data.objects.new("Hood_Canopy", new_mesh)
    new_obj.location = (0.0, -2.15, 2.0)
    new_obj.parent = hood_parent
    
    scene = bpy.context.scene
    scene.collection.objects.link(new_obj)

# ============================================================
# Fix 3: Ball_03 - move to x=0.22 (within return rack bounds)
# ============================================================
ball03 = bpy.data.objects.get("Ball_03")
if ball03 is not None:
    ball03.location[0] = 0.22