"""Read the installed API without executing operators or changing scene datablocks."""
import bpy
import bmesh
import mathutils
import json


def members(cls):
    return sorted(name for name in dir(cls) if not name.startswith('_'))


types={};errors={}
for name in dir(bpy.types):
    try:
        cls=getattr(bpy.types,name)
        rna=getattr(cls,'bl_rna',None)
        if rna is None:continue
        props={p.identifier:{'type':p.type,'target':getattr(getattr(p,'fixed_type',None),'identifier',None)} for p in rna.properties}
        functions={f.identifier:{p.identifier:{'type':p.type,'required':p.is_required} for p in f.parameters if not p.is_output} for f in rna.functions}
        types[name]={'members':sorted(set(members(cls))|set(props)|set(functions)), 'properties':props,'functions':functions}
    except Exception as error:errors['bpy.types.'+name]=type(error).__name__
operators={}
for category in dir(bpy.ops):
    if category.startswith('_'):continue
    group=getattr(bpy.ops,category)
    for name in dir(group):
        if name.startswith('_'):continue
        key='bpy.ops.'+category+'.'+name
        try:
            rna=getattr(group,name).get_rna_type()
            operators[key]={'parameters':{p.identifier:{'type':p.type,'required':p.is_required} for p in rna.properties if p.identifier!='rna_type'},'description':rna.description}
        except Exception as error:errors[key]=type(error).__name__
collections={}
for prop in bpy.data.bl_rna.properties:
    if prop.type=='COLLECTION':
        value=getattr(bpy.data,prop.identifier)
        collections[prop.identifier]={'target':getattr(getattr(prop,'fixed_type',None),'identifier',None),'members':members(value)}
extras={}
for module,prefix in [(bmesh.types,'bmesh.types'),(mathutils,'mathutils')]:
    for name in dir(module):
        value=getattr(module,name)
        if isinstance(value,type):extras[prefix+'.'+name]={'members':members(value)}
runtime_returns={}
probe=next(iter(bpy.context.scene.objects),None)
assert probe is not None, 'Return-type capture needs an existing read-only scene object'
for name,element in [('children','Object'),('children_recursive','Object'),('users_collection','Collection')]:
    value=getattr(probe,name)
    runtime_returns['Object.'+name]={'python_type':type(value).__name__,'members':members(value),
        'element_type':element,'guidance':'Parent/child relationships are changed through obj.parent. To delete an object use bpy.data.objects.remove(obj, do_unlink=True); do not unlink through Object.children.'}
catalog={'schema_version':2,'version':bpy.app.version_string,'build_hash':bpy.app.build_hash.decode(),
    'types':types,'operators':operators,'data_collections':collections,'extras':extras,
    'bmesh_ops':sorted(n for n in dir(bmesh.ops) if not n.startswith('_')),'runtime_returns':runtime_returns,'errors':errors}
with open('/job/api-catalog.json','w') as file:json.dump(catalog,file,separators=(',',':'))
report={'read_only':True,'version':catalog['version'],'types':len(types),'operators':len(operators),'introspection_errors':len(errors),'runtime_returns':runtime_returns}
