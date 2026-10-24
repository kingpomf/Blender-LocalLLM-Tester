"""Prevent common wrong-workflow/API calls before reserving a Blender attempt.

This is a reliability check for ordinary generated Python, not a security sandbox.
"""
import ast


def inspect_authoring(code):
    try:
        tree=ast.parse(code)
    except SyntaxError as error:
        return {'ok':False,'code':'python_syntax','recoverable':True,'message':str(error),'next_tool':'blender_scene_author'}
    aliases={}
    def dotted(node):
        if isinstance(node,ast.Name):return aliases.get(node.id,node.id)
        if isinstance(node,ast.Attribute):return dotted(node.value)+'.'+node.attr
        if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id=='getattr' and len(node.args)>1 and isinstance(node.args[1],ast.Constant) and isinstance(node.args[1].value,str):
            return dotted(node.args[0])+'.'+node.args[1].value
        return ''
    for node in ast.walk(tree):
        if isinstance(node,ast.Import):
            for item in node.names:aliases[item.asname or item.name]=item.name
        elif isinstance(node,ast.ImportFrom) and node.module:
            for item in node.names:aliases[item.asname or item.name]=node.module+'.'+item.name
    for _ in range(3):
        for node in ast.walk(tree):
            if isinstance(node,ast.Assign):
                value=dotted(node.value)
                if value:
                    for target in node.targets:
                        if isinstance(target,ast.Name):aliases[target.id]=value
    constants={}
    for node in ast.walk(tree):
        if isinstance(node,ast.Assign) and isinstance(node.value,ast.Constant) and isinstance(node.value.value,str):
            for target in node.targets:
                if isinstance(target,ast.Name):constants[target.id]=node.value.value
    def string(node):
        return node.value if isinstance(node,ast.Constant) and isinstance(node.value,str) else constants.get(node.id) if isinstance(node,ast.Name) else None
    issues=[]
    for node in ast.walk(tree):
        if isinstance(node,ast.Call):
            call=dotted(node.func)
            if call.startswith('bpy.ops.render.'):
                issues.append({'line':node.lineno,'code':'use_render_queue','message':'Authoring cannot invoke render operators. Prepare/save cameras only; call blender_render_view for queued CPU rendering.'})
            if call in {'bpy.data.meshes.remove','bpy.data.cameras.remove','bpy.data.lights.remove'} and node.args and isinstance(node.args[0],ast.Attribute) and node.args[0].attr=='data':
                issues.append({'line':node.lineno,'code':'live_object_data_removal','message':'Do not remove obj.data while obj still uses it: Blender can invalidate the Object, causing StructRNA ReferenceError on the next access. Save data = obj.data; call bpy.data.objects.remove(obj, do_unlink=True) first; only then remove the saved datablock if data.users == 0. Collecting object names does not repair this deletion-order bug.'})
            if call in {'os.mkdir','os.makedirs'} or (isinstance(node.func,ast.Attribute) and node.func.attr=='mkdir'):
                path=string(node.args[0]) if node.args else None
                if path!='/job':
                    issues.append({'line':node.lineno,'code':'flat_outputs_only','message':'Authoring outputs must be flat /job files; do not create output subdirectories. Queued render tools manage render artifacts.'})
        if isinstance(node,ast.Attribute):
            name=dotted(node)
            if name.endswith(('.render.image_format','.render.file_format')):
                issues.append({'line':node.lineno,'code':'render_settings_api','message':'Use scene.render.image_settings.file_format. Never scene.render.image_format or scene.render.file_format.'})
            if node.attr=='calc_normals':
                issues.append({'line':node.lineno,'code':'mesh_api','message':'Mesh.calc_normals is unavailable; use supported mesh update/normal APIs verified against this runtime.'})
        if isinstance(node,ast.Subscript) and string(node.slice)=='Clearcoat':
            issues.append({'line':node.lineno,'code':'principled_api','message':'The legacy Clearcoat input is unavailable; supported Principled input is Coat Weight.'})
    if issues:
        return {'ok':False,'recoverable':True,'code':'authoring_preflight','submitted':False,'attempt_consumed':False,
                'issues':issues,'next_tool':'blender_render_view' if any(i['code']=='use_render_queue' for i in issues) else 'blender_scene_author'}
    return {'ok':True}
