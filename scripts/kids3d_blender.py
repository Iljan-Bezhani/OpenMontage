#!/usr/bin/env python3
"""Procedural real 3D animated short: PIP & PUFF / PIZZA WEATHER.

Run: blender -b -t 2 --python scripts/kids3d_blender.py -- kids3d-build/timeline.json
All characters, props, camera movement, walk cycles and pizza storm are generated
as editable Blender meshes with keyframed animation. Rendered with Workbench.
"""
import bpy
import json
import math
import sys
from pathlib import Path
from mathutils import Vector

def args_after_dash():
    return sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []

timeline_path = Path(args_after_dash()[0] if args_after_dash() else "kids3d-build/timeline.json")
data = json.loads(timeline_path.read_text())
FPS = 12
END = math.ceil(float(data["duration"]) * FPS)
STORM = float(data["storm_at"])
S = lambda t: max(1, min(END, round(t*FPS)+1))
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
for mat in list(bpy.data.materials):
    bpy.data.materials.remove(mat)

def mat(name,color):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*color,1.0)
    return m

white=mat("Marshmallow white",(.96,.98,1.0))
pale=mat("Cloud highlight",(.78,.90,1.0))
blue=mat("Iris blue",(.20,.39,.66))
black=mat("Chocolate eyes",(.13,.16,.22))
shine=mat("Bright eye reflections",(1,1,1))
orange=mat("Pip orange",(.98,.39,.12))
orange_light=mat("Pip warm cheeks",(1.0,.60,.34))
green=mat("Leaf bright green",(.18,.72,.32))
green_dark=mat("Leaf deep green",(.10,.48,.24))
pink=mat("Soft pink",(.98,.40,.60))
mouthmat=mat("Open mouths",(.41,.16,.24))
grass=mat("Mint grass",(.34,.78,.48))
grass2=mat("Soft forest meadow",(.24,.66,.42))
groundmat=mat("Peach ground",(.94,.86,.68))
yellow=mat("Golden cheese",(1.0,.79,.20))
cheese2=mat("Light cheese",(1.0,.90,.36))
crust=mat("Baked crust",(.85,.47,.19))
red=mat("Tomato pepperoni",(.83,.17,.20))
sunmat=mat("Sun golden",(.99,.77,.22))
sunlight=mat("Sun rays",(1.0,.90,.36))
skybits=mat("Little trees",(.31,.69,.54))

def empty(name, xyz=(0,0,0), parent=None):
    obj=bpy.data.objects.new(name,None)
    bpy.context.collection.objects.link(obj)
    obj.location=xyz
    if parent: obj.parent=parent
    return obj

def uv(name,loc=(0,0,0),scale=(1,1,1),material=white,parent=None,seg=24,rings=12):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg,ring_count=rings,location=(0,0,0))
    o=bpy.context.object
    o.name=name
    if parent: o.parent=parent
    o.location=loc
    o.scale=scale
    o.data.materials.append(material)
    for p in o.data.polygons: p.use_smooth=True
    return o

def cyl(name,loc,radius,depth,material,parent=None,vertices=24):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=depth,location=(0,0,0))
    o=bpy.context.object; o.name=name
    if parent:o.parent=parent
    o.location=loc;o.data.materials.append(material)
    for p in o.data.polygons:p.use_smooth=True
    return o

def key(obj,prop,tm):
    obj.keyframe_insert(data_path=prop,frame=S(tm))

def say_mouth(obj,speaker):
    for item in data["lines"]:
        if item["speaker"]!=speaker:continue
        start=float(item["start"]);end=start+float(item["duration"])
        for t,v in [(start-0.09,0.10),(start,0.72)]:
            obj.scale.z=v;key(obj,"scale",t)
        n=0
        t=start
        while t<end:
            obj.scale.z=0.75 if n%2==0 else 0.16
            key(obj,"scale",t)
            t+=0.19
            n+=1
        obj.scale.z=0.13;key(obj,"scale",end+0.03)

# Infinite pastel stage with actual 3D depth
cyl("Floating green meadow",(0,0,-0.39),7.6,.67,grass,vertices=96)
cyl("Sunlit edge",(0,0,-0.78),7.35,.22,grass2,vertices=96)
for i in range(32):
    angle=i*2*math.pi/32
    radius=6.0+(i%3)*.24
    x,y=radius*math.cos(angle),radius*math.sin(angle)
    if y < -1.9: continue
    uv("Meadow flower", (x,y,.03),(.10,.10,.12),pink if i%3==0 else yellow)
    cyl("Meadow stem",(x,y,-.1),.022,.2,green,vertices=8)

# Some round toy trees in the back
for tx,ty,sc in [(-5,2,.82),(5,2.2,1.1),(-3.9,4,.52),(3.8,4,.62)]:
    cyl("tree trunk",(tx,ty,.56*sc),.17*sc,1.12*sc,crust)
    uv("round happy tree",(tx,ty,1.35*sc),(.65*sc,.54*sc,.76*sc),skybits)

# Pip is a genuine tapered 3D carrot character with legs/arms and facial animation
pip=empty("Pip - the dancing carrot",(2.25,-.1,1.66))
verts=[];faces=[];n=32
levels=[(-1.09,.08),(-.76,.26),(-.30,.45),(.15,.60),(.66,.57),(.95,.32),(1.01,.05)]
for z,rad in levels:
    for j in range(n):
        a=2*math.pi*j/n
        verts.append((math.cos(a)*rad,math.sin(a)*rad,z))
for k in range(len(levels)-1):
    for j in range(n):
        a=k*n+j;b=k*n+(j+1)%n;c=(k+1)*n+(j+1)%n;d=(k+1)*n+j
        faces.append((a,b,c,d))
faces.append(tuple(reversed(tuple(range(n)))))
faces.append(tuple((len(levels)-1)*n+j for j in range(n)))
mesh=bpy.data.meshes.new("Pip tapered carrot skin")
mesh.from_pydata(verts,[],faces)
mesh.update()
carrot=bpy.data.objects.new("Pip's rounded cone body",mesh)
bpy.context.collection.objects.link(carrot)
carrot.parent=pip
carrot.data.materials.append(orange)
for p in carrot.data.polygons:p.use_smooth=True
for dx in (-.23,.23):
    uv("Pip eyeball",(dx,-.57,.40),(.19,.135,.25),white,pip)
    uv("Pip pupil",(dx*1.11,-.70,.38),(.088,.063,.13),black,pip)
    uv("Pip eye shine",(dx*1.13-.027,-.761,.44),(.035,.023,.041),shine,pip)
    uv("Pip rosy cheek",(dx*1.95,-.39,.05),(.14,.055,.088),orange_light,pip)
pipmouth=uv("Pip expressive mouth",(0,-.57,-.04),(.17,.071,.12),mouthmat,pip)
pipmouth.scale.z=.13
for a in [-.35,0,.35]:
    leaf=uv("Pip green leaf",(a*.56,0,1.22),(.18,.14,.47),green if a!=0 else green_dark,pip)
    leaf.rotation_euler.y=-a*.60
piplegs=[]
piparms=[]
for sgn in (-1,1):
    leg=empty("Pip articulated leg",(.23*sgn,-.015,-.9),pip)
    uv("Pip leg",(.0,-.02,-.35),(.095,.10,.41),orange,leg)
    uv("Pip shoe",(.0,-.23,-.67),(.20,.32,.14),blue,leg)
    piplegs.append(leg)
    arm=empty("Pip articulated arm",(.57*sgn,0,.32),pip)
    arm.rotation_euler.y=-sgn*.28
    uv("Pip arm",(.18*sgn,-.02,-.30),(.12,.13,.39),orange,arm)
    uv("Pip hand",(.34*sgn,-.02,-.58),(.17,.17,.17),orange_light,arm)
    piparms.append(arm)

# Puff assembled as volumetric-looking 3D lobes; googly eyes and articulated arms
puff=empty("Puff - a fluffy three-dimensional cloud",(-2.30,0,2.45))
for loc,scale,material in [
    ((-.79,.12,-.03),(.58,.55,.61),white),((0,.12,.22),(.85,.68,.72),white),
    ((.86,.12,-.09),(.58,.59,.57),white),((-.37,-.11,.44),(.63,.62,.64),pale),
    ((.42,-.05,.47),(.65,.58,.66),white),((0,-.03,-.28),(1.13,.48,.42),white)
]:
    uv("Fluffy cloud lobe",loc,scale,material,puff)
for dx in (-.37,.37):
    uv("Puff large eyeball",(dx,-.67,.20),(.23,.16,.27),white,puff)
    uv("Puff iris",(dx,-.813,.19),(.11,.075,.14),blue,puff)
    uv("Puff pupil",(dx,-.866,.19),(.064,.043,.10),black,puff)
    uv("Puff catchlight",(dx-.035,-.905,.25),(.030,.02,.037),shine,puff)
    uv("Puff peach blush",(dx*1.82,-.53,-.12),(.17,.064,.10),pink,puff)
puffmouth=uv("Puff animated happy mouth",(0,-.70,-.21),(.19,.08,.15),mouthmat,puff)
puffmouth.scale.z=.13
puffarms=[]
for sg in (-1,1):
    arm=empty("Puff wing arm",(sg*1.17,.10,-.06),puff)
    uv("Puff little arm",(sg*.26,-.08,-.14),(.38,.16,.16),white,arm)
    uv("Puff mitten",(sg*.53,-.08,-.17),(.17,.18,.19),pale,arm)
    puffarms.append(arm)

# Warm stylized 3D sun, floating behind everyone
sun=empty("Happy sun",(3.95,3.1,4.6))
uv("Sunny face",(0,0,0),(.69,.27,.68),sunmat,sun)
for i in range(12):
    a=i*math.pi/6
    ray=uv("3D sunshine ray",(math.cos(a)*.85,0,math.sin(a)*.85),(.13,.12,.29),sunlight,sun)
    ray.rotation_euler.y=a+math.pi/2
for dx in (-.21,.21):
    uv("Sun eye",(dx,-.28,.13),(.065,.042,.10),black,sun)
uv("Sun smile",(0,-.30,-.22),(.20,.050,.068),crust,sun)

# 3D pizza rain. Each slice is a shaped, textured cheese wedge with crust and toppings.
pizza=[]
def pizza_slice(ix, x, y):
    root=empty("Pizza slice %02d"%ix,(x,y,5.9))
    # The triangle faces camera (negative Y).
    coords=[(-.50,0,.37),(.50,0,.37),(0,0,-.69),(-.50,.12,.37),(.50,.12,.37),(0,.12,-.69)]
    faces=[(0,2,1),(3,4,5),(0,1,4,3),(1,2,5,4),(2,0,3,5)]
    mesh=bpy.data.meshes.new("Cheesy 3D slice mesh")
    mesh.from_pydata(coords,[],faces);mesh.update()
    wedge=bpy.data.objects.new("Golden cheese wedge",mesh)
    bpy.context.collection.objects.link(wedge);wedge.parent=root
    wedge.data.materials.append(yellow)
    uv("Pizza crust",(0,-.04,.39),(.55,.18,.17),crust,root)
    for dx,dz in [(-.25,.11),(.23,.14),(0,-.28)]:
        uv("Pizza pepperoni",(dx,-.095,dz),(.13,.055,.13),red,root)
    root.rotation_euler=(0,0,(ix%3-1)*.26)
    return root

for i in range(11):
    x=-4.3+(i%6)*1.65
    y=-.45+(i%3)*.16
    o=pizza_slice(i,x,y)
    delay=(i*0.36)
    t0=STORM+delay
    t1=t0+1.20+(i%3)*.14
    o.location=(x,y,5.95+(i%2)*.32);o.rotation_euler=(0,0,(i%4-2)*.20);key(o,"location",max(0,t0));key(o,"rotation_euler",max(0,t0))
    o.location=(x+.10,y,.62+(i%2)*.22);o.rotation_euler=(.15,0,(i%4-2)*.45);key(o,"location",t1);key(o,"rotation_euler",t1)
    o.location.z+=.38;key(o,"location",t1+.20)
    o.location.z-=.33;key(o,"location",t1+.40)
    pizza.append(o)

# Give every character obvious full-body acting, not just opening mouths.
for f in range(1,END+1,2):
    t=(f-1)/FPS
    storming=t>STORM
    puff.location=(-2.55+.20*math.sin(.75*t),0,2.55+.16*math.sin(2.4*t))
    puff.rotation_euler.z=.055*math.sin(1.8*t)
    pip.location=(2.30+(.35 if storming else 0)*math.sin(t*.9),-.1,1.65+.08*math.sin(t*3.0))
    pip.rotation_euler.y=.12*math.sin(t*1.7)
    sun.rotation_euler.y=.03*math.sin(t*.65)
    for obj in [puff,pip,sun]:
        key(obj,"location",t)
        key(obj,"rotation_euler",t)
    for i,limb in enumerate(piplegs):
        limb.rotation_euler.y=(1 if i else -1)*.30*math.sin(4.0*t)
        key(limb,"rotation_euler",t)
    for i,limb in enumerate(piparms):
        limb.rotation_euler.y=(1 if i else -1)*(.33+.33*math.sin(2.0*t+i))
        key(limb,"rotation_euler",t)
    for i,limb in enumerate(puffarms):
        limb.rotation_euler.y=(1 if i else -1)*(.26+.32*math.sin(2.5*t+i))
        key(limb,"rotation_euler",t)

say_mouth(pipmouth,"pip")
say_mouth(puffmouth,"puff")

# Animated actual 3D camera with gentle push-in for pizza reveal.
bpy.ops.object.camera_add(location=(0,-16.8,5.2))
cam=bpy.context.object
cam.name="Animated cinema camera"
target=Vector((0,0,2.10))
direction=target-cam.location
cam.rotation_euler=direction.to_track_quat("-Z","Y").to_euler()
cam.data.type="ORTHO"
cam.data.ortho_scale=10.7
for tm,zoom in [(0,10.7),(STORM-1,10.7),(STORM+.7,9.5),(STORM+3,9.8),(data["duration"]-1,10.7)]:
    cam.data.ortho_scale=zoom
    cam.data.keyframe_insert(data_path="ortho_scale",frame=S(tm))
scene=bpy.context.scene
scene.camera=cam
scene.render.engine="BLENDER_WORKBENCH"
scene.display.shading.light="STUDIO"
scene.display.shading.color_type="MATERIAL"
scene.display.shading.show_shadows=True
scene.display.shading.show_cavity=True
scene.display.shading.cavity_type="BOTH"
scene.display.shading.curvature_ridge_factor=1.2
scene.display.shading.curvature_valley_factor=0.8
scene.display.shading.background_type="WORLD"
scene.world.color=(.62,.82,.96)
scene.render.resolution_x=960
scene.render.resolution_y=540
scene.render.resolution_percentage=100
scene.render.film_transparent=False
scene.render.image_settings.file_format="PNG"
scene.frame_start=1
scene.frame_end=END
scene.render.fps=FPS
scene.render.filepath=str((Path("kids3d-build")/"frames"/"frame_").resolve())
Path("kids3d-build/frames").mkdir(parents=True,exist_ok=True)
# Ensure linear keyframe animation remains smooth and no object is hidden
for o in bpy.data.objects:
    if o.animation_data and o.animation_data.action:
        for curve in o.animation_data.action.fcurves:
            for k in curve.keyframe_points:
                k.interpolation="BEZIER"
print("SCENE READY: real 3D meshes",len(bpy.data.objects),"frames",END,flush=True)
bpy.ops.render.render(animation=True)
print("RENDER DONE",flush=True)
