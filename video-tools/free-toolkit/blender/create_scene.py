import bpy, math, os, sys, json
from mathutils import Vector

ROOT=os.path.dirname(os.path.abspath(__file__))
os.makedirs(ROOT,exist_ok=True)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene
scene.render.engine='BLENDER_EEVEE_NEXT'
scene.eevee.taa_render_samples=32
scene.render.resolution_x=720; scene.render.resolution_y=1280
scene.render.resolution_percentage=100
scene.render.fps=30; scene.frame_start=1; scene.frame_end=300
scene.render.image_settings.file_format='PNG'; scene.render.film_transparent=False
scene.render.image_settings.color_mode='RGB'
scene.world.color=(.015,.02,.03)
world=scene.world; world.use_nodes=True
world.node_tree.nodes['Background'].inputs['Color'].default_value=(.017,.025,.045,1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value=.25
scene.view_settings.view_transform='AgX'
scene.view_settings.look='AgX - Medium High Contrast'
scene.render.filepath=ROOT+'/frames/'
scene.render.use_file_extension=True

def material(name,color,metallic=0,roughness=.5):
    m=bpy.data.materials.new(name); m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value=(*color,1)
    bs.inputs['Metallic'].default_value=metallic
    bs.inputs['Roughness'].default_value=roughness
    return m

velvet=material('Original midnight blue velvet',(.024,.072,.105),0,.68)
n=velvet.node_tree.nodes; l=velvet.node_tree.links; bs=n.get('Principled BSDF')
bs.inputs['Sheen Weight'].default_value=.65
bs.inputs['Sheen Roughness'].default_value=.45
bs.inputs['Sheen Tint'].default_value=(.16,.29,.32,1)
tex=n.new('ShaderNodeTexNoise'); tex.inputs['Scale'].default_value=240; tex.inputs['Detail'].default_value=2
bump=n.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=.15; bump.inputs['Distance'].default_value=.0018
l.new(tex.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs['Normal'],bs.inputs['Normal'])
noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=8;noise.inputs['Detail'].default_value=3
ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(.009,.031,.055,1);ramp.color_ramp.elements[1].color=(.036,.103,.128,1)
l.new(noise.outputs['Fac'],ramp.inputs[0]);l.new(ramp.outputs[0],bs.inputs['Base Color'])

oak=material('Natural oak procedural grain',(.35,.19,.075),0,.38)
n=oak.node_tree.nodes;l=oak.node_tree.links;bs=n.get('Principled BSDF')
coord=n.new('ShaderNodeTexCoord');mapping=n.new('ShaderNodeMapping'); mapping.inputs['Scale'].default_value=(2,45,45)
noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=3;noise.inputs['Detail'].default_value=4;noise.inputs['Roughness'].default_value=.7
r=n.new('ShaderNodeValToRGB');r.color_ramp.elements[0].position=.2;r.color_ramp.elements[0].color=(.10,.047,.015,1);r.color_ramp.elements[1].position=.78;r.color_ramp.elements[1].color=(.55,.32,.13,1)
l.new(coord.outputs['Generated'],mapping.inputs['Vector']);l.new(mapping.outputs[0],noise.inputs['Vector']);l.new(noise.outputs[0],r.inputs[0]);l.new(r.outputs[0],bs.inputs['Base Color'])
b=n.new('ShaderNodeBump');b.inputs['Strength'].default_value=.14;b.inputs['Distance'].default_value=.001;l.new(noise.outputs[0],b.inputs['Height']);l.new(b.outputs[0],bs.inputs['Normal'])
brass=material('Brushed champagne brass',(.52,.36,.13),.85,.32)
black=material('Blackened steel',(.016,.022,.026),.8,.28)
seam=material('Woven seam blue',(.018,.050,.070),0,.78)
canvas=material('Undyed jute lining',(.47,.39,.27),0,.9)
n=canvas.node_tree.nodes;l=canvas.node_tree.links;bs=n.get('Principled BSDF');tex=n.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=180
b=n.new('ShaderNodeBump');b.inputs['Strength'].default_value=.2;b.inputs['Distance'].default_value=.002;l.new(tex.outputs[0],b.inputs['Height']);l.new(b.outputs[0],bs.inputs['Normal'])
floor=material('Charcoal concrete stage',(.027,.037,.047),.15,.32)
n=floor.node_tree.nodes;l=floor.node_tree.links;bs=n.get('Principled BSDF');tex=n.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=22;tex.inputs['Detail'].default_value=3
b=n.new('ShaderNodeBump');b.inputs['Strength'].default_value=.1;b.inputs['Distance'].default_value=.012;l.new(tex.outputs[0],b.inputs['Height']);l.new(b.outputs[0],bs.inputs['Normal'])

upholstery=[]
def box(name,loc,dims,mat,bevel=.03,soft=False):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name
    o.dimensions=dims;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(mat)
    if bevel:
        b=o.modifiers.new('Tailored rounded edges','BEVEL');b.width=bevel;b.segments=6 if soft else 3
        b.profile=.65 if soft else .5
        b.affect='EDGES'
    if soft:
        s=o.modifiers.new('Upholstery smoothing','SUBSURF');s.levels=2;s.render_levels=2
    else:
        w=o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    for p in o.data.polygons:p.use_smooth=True
    return o

def pipe(name,pts,r,mat):
    curve=bpy.data.curves.new(name,'CURVE');curve.dimensions='3D';curve.resolution_u=16
    sp=curve.splines.new('BEZIER');sp.bezier_points.add(len(pts)-1)
    for p,co in zip(sp.bezier_points,pts): p.co=co;p.handle_left_type='AUTO';p.handle_right_type='AUTO'
    curve.bevel_depth=r;curve.bevel_resolution=3
    ob=bpy.data.objects.new(name,curve);scene.collection.objects.link(ob);ob.data.materials.append(mat)
    return ob

# Actual timber infrastructure: two long side rails, cross braces and separate slats.
box('Front hardwood structural rail',(0,-.46,.35),(2.82,.105,.16),oak,.015)
box('Rear hardwood structural rail',(0,.46,.35),(2.82,.105,.16),oak,.015)
box('Left hardwood structural rail',(-1.36,0,.35),(.11,.9,.16),oak,.015)
box('Right hardwood structural rail',(1.36,0,.35),(.11,.9,.16),oak,.015)
for x in [-.7,0,.7]:box('Frame cross brace',(x,0,.34),(.065,.9,.12),oak,.008)
for x in [-1.18+i*.196 for i in range(13)]:box('Individual oak seat support slat',(x,0,.42),(.105,.87,.045),oak,.009)
for x in [-1.27,1.27]:
    for y in [-.38,.38]:
        box('Tapered champagne metal foot',(x,y,.145),(.055,.055,.29),brass,.016)
        bpy.ops.mesh.primitive_uv_sphere_add(segments=20,ring_count=12,radius=.012,location=(x,y,.305));bpy.context.object.data.materials.append(black)

# Three deliberately original modular cushions, no brand asset or copied product design.
base=box('Floating upholstered base',(0,0,.53),(3.08,1.13,.29),velvet,.14,True);upholstery.append((base,.92))
for i,x in enumerate([-1.0,0,1.0]):
    c=box('Deep plush seat '+str(i+1),(x,-.13,.74),(.99,.9,.25),velvet,.115,True);upholstery.append((c,1.12+i*.025))
    c=box('Relaxed pillowed back '+str(i+1),(x,.40,1.13),(.99,.28,.76),velvet,.13,True);c.rotation_euler.x=math.radians(9);upholstery.append((c,1.0))
    # Fine tailored front piping is tangible, subtle, and not a graphic outline.
    p=pipe('Seat seam '+str(i+1),[(x-.42,-.566,.756),(x,-.579,.751),(x+.42,-.566,.756)],.003,seam);upholstery.append((p,1.12+i*.025))
for x in [-1.53,1.53]:
    c=box('Rounded upholstered arm',(x,0,.88),(.30,1.19,.67),velvet,.143,True);upholstery.append((c,1.0))

# A slim hand-made side table and physical material rolls give believable scale, not a fake factory.
box('Oak material worktable',(-2.3,.8,.79),(.95,.72,.055),oak,.018)
for x in [-2.65,-1.95]:
    for y in [.55,1.05]:box('Table steel leg',(x,y,.4),(.035,.035,.76),black,.01)
for i in range(4):
    sw=box('Folded material sample '+str(i),(-2.3+.025*i,.8,.83+.024*i),(.36,.28,.021),canvas if i%2 else velvet,.012)
    sw.rotation_euler.z=math.radians(-13+7*i)
for j in range(3):
    o=box('Leaning oak stock '+str(j),(2.25+j*.15,.9,1.3),(.10,.14,2.5),oak,.012)
    o.rotation_euler.y=math.radians(-7-j*2)

box('Large studio ground',(0,0,-.05),(200,200,.1),floor,.01)

def area(name,loc,power,color,size,target,shape='DISK',size_y=None):
    bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name=name;o.data.energy=power;o.data.color=color;o.data.shape=shape;o.data.size=size
    if size_y is not None:o.data.size_y=size_y
    o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();return o
area('Warm oversized key',(-3.5,-4,5),1400,(1,.79,.56),4,(0,0,.7))
area('Cool soft fill',(3,-2.5,2.8),700,(.46,.68,1),3,(0,0,.7))
area('Gold edge strip',(0,2.8,4),1850,(1,.72,.37),3.4,(0,0,1),'RECTANGLE',.9)
area('Upper velvet grazing light',(-1,0,5),1000,(.75,.87,1),2.5,(0,0,.8))
area('Workshop pool',(-3,2,3),300,(1,.6,.3),1.5,(-2.2,.8,.8))

# A real perspective camera with animated dolly, orbit, focus and focal length.
bpy.ops.object.camera_add();cam=bpy.context.object;cam.name='Cinematic real dolly camera';scene.camera=cam
cam.data.lens=52;cam.data.sensor_width=36;cam.data.dof.use_dof=True;cam.data.dof.aperture_fstop=5.6
bpy.ops.object.empty_add(type='PLAIN_AXES',location=(0,0,.9));focus=bpy.context.object;focus.name='Camera focus target';cam.data.dof.focus_object=focus
keys=[
    (1,(4.3,-7.3,3.1),(0,0,1.05),52),
    (76,(3.4,-6.8,2.55),(0,0,1.0),52),
    (145,(2.2,-7.7,3.8),(0,0,1.3),52),
    (225,(-2.6,-7.6,4.2),(0,0,1.5),52),
    (300,(-3.8,-7.3,3.6),(0,0,1.45),52)
]
for frame,loc,tgt,lens in keys:
    cam.location=loc;cam.rotation_euler=(Vector(tgt)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens
    cam.keyframe_insert(data_path='location',frame=frame);cam.keyframe_insert(data_path='rotation_euler',frame=frame);cam.data.keyframe_insert(data_path='lens',frame=frame)
    focus.location=tgt;focus.keyframe_insert(data_path='location',frame=frame)
for ob,lift in upholstery:
    start=ob.location.copy()
    for f,dz in [(1,0),(80,0),(170,lift),(300,lift)]:
        ob.location=start+Vector((0,0,dz));ob.keyframe_insert(data_path='location',frame=f)
for ob in [cam,focus]+[o for o,_ in upholstery]:
    if ob.animation_data and ob.animation_data.action:
        for fc in ob.animation_data.action.fcurves:
            for k in fc.keyframe_points:k.interpolation='BEZIER'

scene.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=ROOT+'/original_furniture_reveal.blend')
open(ROOT+'/PROVENANCE.json','w').write(json.dumps({'creator':'Original procedural scene made in Blender for this video','assets':'All geometry, materials, lights and camera authored in create_scene.py. No downloaded model, texture, brand mark or source video frame.','meaning':'Illustrative furniture production and assembly, not an actual GUMA or Saloni product or facility.','software':'Blender 4.3.2, GNU GPL','render':'720x1280, 30fps, Eevee, 32 samples'},indent=2))

if '--preview' in sys.argv:
    for f in [1,145,250]:
        scene.frame_set(f);scene.render.filepath=ROOT+f'/preview_{f:03}.png';bpy.ops.render.render(write_still=True)
if '--animate' in sys.argv:
    os.makedirs(ROOT+'/frames',exist_ok=True);scene.render.filepath=ROOT+'/frames/';bpy.ops.render.render(animation=True)
