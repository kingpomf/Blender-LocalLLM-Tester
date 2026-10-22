"""Static typing fixture only; actual execution is through the isolated worker."""
from typing import cast
import bpy

scene = cast(bpy.types.Scene, bpy.context.scene)
scene.unit_settings.system = 'METRIC'
collection = bpy.data.collections.new('Fixture')
scene.collection.children.link(collection)
mesh = bpy.data.meshes.new('FixtureMesh')
obj = bpy.data.objects.new('FixtureObject', mesh)
collection.objects.link(obj)
root = bpy.data.objects.new('Root', None)
scene.collection.objects.link(root)
obj.parent = root
view_layer = cast(bpy.types.ViewLayer, bpy.context.view_layer)
view_layer.objects.active = obj
coordinates = [obj.location.x, obj.location.y, obj.location.z]
