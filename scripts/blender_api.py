"""Bounded installed-API lookup and conservative typed Python preflight."""
import ast
import difflib
import hashlib
import json
from pathlib import Path
import re


def load_catalog(root):
    root=Path(root);path=root/'artifacts/reports/blender-api-catalog.json'
    if not path.exists():return None
    receipt=json.loads((root/'artifacts/reports/blender-api-catalog-receipt.json').read_text())
    data=path.read_bytes()
    if hashlib.sha256(data).hexdigest()!=receipt['sha256']:raise ValueError('Installed API catalog hash changed')
    catalog=json.loads(data)
    if catalog['version']!='5.2.3 LTS':raise ValueError('API catalog belongs to another Blender runtime')
    return catalog


def lookup(catalog,query,limit=12):
    query=query.strip();types=catalog['types'];operators=catalog['operators']
    if query in operators:return {'query':query,'operator':operators[query]}
    if query in catalog['extras']:return {'query':query,**catalog['extras'][query]}
    if query.startswith('bpy.data.') and query[9:] in catalog['data_collections']:
        return {'query':query,**catalog['data_collections'][query[9:]]}
    name=query.removeprefix('bpy.types.')
    if name in types:return {'query':query,'type':name,**types[name]}
    if '.' in name:
        owner,member=name.rsplit('.',1)
        if owner in types:
            data=types[owner]
            return {'query':query,'available':member in data['members'],'function':data['functions'].get(member),
                'property':data['properties'].get(member),'suggestions':difflib.get_close_matches(member,data['members'],n=8)}
    matches=[key for key in operators if query.lower() in key.lower()]
    matches+=['bpy.types.'+key for key in types if query.lower() in key.lower()]
    matches+=['bpy.types.'+key+'.'+member for key,data in types.items() for member in data['members'] if query.lower() in member.lower()]
    return {'query':query,'matches':matches[:limit],'total_matches':len(matches),'next':'Query an exact bpy.types.Type, Type.member or bpy.ops.category.operator for supported parameters.'}


def inspect_api(code,catalog):
    checker=ApiChecker(catalog);checker.visit(ast.parse(code));return checker.issues


class ApiChecker(ast.NodeVisitor):
    def __init__(self,catalog):
        self.catalog=catalog;self.env={};self.issues=[]

    def raw(self,node):
        if isinstance(node,ast.Name):return node.id
        if isinstance(node,ast.Attribute):return self.raw(node.value)+'.'+node.attr
        return ''

    def resolve(self,node):
        if isinstance(node,ast.Name):return self.env.get(node.id)
        if isinstance(node,ast.Attribute):
            override=self.env.get(self.raw(node))
            if override:return override
            base=self.resolve(node.value)
            if not base:return None
            kind,key=base
            if kind=='path':
                path=key+'.'+node.attr
                if key=='bpy.data' and node.attr in self.catalog['data_collections']:return ('data_collection',node.attr)
                if key=='bpy.types' and node.attr in self.catalog['types']:return ('class',node.attr)
                if path=='bpy.context.scene':return ('type','Scene')
                if path in {'bpy.context.object','bpy.context.active_object'}:return ('type','Object')
                return ('path',path)
            if kind=='data_collection' and node.attr in {'new','get'}:return ('factory',self.catalog['data_collections'][key]['target'])
            if kind=='collection' and node.attr in {'get','__getitem__'}:return ('factory',key)
            if kind=='type':
                prop=self.catalog['types'].get(key,{}).get('properties',{}).get(node.attr)
                if key=='Object' and node.attr=='data':return None  # Runtime-polymorphic, unless explicitly narrowed.
                if prop and prop.get('target'):
                    return ('collection' if prop['type']=='COLLECTION' else 'type',prop['target'])
                extra={'bmesh.types.BMesh':{'verts':'bmesh.types.BMVertSeq','edges':'bmesh.types.BMEdgeSeq','faces':'bmesh.types.BMFaceSeq'}}.get(key,{})
                if node.attr in extra:return ('type',extra[node.attr])
            return None
        if isinstance(node,ast.Subscript):
            base=self.resolve(node.value)
            if base and base[0] in {'data_collection','collection'}:
                return ('type',self.catalog['data_collections'][base[1]]['target'] if base[0]=='data_collection' else base[1])
        if isinstance(node,ast.Call):
            value=self.resolve(node.func)
            if value and value[0] in {'factory','class'}:return ('type',value[1])
            if value==('path','bmesh.new'):return ('type','bmesh.types.BMesh')
            if value and value[0]=='path' and value[1] in self.catalog['extras']:return ('type',value[1])
        return None

    def issue(self,node,code,path,message,suggestions=None):
        self.issues.append({'line':node.lineno,'code':code,'api':path,'message':message,'suggestions':suggestions or [],'next_tool':'blender_api_lookup'})

    def visit_Import(self,node):
        for item in node.names:self.env[item.asname or item.name.split('.')[0]]=('path',item.name if item.asname else item.name.split('.')[0])

    def visit_ImportFrom(self,node):
        for item in node.names:
            self.env[item.asname or item.name]=('class',item.name) if node.module=='bpy.types' and item.name in self.catalog['types'] else ('path',(node.module or '')+'.'+item.name)

    def visit_Assign(self,node):
        self.visit(node.value);value=self.resolve(node.value)
        for target in node.targets:
            if isinstance(target,ast.Name):
                if value:self.env[target.id]=value
                else:self.env.pop(target.id,None)
            else:self.visit(target)

    def visit_AnnAssign(self,node):
        self.generic_visit(node);value=self.resolve(node.annotation)
        if isinstance(node.target,ast.Name) and value and value[0]=='class':self.env[node.target.id]=('type',value[1])

    def visit_FunctionDef(self,node):
        old=self.env;self.env=dict(old)
        for argument in node.args.posonlyargs+node.args.args+node.args.kwonlyargs:
            self.env.pop(argument.arg,None)
            value=self.resolve(argument.annotation)
            if value and value[0]=='class':self.env[argument.arg]=('type',value[1])
        for statement in node.body:self.visit(statement)
        self.env=old

    def visit_If(self,node):
        self.visit(node.test);old=dict(self.env)
        test=node.test
        if isinstance(test,ast.Compare) and len(test.ops)==1 and isinstance(test.ops[0],ast.Eq) and isinstance(test.left,ast.Attribute) and test.left.attr=='type' and isinstance(test.comparators[0],ast.Constant):
            kind={'MESH':'Mesh','CAMERA':'Camera','LIGHT':'Light'}.get(str(test.comparators[0].value))
            if kind:self.env[self.raw(test.left.value)+'.data']=('type',kind)
        # Also narrow the common `obj is not None and obj.type == 'MESH'` guard.
        if isinstance(test,ast.BoolOp) and isinstance(test.op,ast.And):
            for condition in test.values:
                if isinstance(condition,ast.Compare) and len(condition.ops)==1 and isinstance(condition.ops[0],ast.Eq) and isinstance(condition.left,ast.Attribute) and condition.left.attr=='type' and isinstance(condition.comparators[0],ast.Constant):
                    kind={'MESH':'Mesh','CAMERA':'Camera','LIGHT':'Light'}.get(str(condition.comparators[0].value))
                    if kind:self.env[self.raw(condition.left.value)+'.data']=('type',kind)
        for statement in node.body:self.visit(statement)
        self.env=dict(old)
        for statement in node.orelse:self.visit(statement)
        self.env=old

    def visit_Attribute(self,node):
        base=self.resolve(node.value)
        if base and base[0]=='data_collection' and node.attr not in self.catalog['data_collections'][base[1]]['members']:
            self.issue(node,'unsupported_member','bpy.data.'+base[1]+'.'+node.attr,'Datablock collection member is absent from the installed runtime.')
        if base and base[0] in {'type','class'}:
            data=self.catalog['types'].get(base[1]) or self.catalog['extras'].get(base[1])
            if data and node.attr not in data['members'] and not node.attr.startswith('_'):
                self.issue(node,'unsupported_member',base[1]+'.'+node.attr,'This member is absent from the installed Blender API. Unknown receiver types are not rejected.',difflib.get_close_matches(node.attr,data['members'],n=5))
        self.generic_visit(node)

    def visit_Call(self,node):
        target=self.resolve(node.func);parameters=None
        if target and target[0]=='path' and target[1].startswith('bmesh.ops.') and target[1].split('.')[-1] not in self.catalog['bmesh_ops']:
            self.issue(node,'unsupported_operator',target[1],'BMesh operator is absent from this installed runtime.',difflib.get_close_matches(target[1].split('.')[-1],self.catalog['bmesh_ops'],n=5))
        if target and target[0]=='path' and target[1].startswith('bpy.ops.'):
            op=self.catalog['operators'].get(target[1])
            if op:parameters=op['parameters']
            elif target[1].rsplit('.',1)[-1] in {'poll','get_rna_type'} and target[1].rsplit('.',1)[0] in self.catalog['operators']:
                parameters={}
            elif target[1] not in self.catalog['errors']:
                self.issue(node,'unsupported_operator',target[1],'Operator is absent from this installed runtime.',difflib.get_close_matches(target[1],self.catalog['operators'],n=5))
        if isinstance(node.func,ast.Attribute):
            owner=self.resolve(node.func.value)
            if owner and owner[0]=='type':parameters=self.catalog['types'].get(owner[1],{}).get('functions',{}).get(node.func.attr)
        if parameters is not None:
            for keyword in node.keywords:
                if keyword.arg is not None and keyword.arg not in parameters:self.issue(node,'unsupported_keyword',ast.unparse(node.func),f'Unsupported keyword {keyword.arg!r}; accepted keywords: '+', '.join(parameters))
        self.generic_visit(node)


def classify_api_error(catalog,diagnostics):
    """Only classify a concrete absent RNA member, never generic Attribute/TypeErrors."""
    logs='\n'.join(log.get('text','') for log in diagnostics.get('logs',{}).values())
    exceptions=re.findall(r'^([A-Za-z_]\w*(?:Error|Exception)): (.+)$',logs,re.M)
    if not exceptions or exceptions[-1][0]!='AttributeError':return None
    missing_operator=re.fullmatch(r'Calling operator "(bpy\.ops\.[\w.]+)" error, could not be found',exceptions[-1][1])
    if missing_operator and missing_operator[1] not in catalog['operators'] and missing_operator[1] not in catalog['errors']:
        return {'category':'api_correction','operator':missing_operator[1],'message':'Operator absent from installed Blender '+catalog['version']}
    for owner,member in re.findall(r"^'([^']+)' object has no attribute '([^']+)'$",exceptions[-1][1]):
        data=catalog['types'].get(owner)
        if data and member not in data['members']:
            return {'category':'api_correction','type':owner,'member':member,'message':owner+'.'+member+' is absent from Blender '+catalog['version'],
                'suggestions':difflib.get_close_matches(member,data['members'],n=5)}
    return None
