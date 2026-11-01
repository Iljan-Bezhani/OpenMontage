#!/usr/bin/env python3
"""ABC Wonder Garden: original preschool 3D animated demo for Blender Workbench.

Procedural 3D bunny and bear, 3D letter toys, animated red apple, floating
balloon and playful kitty. Character timing synchronized to Kokoro dialogue.
"""
import bpy
import json
import math
import sys
from pathlib import Path
from mathutils import Vector

TIMELINE = Path("abc-build/timeline.json")
data=json.loads(TIMELINE.read_text(encoding="utf-8"))
LINES=data["lines"]
FPS=12
DURATION=float(data["duration"])
FRAME_END=math.ceil(DURATION*FPS)
frame=lambda seconds:max(1,min(FRAME_END,round(seconds*FPS)+1))
section_start=lambda name:next(float(l["start"]) for l in LINES if l["section"]==name)
T_APPLE=section_start("apple")
T_BALLOON=section_start("balloon")
T_CAT=section_start("cat")
T_REVIEW=section_start("review")
T_OUTRO=section_start("outro")

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
for m in list(bpy.data.materials):bpy.data.materials.remove(m)

def material(name,rgba):
    mat=bpy.data.materials.new(name)
    mat.diffuse_color=(*rgba[:3],1.0)
    return mat

ivory=material("cream character highlights",(.98,.98,.94))
white=material("snow white",(.99,.99,1.0))
pink=material("pink bunny",(.99,.65,.77))
pink2=material("pink bunny ears",(.93,.37,.57))
blue=material("sky blue bow",(.26,.74,.91))
yellow=material("sunshine yellow",(.99,.83,.36))
orange=material("teddy orange",(.78,.51,.28))
brown=material("teddy chocolate",(.32,.21,.24))
black=material("soft black pupils",(.13,.16,.21))
eye_blue=material("bright blue iris",(.18,.39,.76))
red=material("bright red apple",(.96,.22,.27))
green=material("spring green",(.32,.80,.42))
green2=material("leaf green",(.12,.56,.29))
teal=material("mint green",(.39,.87,.74))
purple=material("purple alphabet",(.61,.42,.94))
azure=material("turquoise alphabet",(.28,.78,.95))
gold=material("golden letter",(.99,.72,.20))
peach=material("soft peach",(.99,.82,.67))
lavender=material("pastel clouds",(.76,.74,.96))
grass=material("grassy platform",(.55,.88,.63))
dirt=material("grass platform edge",(.31,.72,.54))
warm=material("balloon coral",(.99,.40,.55))
catfur=material("peach orange kitty",(.99,.68,.37))
catmuzzle=material("kitty muzzle",(.99,.87,.74))
nose=material("little pink nose",(.93,.32,.43))
mouth_color=material("happy mouth",(.41,.17,.26))

def empty(name,loc=(0,0,0),parent=None):
    obj=bpy.data.objects.new(name,None);bpy.context.collection.objects.link(obj)
    obj.location=loc
    if parent:obj.parent=parent
    return obj

def orb(name,loc,scale,mat,parent=None):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20,ring_count=12,location=(0,0,0))
    o=bpy.context.object;o.name=name
    if parent:o.parent=parent
    o.location=loc;o.scale=scale;o.data.materials.append(mat)
    for f in o.data.polygons:f.use_smooth=True
    return o

def cylinder(name,loc,r,depth,mat,parent=None,n=24):
    bpy.ops.mesh.primitive_cylinder_add(vertices=n,radius=r,depth=depth,location=(0,0,0))
    o=bpy.context.object;o.name=name
    if parent:o.parent=parent
    o.location=loc;o.data.materials.append(mat)
    for f in o.data.polygons:f.use_smooth=True
    return o

def text3d(name,label,loc,size,mat,parent=None,depth=.065):
    crv=bpy.data.curves.new(name,"FONT")
    crv.body=label;crv.align_x="CENTER";crv.align_y="CENTER";crv.size=size
    crv.extrude=depth;crv.bevel_depth=.013;crv.bevel_resolution=2
    ob=bpy.data.objects.new(name,crv)
    bpy.context.collection.objects.link(ob)
    if parent:ob.parent=parent
    ob.location=loc;ob.rotation_euler.x=math.pi/2
    crv.materials.append(mat)
    return ob

def key(o,property_name,t):
    o.keyframe_insert(data_path=property_name,frame=frame(t))

def scale_phase(root,start,end,delay=.18):
    for t,s in [(0,.001),(max(0,start-.10),.001),(start+delay,1.0),
                (max(start+delay,end-.15),1.0),(end+.04,.001)]:
        root.scale=(s,s,s)
        key(root,"scale",t)

def eyelids(name,root,x,y,z):
    orb(name+" whites",(x,y,z),(.153,.120,.200),white,root)
    orb(name+" irises",(x,y-.104,z-.014),(.077,.048,.118),eye_blue,root)
    orb(name+" pupils",(x,y-.145,z-.012),(.042,.034,.073),black,root)
    orb(name+" sparkle",(x-.035,y-.173,z+.045),(.023,.015,.034),white,root)

# rounded toy meadow with floating candy decorations, no copyrighted visuals
cylinder("bright grass platform",(0,0,-.42),6.8,.65,grass,n=80)
cylinder("emerald edge",(0,0,-.80),6.6,.25,dirt,n=80)
for idx in range(23):
    ang=idx*math.pi*2/23
    r=5.55+(idx%3)*.20
    x,y=r*math.cos(ang),r*math.sin(ang)
    if y<-.9:continue
    orb("little meadow blossom",(x,y,.055),(.075,.075,.055),pink2 if idx%3==0 else yellow)
for i,x in enumerate([-5.5,-4.75,4.80,5.45]):
    cylinder("candy tree trunk",(x,2.9,.48),.12,.9,orange,n=16)
    orb("candy tree top",(x,2.9,1.20),(.52,.48,.57),teal if i%2 else green2)
for i in range(13):
    x=-4.5+i*.74
    orb("ground dot",(x,2.75,.095),(.055,.075,.04),lavender if i%2 else yellow)

# LULU pink bunny - expressive original character
bunny=empty("Lulu bunny animated root",(-2.7,-.30,0))
orb("Lulu large body",(0,0,.88),(.60,.48,.76),pink,bunny)
orb("Lulu tummy",(0,-.43,.83),(.38,.12,.48),ivory,bunny)
orb("Lulu round head",(0,-.055,2.02),(.76,.62,.75),pink,bunny)
orb("Lulu cotton tail",(.45,.37,.73),(.22,.22,.23),ivory,bunny)
ears=[]
for sg in (-1,1):
    ear=empty("Lulu movable ear",(sg*.40,.08,2.50),bunny)
    orb("long rabbit ear",(0,0,.42),(.24,.21,.63),pink,ear)
    orb("soft ear inset",(0,-.202,.43),(.135,.055,.46),pink2,ear)
    ears.append(ear)
    eyelids("Lulu eye",bunny,sg*.33,-.611,2.11)
    orb("Lulu blush",(sg*.56,-.55,1.86),(.18,.09,.11),pink2,bunny)
    orb("Lulu foot",(sg*.37,-.17,.20),(.31,.36,.20),pink,bunny)
orb("Lulu nose",(0,-.72,1.88),(.10,.07,.08),nose,bunny)
bunny_mouth=orb("Lulu lip sync",(0,-.713,1.72),(.15,.055,.14),mouth_color,bunny)
bunny_mouth.scale.z=.15
arms_b=[]
for sg in (-1,1):
    arm=empty("Lulu waving arm",(sg*.54,0,1.18),bunny)
    orb("Lulu arm",(sg*.24,-.05,-.21),(.22,.20,.41),pink,arm)
    orb("Lulu hand",(sg*.32,-.08,-.43),(.22,.21,.20),pink,arm)
    arms_b.append(arm)
orb("Lulu blue bow center",(.60,-.12,2.59),(.15,.11,.14),blue,bunny)
orb("Lulu bow loop A",(.46,-.12,2.60),(.19,.07,.13),blue,bunny)
orb("Lulu bow loop B",(.75,-.12,2.60),(.19,.07,.13),blue,bunny)

# MILO, a chubby golden teddy
bear=empty("Milo bear animated root",(2.75,-.17,0))
orb("Milo chubby body",(0,0,.98),(.73,.57,.78),orange,bear)
orb("Milo cream belly",(0,-.55,.99),(.49,.15,.57),peach,bear)
orb("Milo big head",(0,-.08,2.07),(.82,.68,.75),orange,bear)
for sg in (-1,1):
    orb("Milo bear ear",(sg*.64,-.01,2.60),(.30,.22,.33),orange,bear)
    orb("Milo ear center",(sg*.65,-.22,2.60),(.17,.060,.19),pink,bear)
    eyelids("Milo blue eye",bear,sg*.31,-.68,2.13)
    orb("Milo foot",(sg*.39,-.22,.21),(.32,.39,.24),orange,bear)
    orb("Milo cheek",(sg*.56,-.62,1.87),(.15,.068,.092),pink2,bear)
orb("Milo cream muzzle",(0,-.72,1.76),(.37,.18,.25),peach,bear)
orb("Milo tiny nose",(0,-.885,1.82),(.112,.075,.083),brown,bear)
bear_mouth=orb("Milo lip sync",(0,-.89,1.63),(.14,.065,.132),mouth_color,bear)
bear_mouth.scale.z=.14
arms_m=[]
for sg in (-1,1):
    arm=empty("Milo waving arm",(sg*.66,0,1.27),bear)
    orb("Milo arm",(sg*.19,-.045,-.18),(.26,.23,.40),orange,arm)
    orb("Milo paw",(sg*.27,-.06,-.39),(.26,.24,.22),orange,arm)
    arms_m.append(arm)
# little star badge on tummy
orb("Milo star badge",(.01,-.713,.98),(.13,.057,.15),yellow,bear)

# Hero title; 3D individual alphabet toys on the intro platform
intro=empty("INTRO TOY TITLE")
text3d("Big welcome title","ABC WONDER",(0,-.55,4.35),.83,purple,intro)
text3d("Garden title","GARDEN",(0,-.56,3.68),.83,green2,intro)
intro_letters=[]
for j,(letter,ma) in enumerate([("A",red),("B",azure),("C",gold)]):
    block=empty("Intro letter "+letter,(-1.08+j*1.07,-.50,2.65),intro)
    orb("colorful alphabet toy base",(0,.12,-.33),(.40,.33,.10),peach,block)
    text3d("Intro raised letter "+letter,letter,(0,-.27,.05),.88,ma,block,.095)
    intro_letters.append(block)
scale_phase(intro,0,T_APPLE)

# APPLE SECTION — three dimensional letter with red apple that hops
apple=empty("APPLE LETTER A SCENE")
text3d("Very large letter A","A",(-.82,-.60,2.70),2.0,red,apple,.11)
orb("Apple bright red body",(.88,-.15,1.66),(.69,.59,.72),red,apple)
orb("Apple lobes left",(.61,-.13,2.12),(.34,.42,.26),red,apple)
orb("Apple lobes right",(1.16,-.13,2.12),(.34,.42,.26),red,apple)
cylinder("Apple brown stem",(.88,-.08,2.35),.055,.40,brown,apple)
leaf=orb("Apple green leaf",(1.09,-.13,2.49),(.26,.09,.14),green2,apple)
leaf.rotation_euler.y=.38
orb("Apple cheerful eye 1",(.64,-.735,1.74),(.060,.04,.105),black,apple)
orb("Apple cheerful eye 2",(1.06,-.735,1.74),(.060,.04,.105),black,apple)
orb("Apple tiny smile",(.87,-.752,1.56),(.14,.03,.05),mouth_color,apple)
text3d("Word APPLE","APPLE",(0,-.64,.52),.52,green2,apple)
scale_phase(apple,T_APPLE,T_BALLOON)
# wobble during the A section
for t in [T_APPLE+.22,T_APPLE+1.7,T_APPLE+3.0,T_APPLE+4.5,T_APPLE+5.8]:
    leaf.rotation_euler.y=.38+.25*math.sin(t*1.1)
    key(leaf,"rotation_euler",t)

# BALLOON SECTION — floating 3D red balloon with string and waving motion
balloon=empty("BALLOON LETTER B SCENE")
text3d("Very large letter B","B",(-.77,-.60,2.67),1.95,azure,balloon,.12)
flying=empty("Floating balloon root",(1.00,-.10,1.38),balloon)
orb("Balloon inflated round body",(0,0,.58),(.51,.45,.76),warm,flying)
orb("Balloon reflection",(-.18,-.365,.82),(.12,.045,.24),white,flying)
orb("Balloon knot",(0,0,-.22),(.10,.10,.13),warm,flying)
string=cylinder("Balloon swaying string",(0,.02,-.61),.024,.78,ivory,flying,n=12)
string.rotation_euler.y=.12
text3d("Word BALLOON","BALLOON",(0,-.61,.52),.49,blue,balloon)
scale_phase(balloon,T_BALLOON,T_CAT)
for t in [T_BALLOON+.20,T_BALLOON+2.5,T_BALLOON+5.0,T_BALLOON+8.2]:
    flying.location=(1.0+.15*math.sin(t),-.10,1.38+.30*math.sin((t-T_BALLOON)*.8))
    key(flying,"location",t)

# CAT SECTION — original 3D kitten, tail moves and head bobs
cat_scene=empty("CAT LETTER C SCENE")
text3d("Very large letter C","C",(-.85,-.60,2.72),2.00,gold,cat_scene,.12)
kitty=empty("Tiny Kitty animated",(1.0,-.24,.55),cat_scene)
orb("Cat little body",(0,.07,.55),(.52,.45,.68),catfur,kitty)
orb("Cat round head",(0,-.20,1.30),(.59,.53,.55),catfur,kitty)
for sg in (-1,1):
    # pointy ears as beveled short cones
    bpy.ops.mesh.primitive_cone_add(vertices=16,radius1=.24,radius2=.0,depth=.52,location=(0,0,0))
    cone=bpy.context.object;cone.name="Kitty pointed ear"
    cone.parent=kitty;cone.location=(sg*.37,-.16,1.78)
    cone.data.materials.append(catfur)
    for poly in cone.data.polygons:poly.use_smooth=True
    orb("Kitty foot",(sg*.33,-.35,.12),(.24,.34,.17),catfur,kitty)
    orb("Kitty glossy eye",(sg*.23,-.686,1.39),(.065,.055,.125),black,kitty)
    orb("Kitty eye shine",(sg*.22-.015,-.738,1.45),(.023,.019,.027),white,kitty)
orb("Kitty cream muzzle",(0,-.72,1.18),(.28,.09,.19),catmuzzle,kitty)
orb("Kitty pink nose",(0,-.818,1.24),(.09,.052,.072),nose,kitty)
orb("Kitty smiling mouth",(0,-.809,1.08),(.12,.037,.044),mouth_color,kitty)
tail=empty("Kitty wagging tail",(.50,.26,.56),kitty)
for idx,(x,y,z,rad) in enumerate([(.14,.1,.0,.18),(.31,.15,.26,.15),(.36,.15,.53,.13),(.29,.15,.73,.13)]):
    orb("Curled kitty tail", (x,y,z),(rad,rad,rad),catfur,tail)
text3d("Word CAT","CAT",(0,-.61,.52),.53,purple,cat_scene)
scale_phase(cat_scene,T_CAT,T_REVIEW)
for i,t in enumerate([T_CAT+.2,T_CAT+2,T_CAT+4,T_CAT+6,T_CAT+8,T_CAT+10]):
    tail.rotation_euler.y=.30 if i%2 else -.26
    key(tail,"rotation_euler",t)
    kitty.rotation_euler.z=.05*math.sin(i*.8)
    key(kitty,"rotation_euler",t)

# REVIEW SECTION — all 3 letter toys in the same frame
review=empty("REVIEW ABC TOYS")
text3d("Review giant A","A",(-1.16,-.60,2.45),1.3,red,review)
text3d("Review giant B","B",(0,-.60,2.45),1.3,azure,review)
text3d("Review giant C","C",(1.17,-.60,2.45),1.3,gold,review)
text3d("Repeat the alphabet","A  B  C",(0,-.65,1.25),.75,purple,review)
scale_phase(review,T_REVIEW,T_OUTRO)

outro=empty("OUTRO")
text3d("You've learned letters","GREAT JOB!",(0,-.55,3.28),.90,purple,outro)
text3d("See you later","SEE YOU SOON!",(0,-.57,1.83),.64,green2,outro)
scale_phase(outro,T_OUTRO,DURATION+1)

# Character acting and lip sync, all generated as real 3D keyframes
for f in range(1,FRAME_END+1,3):
    t=(f-1)/FPS
    bunny.location=(-2.66+.07*math.sin(t*.65),-.30,.10*math.sin(t*2.25))
    bunny.rotation_euler.y=.050*math.sin(t*1.20)
    bear.location=(2.69+.07*math.sin(t*.63),-.17,.07*math.sin(t*2.42+.7))
    bear.rotation_euler.y=.045*math.sin(t*1.05+.8)
    for ob in [bunny,bear]:
        key(ob,"location",t)
        key(ob,"rotation_euler",t)
    for i,arm in enumerate(arms_b):
        arm.rotation_euler.y=(1 if i else -1)*(.16+.48*math.sin(t*2.2+i))
        key(arm,"rotation_euler",t)
    for i,arm in enumerate(arms_m):
        arm.rotation_euler.y=(1 if i else -1)*(.19+.40*math.sin(t*2.0+i+.5))
        key(arm,"rotation_euler",t)
    for i,ear in enumerate(ears):
        ear.rotation_euler.y=(1 if i else -1)*(.06+.14*math.sin(t*1.5+i))
        key(ear,"rotation_euler",t)

for speaker,mouth in (("lulu",bunny_mouth),("milo",bear_mouth)):
    for line in LINES:
        if line["speaker"]!=speaker:continue
        start=float(line["start"])
        stop=start+float(line["duration"])
        for tm,val in [(max(0,start-.08),.12),(start,.64)]:
            mouth.scale.z=val;key(mouth,"scale",tm)
        ti=start
        j=0
        while ti<stop:
            mouth.scale.z=.78 if j%2==0 else .18
            key(mouth,"scale",ti)
            ti+=.17;j+=1
        mouth.scale.z=.12
        key(mouth,"scale",stop+.05)

# Camera is orthographic for clear toddler friendly composition
bpy.ops.object.camera_add(location=(0,-17.2,5.15))
camera=bpy.context.object;camera.name="Slow-moving family show camera"
direction=Vector((0,0,1.95))-camera.location
camera.rotation_euler=direction.to_track_quat("-Z","Y").to_euler()
camera.data.type="ORTHO"
camera.data.ortho_scale=10.6
for t,size in [(0,11.2),(T_APPLE,10.0),(T_BALLOON,10.0),(T_CAT,10.0),(T_REVIEW,10.8),(DURATION,11.2)]:
    camera.data.ortho_scale=size
    camera.data.keyframe_insert(data_path="ortho_scale",frame=frame(t))

scene=bpy.context.scene
scene.camera=camera
scene.render.engine="BLENDER_WORKBENCH"
scene.display.shading.light="STUDIO"
scene.display.shading.color_type="MATERIAL"
scene.display.shading.show_shadows=True
scene.display.shading.show_cavity=True
scene.display.shading.cavity_type="BOTH"
scene.display.shading.curvature_ridge_factor=1.3
scene.display.shading.curvature_valley_factor=.8
scene.display.shading.background_type="WORLD"
scene.world.color=(.62,.86,.98)
scene.render.resolution_x=960
scene.render.resolution_y=540
scene.render.resolution_percentage=100
scene.render.film_transparent=False
scene.render.image_settings.file_format="PNG"
scene.frame_start=1
scene.frame_end=FRAME_END
scene.render.fps=FPS
Path("abc-build/frames").mkdir(parents=True,exist_ok=True)
scene.render.filepath=str((Path("abc-build")/"frames"/"frame_").resolve())

print(f"ABC WONDER GARDEN 3D: objects={len(bpy.data.objects)}, frames={FRAME_END}, duration={DURATION:.1f}",flush=True)
bpy.ops.render.render(animation=True)
print("ABC 3D RENDER COMPLETE",flush=True)
