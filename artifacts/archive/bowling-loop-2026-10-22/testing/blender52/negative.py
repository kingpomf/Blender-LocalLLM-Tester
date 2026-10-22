"""Intentional invalid APIs: diagnostics must flag these, not suppress them."""
import bpy

obj = bpy.data.objects.new('Invalid', None)
obj.children.link(obj)
bpy.scene.unit_system = 'METRIC'
bpy.ops.object.collection_links_add()
