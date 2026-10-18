import bpy, os, math, sys
from mathutils import Vector
ROOT=os.path.dirname(os.path.abspath(__file__))
scene=bpy.context.scene
scene.render.resolution_x=720;scene.render.resolution_y=1280;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
cam=scene.camera
def aim(loc,target,lens=58):
    cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens
    cam.data.dof.focus_object=None;cam.data.dof.focus_distance=(Vector(target)-cam.location).length
    cam.data.dof.aperture_fstop=4

if '--glb' in sys.argv:
    bpy.ops.export_scene.gltf(filepath=ROOT+'/original_furniture_reveal.glb',export_format='GLB',export_cameras=True,export_lights=True,export_animations=True,export_frame_range=True)

if '--angles' in sys.argv:
    scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=48;scene.cycles.use_denoising=False
    scene.cycles.max_bounces=6;scene.cycles.diffuse_bounces=3;scene.cycles.glossy_bounces=3
    scene.render.resolution_x=720;scene.render.resolution_y=1280
    # Independently composed camera angles for purposeful editorial cutting.
    for name,frame,loc,tgt,lens in [
      ('hero_main',1,(4.3,-7.3,3.1),(0,0,1.05),52),
      ('velvet_macro',1,(1.6,-1.80,1.20),(1.15,-.35,.85),64),
      ('oak_structure',250,(1.65,-2.3,1.12),(0,-.1,.38),60),
      ('top_down',250,(0,-.1,6.1),(0,0,.75),32),
      ('hero_side',1,(-4.1,-4.3,2.1),(0,0,.93),58),
      ('exploded_reveal',250,(-3.8,-7.3,3.6),(0,0,1.45),52)
    ]:
        scene.frame_set(frame);aim(loc,tgt,lens);scene.render.filepath=ROOT+'/'+name+'.png';bpy.ops.render.render(write_still=True)

if '--workbench-test' in sys.argv or '--workbench' in sys.argv:
    scene.render.engine='BLENDER_WORKBENCH'
    sh=scene.display.shading;sh.light='STUDIO';sh.studio_light='paint.sl';sh.color_type='MATERIAL';sh.show_shadows=True;sh.show_cavity=True;sh.cavity_type='BOTH';sh.curvature_ridge_factor=1.2;sh.curvature_valley_factor=1.1
    sh.show_specular_highlight=True;sh.background_type='WORLD';sh.show_object_outline=False
    for mat in bpy.data.materials:
        if mat.use_nodes:
            bs=mat.node_tree.nodes.get('Principled BSDF')
            if bs:mat.diffuse_color=bs.inputs['Base Color'].default_value
    if '--workbench-test' in sys.argv:
        scene.frame_set(200);scene.render.filepath=ROOT+'/workbench_test.png';bpy.ops.render.render(write_still=True)
    else:
        scene.frame_start=1;scene.frame_end=300
        os.makedirs(ROOT+'/workbench_frames',exist_ok=True);scene.render.filepath=ROOT+'/workbench_frames/';bpy.ops.render.render(animation=True)
