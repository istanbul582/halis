import bpy,os
ROOT=os.path.dirname(os.path.abspath(__file__))
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=12;s.cycles.use_denoising=False;s.cycles.max_bounces=3;s.cycles.diffuse_bounces=2;s.cycles.glossy_bounces=2
s.render.resolution_x=360;s.render.resolution_y=640;s.render.resolution_percentage=100
s.frame_set(1);s.render.filepath=ROOT+'/quick_hero.png';bpy.ops.render.render(write_still=True)
