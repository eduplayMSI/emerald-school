"""
P03_accessibility.py — EMERALD-SCARLATE NORDESTE
Rebuild P02 + rotas/marcadores/obstáculos/perigos + playground.
Uso: abrir no Text Editor do Blender 5.2 LTS e executar (Alt+P).
"""
import bpy, math, os

def resolve_project_root():
    if bpy.data.filepath:
        p = os.path.dirname(bpy.data.filepath)
        return os.path.dirname(p) if os.path.basename(p).lower() == "blender" else p
    env = os.environ.get("EMERALD_ROOT")
    if env and os.path.isdir(env): return env
    home = os.path.expanduser("~")
    for c in (os.path.join(home,"Desktop","EMERALD-SCHOOL"),
              os.path.join(home,"Documents","EMERALD-SCHOOL"),
              os.path.join(home,"OneDrive","Desktop","EMERALD-SCHOOL"),
              os.path.join(home,"EMERALD-SCHOOL")):
        if os.path.isdir(c): return c
    d = os.path.join(home,"Desktop")
    return os.path.join(d if os.path.isdir(d) else home, "EMERALD-SCHOOL")

PROJECT_ROOT = resolve_project_root()
print(f"[EMERALD] PROJECT_ROOT = {PROJECT_ROOT}")
GLB_OUT   = os.path.join(PROJECT_ROOT, "assets", "EMERALD_SCHOOL.glb")
BLEND_OUT = os.path.join(PROJECT_ROOT, "blender", "EMERALD_SCHOOL.blend")
for d in (os.path.dirname(GLB_OUT), os.path.dirname(BLEND_OUT)):
    os.makedirs(d, exist_ok=True)

WALL_T, DOOR_W, DOOR_H = 0.15, 0.90, 2.10
WIN_SILL, WIN_TOP = 0.90, 2.10
ROOT_NAME = "EMERALD_GENERATED"

def check_environment():
    v = bpy.app.version
    print(f"[EMERALD] Blender {v[0]}.{v[1]}.{v[2]}")
    if v[0] < 5 or (v[0]==5 and v[1]<2): raise RuntimeError("Blender 5.2+ exigido.")
    if not hasattr(bpy.ops.export_scene, "gltf"):
        raise RuntimeError("Habilite glTF 2.0 em Preferences → Add-ons.")
    print("[EMERALD] Exportador glTF OK.")

def cleanup():
    coll = bpy.data.collections.get(ROOT_NAME)
    if coll:
        for obj in list(coll.all_objects):
            try: bpy.data.objects.remove(obj, do_unlink=True)
            except Exception: pass
        for sub in list(coll.children_recursive):
            try: bpy.data.collections.remove(sub)
            except Exception: pass
        try: bpy.data.collections.remove(coll)
        except Exception: pass
    for m in list(bpy.data.materials):
        if m.name.startswith("EM_"):
            try: bpy.data.materials.remove(m)
            except Exception: pass
    print("[EMERALD] Cleanup OK.")

_MATS = {}
def mat(name, rgb, rough=0.8, metal=0.0, alpha=1.0):
    if name in _MATS: return _MATS[name]
    m = bpy.data.materials.new(f"EM_{name}"); m.use_nodes = True
    nt = m.node_tree
    bsdf = next((n for n in nt.nodes if n.type=="BSDF_PRINCIPLED"), None)
    if bsdf is None:
        bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
        out = next((n for n in nt.nodes if n.type=="OUTPUT_MATERIAL"), None)
        if out: nt.links.new(bsdf.outputs[0], out.inputs[0])
    def _s(k,v):
        if k in bsdf.inputs: bsdf.inputs[k].default_value = v
    _s("Base Color", (*rgb,1.0)); _s("Roughness", rough); _s("Metallic", metal)
    if alpha < 1.0: _s("Alpha", alpha); m.blend_method="BLEND"
    _MATS[name]=m; return m

MATS = {
    "floor_beige":  lambda: mat("floor_beige",  (0.86,0.80,0.70),0.55),
    "floor_class":  lambda: mat("floor_class",  (0.82,0.72,0.55),0.65),
    "floor_berc":   lambda: mat("floor_berc",   (0.99,0.99,0.99),0.65),
    "floor_wc":     lambda: mat("floor_wc",     (0.62,0.64,0.66),0.55),
    "floor_cafe":   lambda: mat("floor_cafe",   (0.75,0.80,0.82),0.55),
    "wall_yellow":  lambda: mat("wall_yellow",  (0.96,0.82,0.25),0.85),
    "wall_white":   lambda: mat("wall_white",   (0.97,0.97,0.97),0.85),
    "roof_tile":    lambda: mat("roof_tile",    (0.72,0.26,0.20),0.75),
    "roof_metal":   lambda: mat("roof_metal",   (0.78,0.78,0.80),0.45,0.6),
    "column":       lambda: mat("column",       (0.90,0.90,0.90),0.55),
    "column_accent":lambda: mat("column_accent",(0.95,0.55,0.20),0.65),
    "door_wood":    lambda: mat("door_wood",    (0.52,0.36,0.22),0.70),
    "door_frame":   lambda: mat("door_frame",   (0.92,0.92,0.92),0.60),
    "glass":        lambda: mat("glass",        (0.72,0.86,0.95),0.05,0.0,0.35),
    "ground":       lambda: mat("ground",       (0.55,0.68,0.35),0.95),
    "sand":         lambda: mat("sand",         (0.85,0.78,0.55),0.95),
    "patio_rubber": lambda: mat("patio_rubber", (0.78,0.30,0.28),0.85),
    "invisible":    lambda: mat("invisible",    (1.00,0.00,1.00),1.0),
    "route_line":   lambda: mat("route_line",   (1.00,0.42,0.21),0.55),
    "marker_info":  lambda: mat("marker_info",  (0.15,0.55,0.95),0.45),
    "marker_obst":  lambda: mat("marker_obst",  (0.95,0.75,0.10),0.45),
    "marker_haz":   lambda: mat("marker_haz",   (0.92,0.15,0.15),0.45),
    "play_equip":   lambda: mat("play_equip",   (0.20,0.65,0.85),0.55,0.3),
}

ROOT_COLL = None
SUBS = {}
def init_collections():
    global ROOT_COLL
    ROOT_COLL = bpy.data.collections.get(ROOT_NAME) or bpy.data.collections.new(ROOT_NAME)
    if ROOT_COLL.name not in bpy.context.scene.collection.children:
        bpy.context.scene.collection.children.link(ROOT_COLL)
    for n in ["SITE","FLOORS","WALLS","DOORS","WINDOWS","ROOFS","STRUCTURE",
              "COLLIDERS","CAMERAS","LIGHTING",
              "ROUTES","MARKERS","OBSTACLES","HAZARDS","ACCESSIBILITY","PLAYGROUND"]:
        full = f"{ROOT_NAME}_{n}"
        c = bpy.data.collections.get(full) or bpy.data.collections.new(full)
        if c.name not in ROOT_COLL.children:
            ROOT_COLL.children.link(c)
        SUBS[n] = c

def make_box(name, center, size, material, collection):
    sx, sy, sz = size; hx, hy, hz = sx/2, sy/2, sz/2
    verts = [(-hx,-hy,-hz),(hx,-hy,-hz),(hx,hy,-hz),(-hx,hy,-hz),
             (-hx,-hy,hz),(hx,-hy,hz),(hx,hy,hz),(-hx,hy,hz)]
    faces = [(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]
    me = bpy.data.meshes.new(name+"_mesh"); me.from_pydata(verts,[],faces); me.update()
    o = bpy.data.objects.new(name, me); o.location = center
    o.data.materials.append(material); collection.objects.link(o)
    return o

def make_mesh_data(name, verts, faces, material, collection, loc=(0,0,0)):
    me = bpy.data.meshes.new(name+"_mesh"); me.from_pydata(verts,[],faces); me.update()
    o = bpy.data.objects.new(name, me); o.location = loc
    o.data.materials.append(material); collection.objects.link(o)
    return o

def make_sphere(name, center, radius, material, collection):
    me = bpy.data.meshes.new(name+"_mesh")
    bm_verts = []; bm_faces = []
    segs, rings = 12, 8
    for i in range(rings+1):
        v = i / rings
        phi = v * math.pi
        for j in range(segs):
            u = j / segs
            theta = u * 2 * math.pi
            x = radius * math.sin(phi) * math.cos(theta)
            y = radius * math.sin(phi) * math.sin(theta)
            z = radius * math.cos(phi)
            bm_verts.append((x,y,z))
    for i in range(rings):
        for j in range(segs):
            a = i*segs + j
            b = i*segs + (j+1)%segs
            c = (i+1)*segs + j
            d = (i+1)*segs + (j+1)%segs
            bm_faces.append((a,b,d,c))
    me.from_pydata(bm_verts, [], bm_faces); me.update()
    o = bpy.data.objects.new(name, me); o.location = center
    o.data.materials.append(material); collection.objects.link(o)
    return o

def add_collider(name, center, size):
    o = make_box(name, center, size, MATS["invisible"](), SUBS["COLLIDERS"])
    o.display_type = "WIRE"; o.hide_render = True
    return o

# ---------- MUROS / PORTAS / SALAS (idêntico ao P02) ----------
DOORS_CREATED = []
def build_wall_along_x(name, x1, x2, y, height, openings):
    wm = MATS["wall_yellow"]()
    ops = sorted(openings, key=lambda o:o["pos"]); cursor, idx = x1, 0
    for op in ops:
        s = x1+op["pos"]-op["width"]/2; e = x1+op["pos"]+op["width"]/2
        if s > cursor+1e-4:
            w=s-cursor; cx=(cursor+s)/2
            make_box(f"{name}_S{idx}",(cx,y,height/2),(w,WALL_T,height),wm,SUBS["WALLS"])
            add_collider(f"COLLIDER_{name}_S{idx}",(cx,y,height/2),(w,WALL_T,height))
        cx_op=(s+e)/2
        if op["type"]=="door":
            hh=height-DOOR_H
            if hh>1e-3: make_box(f"{name}_HDR{idx}",(cx_op,y,(DOOR_H+height)/2),
                                (op["width"],WALL_T,hh),wm,SUBS["WALLS"])
            DOORS_CREATED.append({"id":f"{name}_D{idx}","hinge_x":s,"hinge_y":y,
                                  "leaf_w":op["width"],"swing":op.get("swing",1)})
        elif op["type"]=="window":
            if WIN_SILL>1e-3: make_box(f"{name}_SILL{idx}",(cx_op,y,WIN_SILL/2),
                                       (op["width"],WALL_T,WIN_SILL),wm,SUBS["WALLS"])
            hh=height-WIN_TOP
            if hh>1e-3: make_box(f"{name}_WHDR{idx}",(cx_op,y,(WIN_TOP+height)/2),
                                 (op["width"],WALL_T,hh),wm,SUBS["WALLS"])
            make_box(f"{name}_GLASS{idx}",(cx_op,y,(WIN_SILL+WIN_TOP)/2),
                     (op["width"]-0.10,0.02,(WIN_TOP-WIN_SILL)-0.10),
                     MATS["glass"](),SUBS["WINDOWS"])
            add_collider(f"COLLIDER_{name}_WIN{idx}",(cx_op,y,height/2),
                         (op["width"],WALL_T,height))
        cursor=e; idx+=1
    if cursor<x2-1e-4:
        w=x2-cursor; cx=(cursor+x2)/2
        make_box(f"{name}_SEND",(cx,y,height/2),(w,WALL_T,height),wm,SUBS["WALLS"])
        add_collider(f"COLLIDER_{name}_SEND",(cx,y,height/2),(w,WALL_T,height))

def build_wall_along_y(name, y1, y2, x, height, openings):
    wm = MATS["wall_yellow"]()
    ops = sorted(openings, key=lambda o:o["pos"]); cursor, idx = y1, 0
    for op in ops:
        s = y1+op["pos"]-op["width"]/2; e = y1+op["pos"]+op["width"]/2
        if s > cursor+1e-4:
            w=s-cursor; cy=(cursor+s)/2
            make_box(f"{name}_S{idx}",(x,cy,height/2),(WALL_T,w,height),wm,SUBS["WALLS"])
            add_collider(f"COLLIDER_{name}_S{idx}",(x,cy,height/2),(WALL_T,w,height))
        cy_op=(s+e)/2
        if op["type"]=="window":
            make_box(f"{name}_SILL{idx}",(x,cy_op,WIN_SILL/2),
                     (WALL_T,op["width"],WIN_SILL),wm,SUBS["WALLS"])
            hh=height-WIN_TOP
            if hh>1e-3: make_box(f"{name}_WHDR{idx}",(x,cy_op,(WIN_TOP+height)/2),
                                 (WALL_T,op["width"],hh),wm,SUBS["WALLS"])
            make_box(f"{name}_GLASS{idx}",(x,cy_op,(WIN_SILL+WIN_TOP)/2),
                     (0.02,op["width"]-0.10,(WIN_TOP-WIN_SILL)-0.10),
                     MATS["glass"](),SUBS["WINDOWS"])
            add_collider(f"COLLIDER_{name}_WIN{idx}",(x,cy_op,height/2),
                         (WALL_T,op["width"],height))
        elif op["type"]=="door":
            hh=height-DOOR_H
            if hh>1e-3: make_box(f"{name}_HDR{idx}",(x,cy_op,(DOOR_H+height)/2),
                                (WALL_T,op["width"],hh),wm,SUBS["WALLS"])
        cursor=e; idx+=1
    if cursor<y2-1e-4:
        w=y2-cursor; cy=(cursor+y2)/2
        make_box(f"{name}_SEND",(x,cy,height/2),(WALL_T,w,height),wm,SUBS["WALLS"])
        add_collider(f"COLLIDER_{name}_SEND",(x,cy,height/2),(WALL_T,w,height))

def build_door_leaf(door_id, hinge_x, hinge_y, leaf_w, swing):
    fm = MATS["door_frame"](); ft = 0.06; cx = hinge_x+leaf_w/2
    for sx in (hinge_x, hinge_x+leaf_w):
        make_box(f"FRAME_{door_id}_{int(sx*100)}",(sx,hinge_y,(DOOR_H+ft)/2),
                 (ft,WALL_T+0.02,DOOR_H+ft),fm,SUBS["DOORS"])
    make_box(f"FRAME_{door_id}_TOP",(cx,hinge_y,DOOR_H+ft/2),
             (leaf_w+ft*2,WALL_T+0.02,ft),fm,SUBS["DOORS"])
    piv = bpy.data.objects.new(f"DOOR_PIVOT_{door_id}", None)
    piv.empty_display_type="ARROWS"; piv.empty_display_size=0.4
    piv.location=(hinge_x,hinge_y,0.0)
    SUBS["DOORS"].objects.link(piv)
    piv["emerald_kind"]="door_pivot"; piv["emerald_swing"]=float(swing)
    piv["emerald_door_id"]=door_id
    leaf = make_box(f"DOOR_LEAF_{door_id}",(0,0,0),(leaf_w,0.05,DOOR_H-0.05),
                    MATS["door_wood"](),SUBS["DOORS"])
    leaf.location=(leaf_w/2,0,(DOOR_H-0.05)/2); leaf.parent=piv
    col = add_collider(f"COLLIDER_DOOR_{door_id}",
                       (hinge_x+leaf_w/2,hinge_y,(DOOR_H-0.05)/2),
                       (leaf_w,0.20,DOOR_H-0.05))
    col["emerald_kind"]="door_collider"; col["emerald_door_id"]=door_id

ROOMS = [
    ("SPC_CLASS_01",  1,  8,  0.9,  7.9, 3.0, "S","floor_class"),
    ("SPC_CLASS_02",  8, 15,  0.9,  7.9, 3.0, "S","floor_class"),
    ("SPC_CLASS_03", 15, 22,  0.9,  7.9, 3.0, "S","floor_class"),
    ("SPC_CLASS_04", 22, 29,  0.9,  7.9, 3.0, "S","floor_class"),
    ("SPC_MULTI",    29, 37,  0.9,  6.9, 3.0, "S","floor_class"),
    ("SPC_BERC_01",   1,  7, -6.9, -0.9, 3.0, "N","floor_berc"),
    ("SPC_BERC_02",   7, 13, -6.9, -0.9, 3.0, "N","floor_berc"),
    ("SPC_WC_01",    13, 16, -3.4, -0.9, 2.8, "N","floor_wc"),
    ("SPC_WC_02",    16, 19, -3.4, -0.9, 2.8, "N","floor_wc"),
    ("SPC_KITCHEN",  19, 24, -4.9, -0.9, 3.0, "N","floor_wc"),
    ("SPC_CAFE",     24, 32, -6.9, -0.9, 3.0, "N","floor_cafe"),
]

def build_rooms():
    first_x = {"N":None,"S":None}
    for rid,x1,x2,y1,y2,h,corr,fmat in ROOMS:
        make_box(f"FLOOR_{rid}",((x1+x2)/2,(y1+y2)/2,-0.05),
                 (x2-x1,y2-y1,0.10),MATS[fmat](),SUBS["FLOORS"])
        cx_door=(x1+x2)/2; win_w=min(2.0,(x2-x1)*0.5)
        if corr=="S":
            build_wall_along_x(f"WALL_{rid}_S",x1,x2,y1,h,
                [{"type":"door","pos":cx_door-x1,"width":DOOR_W,"swing":+1}])
            build_wall_along_x(f"WALL_{rid}_N",x1,x2,y2,h,
                [{"type":"window","pos":cx_door-x1,"width":win_w}])
        else:
            build_wall_along_x(f"WALL_{rid}_N",x1,x2,y2,h,
                [{"type":"door","pos":cx_door-x1,"width":DOOR_W,"swing":-1}])
            build_wall_along_x(f"WALL_{rid}_S",x1,x2,y1,h,
                [{"type":"window","pos":cx_door-x1,"width":win_w}])
        west_ext = (first_x[corr] is None)
        if west_ext:
            build_wall_along_y(f"WALL_{rid}_W",y1,y2,x1,h,
                [{"type":"window","pos":(y1+y2)/2-y1,"width":min(1.4,(y2-y1)*0.4)}])
            first_x[corr]=rid
        else:
            build_wall_along_y(f"WALL_{rid}_W",y1,y2,x1,h,[])
        is_last = rid in ("SPC_MULTI","SPC_CAFE")
        if is_last:
            build_wall_along_y(f"WALL_{rid}_E",y1,y2,x2,h,
                [{"type":"window","pos":(y1+y2)/2-y1,"width":min(1.4,(y2-y1)*0.4)}])
        else:
            build_wall_along_y(f"WALL_{rid}_E",y1,y2,x2,h,[])

def build_corridor():
    make_box("FLOOR_CORRIDOR",(19,0,-0.05),(36,1.8,0.10),
             MATS["floor_beige"](),SUBS["FLOORS"])
    make_box("CEIL_CORRIDOR",(19,0,2.85),(36,1.8,0.10),
             MATS["wall_white"](),SUBS["ROOFS"])

def build_patio():
    px1,px2,py1,py2 = 2.0,14.0,8.5,14.5
    make_box("FLOOR_PATIO",((px1+px2)/2,(py1+py2)/2,-0.05),
             (px2-px1,py2-py1,0.10),MATS["patio_rubber"](),SUBS["FLOORS"])
    col_h=3.5
    for i,(cx,cy) in enumerate([(px1+0.2,py1+0.2),(px2-0.2,py1+0.2),
                                 (px1+0.2,py2-0.2),(px2-0.2,py2-0.2),
                                 ((px1+px2)/2,py1+0.2),((px1+px2)/2,py2-0.2)]):
        make_box(f"COLUMN_PATIO_{i+1:02d}",(cx,cy,col_h/2),
                 (0.20,0.20,col_h),MATS["column"](),SUBS["STRUCTURE"])
        add_collider(f"COLLIDER_COL_PATIO_{i+1:02d}",(cx,cy,col_h/2),(0.20,0.20,col_h))
    make_box("ROOF_PATIO",((px1+px2)/2,(py1+py2)/2,col_h+0.10),
             (px2-px1+0.4,py2-py1+0.4,0.10),MATS["glass"](),SUBS["ROOFS"])

def build_roof():
    xmin,xmax = 0.5,37.5; y_s,y_n = -8.4,9.4
    z_e,y_r,z_r = 3.10,0.5,4.50; t=0.15; mr=MATS["roof_tile"]()
    v_s = [(xmin,y_s,z_e),(xmax,y_s,z_e),(xmax,y_r,z_r),(xmin,y_r,z_r),
           (xmin,y_s,z_e-t),(xmax,y_s,z_e-t),(xmax,y_r,z_r-t),(xmin,y_r,z_r-t)]
    f = [(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]
    make_mesh_data("ROOF_SOUTH",v_s,f,mr,SUBS["ROOFS"])
    v_n = [(xmin,y_r,z_r),(xmax,y_r,z_r),(xmax,y_n,z_e),(xmin,y_n,z_e),
           (xmin,y_r,z_r-t),(xmax,y_r,z_r-t),(xmax,y_n,z_e-t),(xmin,y_n,z_e-t)]
    make_mesh_data("ROOF_NORTH",v_n,f,mr,SUBS["ROOFS"])
    make_box("ROOF_RIDGE",((xmin+xmax)/2,y_r,z_r),(xmax-xmin,0.20,0.10),mr,SUBS["ROOFS"])

def build_entrance_portico():
    px,col_h,pw = -0.3,3.6,0.35
    for i,cy in enumerate([-2.2,2.2]):
        make_box(f"COLUMN_ENTRY_{i+1:02d}",(px,cy,col_h/2),
                 (pw,pw,col_h),MATS["column_accent"](),SUBS["STRUCTURE"])
        add_collider(f"COLLIDER_COL_ENTRY_{i+1:02d}",(px,cy,col_h/2),(pw,pw,col_h))
    make_box("BEAM_ENTRY",(px,0,col_h+0.15),(pw+0.05,4.9,0.30),
             MATS["column_accent"](),SUBS["STRUCTURE"])
    make_box("MARQUISE_ENTRY",(px-1.4,0,col_h+0.35),(3.2,5.2,0.12),
             MATS["roof_metal"](),SUBS["ROOFS"])
    for i,cy in enumerate([-2.2,2.2]):
        make_box(f"COLUMN_MARQ_{i+1:02d}",(px-2.8,cy,col_h/2),
                 (pw,pw,col_h),MATS["column_accent"](),SUBS["STRUCTURE"])
        add_collider(f"COLLIDER_COL_MARQ_{i+1:02d}",(px-2.8,cy,col_h/2),(pw,pw,col_h))

def build_site():
    make_box("SITE_TERRAIN",(19,0,-0.10),(120,100,0.10),
             MATS["ground"](),SUBS["SITE"])
    make_box("SITE_ENTRY_W",(-3.5,0,-0.08),(9,4.4,0.06),
             MATS["floor_beige"](),SUBS["SITE"])

# ---------- P03: PLAYGROUND ----------
def build_playground():
    # Tanque de areia a norte do pátio (y ∈ [16,20], x ∈ [4,12])
    make_box("PLAY_SAND",(8,18,-0.02),(8,4,0.06),MATS["sand"](),SUBS["PLAYGROUND"])
    # Borda de contenção (4 lados)
    make_box("PLAY_BORDER_N",(8,20,-0.02+0.08),(8.2,0.15,0.20),
             MATS["floor_beige"](),SUBS["PLAYGROUND"])
    make_box("PLAY_BORDER_S",(8,16,-0.02+0.08),(8.2,0.15,0.20),
             MATS["floor_beige"](),SUBS["PLAYGROUND"])
    make_box("PLAY_BORDER_W",(4,18,-0.02+0.08),(0.15,4.2,0.20),
             MATS["floor_beige"](),SUBS["PLAYGROUND"])
    make_box("PLAY_BORDER_E",(12,18,-0.02+0.08),(0.15,4.2,0.20),
             MATS["floor_beige"](),SUBS["PLAYGROUND"])
    # Escorregador conceitual (plataforma + rampa)
    make_box("PLAY_SLIDE_PLATFORM",(5.5,18,0.55),(1.0,1.0,1.10),
             MATS["play_equip"](),SUBS["PLAYGROUND"])
    # rampa inclinada: usamos uma caixa rotacionada (visual)
    ramp = make_box("PLAY_SLIDE_RAMP",(4.6,18,0.55),(1.8,0.60,0.10),
                    MATS["play_equip"](),SUBS["PLAYGROUND"])
    ramp.rotation_euler = (0, math.radians(-28), 0)
    add_collider("COLLIDER_PLAY_SLIDE_PLATFORM",(5.5,18,0.55),(1.0,1.0,1.10))
    # Balanço conceitual (2 postes + travessa)
    for i,cy in enumerate([17.0,19.0]):
        make_box(f"PLAY_SWING_POST_{i+1}",(10.5,cy,1.2),(0.12,0.12,2.4),
                 MATS["play_equip"](),SUBS["PLAYGROUND"])
        add_collider(f"COLLIDER_PLAY_SWING_POST_{i+1}",(10.5,cy,1.2),(0.12,0.12,2.4))
    make_box("PLAY_SWING_BEAM",(10.5,18,2.35),(0.12,2.2,0.12),
             MATS["play_equip"](),SUBS["PLAYGROUND"])

# ---------- P03: ROTAS / MARCADORES / OBST / PERIGOS ----------
# Waypoints em coordenadas Blender (x, y). z=0.05 para fita.
ROUTES_DATA = {
    "ROUTE_001": [(-3.5,0),(-0.3,0),(0.5,0),(5,0)],
    "ROUTE_002": [(4.5,0),(4.5,0.9),(4.5,3.0)],
    "ROUTE_003": [(4.0,0),(4.0,-0.9),(4.0,-3.0)],
    "ROUTE_004": [(14.5,0),(14.5,-0.9),(14.5,-2.0)],
    "ROUTE_005": [(28,0),(28,-0.9),(28,-3.0)],
    "ROUTE_006": [(21.5,0),(21.5,-0.9),(21.5,-3.0)],
    "ROUTE_007": [(5,0),(1,0),(0,0),(0,5),(0,8.5),(2,8.5),(8,11)],
    "ROUTE_008": [(8,11),(8,14),(8,16),(8,18)],
}

def build_route_ribbon(route_id, wps):
    z = 0.05; width = 0.15; verts = []; faces = []
    for i,(bx,by) in enumerate(wps):
        if i==0:
            dx=wps[1][0]-wps[0][0]; dy=wps[1][1]-wps[0][1]
        elif i==len(wps)-1:
            dx=wps[-1][0]-wps[-2][0]; dy=wps[-1][1]-wps[-2][1]
        else:
            dx=wps[i+1][0]-wps[i-1][0]; dy=wps[i+1][1]-wps[i-1][1]
        L = math.hypot(dx,dy) or 1.0
        px,py = -dy/L*width/2, dx/L*width/2
        verts.append((bx-px,by-py,z)); verts.append((bx+px,by+py,z))
    for i in range(len(wps)-1):
        a=i*2; b=i*2+1; c=(i+1)*2; d=(i+1)*2+1
        faces.append((a,c,d,b))
    make_mesh_data(f"ROUTE_RIBBON_{route_id}",verts,faces,
                   MATS["route_line"](),SUBS["ROUTES"])

def build_marker_sphere(prefix, m_id, bx, by, bz, material):
    make_sphere(f"{prefix}_{m_id}",(bx,by,bz),0.12,material(),SUBS[prefix.replace("_SPH","").replace("MARKER","MARKERS").replace("OBSTACLE","OBSTACLES").replace("HAZARD","HAZARDS")] if False else
                (SUBS["MARKERS"] if prefix.startswith("MARKER") else
                 SUBS["OBSTACLES"] if prefix.startswith("OBSTACLE") else
                 SUBS["HAZARDS"]))

def build_route_visuals():
    for rid, wps in ROUTES_DATA.items():
        build_route_ribbon(rid, wps)

def build_marker_visuals():
    infos = [
        ("MARKER_001",-0.3,0,2.0),
        ("MARKER_002",4.5,0.9,1.5),
        ("MARKER_003",4.0,-0.9,1.5),
        ("MARKER_004",14.5,-0.9,1.5),
        ("MARKER_005",-0.3,2.2,1.8),
        ("MARKER_006",19,0,0.05),
        ("MARKER_007",8,11,0.05),
        ("MARKER_008",0,0,0.05),
    ]
    for mid,bx,by,bz in infos:
        make_sphere(f"MARKER_SPHERE_{mid}",(bx,by,bz),0.12,
                    MATS["marker_info"](),SUBS["MARKERS"])

def build_obstacle_visuals():
    obst = [
        ("OBSTACLE_001",4.5,0.9,0.03),
        ("OBSTACLE_002",-0.3,-2.2,1.8),
        ("OBSTACLE_003",-3.1,-2.2,1.8),
        ("OBSTACLE_004",2.2,14.3,1.75),
    ]
    for oid,bx,by,bz in obst:
        make_sphere(f"OBSTACLE_SPHERE_{oid}",(bx,by,bz),0.12,
                    MATS["marker_obst"](),SUBS["OBSTACLES"])

def build_hazard_visuals():
    hz = [
        ("HAZARD_001",0,4,0.05),
        ("HAZARD_002",-3.5,0,0.01),
        ("HAZARD_003",14.5,-2,0.05),
    ]
    for hid,bx,by,bz in hz:
        make_sphere(f"HAZARD_SPHERE_{hid}",(bx,by,bz),0.12,
                    MATS["marker_haz"](),SUBS["HAZARDS"])

def build_cameras_and_lights():
    cd = bpy.data.cameras.new("CAM_EXTERNAL"); cd.lens = 35
    c = bpy.data.objects.new("CAM_EXTERNAL", cd)
    c.location = (-25,-25,18); c.rotation_euler = (math.radians(60),0,math.radians(-45))
    SUBS["CAMERAS"].objects.link(c)
    cd2 = bpy.data.cameras.new("CAM_INTERNAL"); cd2.lens = 24
    c2 = bpy.data.objects.new("CAM_INTERNAL", cd2)
    c2.location = (1.0,0,1.7); c2.rotation_euler = (math.radians(90),0,math.radians(90))
    SUBS["CAMERAS"].objects.link(c2)
    bpy.context.scene.camera = c
    sd = bpy.data.lights.new("SUN_NORDESTE", type="SUN")
    sd.energy = 3.5; sd.color = (1.0,0.957,0.878)
    s = bpy.data.objects.new("SUN_NORDESTE", sd)
    s.location = (30,40,50); s.rotation_euler = (math.radians(45),0,math.radians(30))
    SUBS["LIGHTING"].objects.link(s)
    w = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
    bpy.context.scene.world = w; w.use_nodes = True
    bg = next((n for n in w.node_tree.nodes if n.type=="BACKGROUND"), None)
    if bg:
        bg.inputs["Color"].default_value = (0.75,0.85,0.95,1.0)
        bg.inputs["Strength"].default_value = 1.0

def export_glb():
    for o in bpy.context.selected_objects: o.select_set(False)
    # excluir marcadores/rotas/perigos/obstáculos (visualização Web usa JSON)
    EXCLUDE = ("MARKER_SPHERE_","OBSTACLE_SPHERE_","HAZARD_SPHERE_","ROUTE_RIBBON_")
    count = 0
    for o in ROOT_COLL.all_objects:
        if o.type not in {"MESH","EMPTY"}: continue
        if any(o.name.startswith(p) for p in EXCLUDE): continue
        o.select_set(True); count += 1
    if count == 0: raise RuntimeError("Nada para exportar.")
    rna = bpy.ops.export_scene.gltf.get_rna_type()
    sup = {p.identifier for p in rna.properties}
    kw = dict(filepath=GLB_OUT, export_format="GLB", use_selection=True,
              export_yup=True, export_apply=False, export_animations=False)
    if "export_extras" in sup: kw["export_extras"]=True
    if "export_materials" in sup: kw["export_materials"]="EXPORT"
    if "export_cameras" in sup: kw["export_cameras"]=False
    if "export_lights" in sup: kw["export_lights"]=False
    bpy.ops.export_scene.gltf(**kw)
    if not os.path.exists(GLB_OUT) or os.path.getsize(GLB_OUT)==0:
        raise RuntimeError("GLB não gerado.")
    sz = os.path.getsize(GLB_OUT)/(1024*1024)
    print(f"[EMERALD] GLB: {GLB_OUT} ({sz:.2f} MB, {count} objetos exportados)")

def main():
    check_environment(); cleanup(); init_collections()
    build_site(); build_corridor(); build_rooms()
    build_patio(); build_roof(); build_entrance_portico()
    build_playground()
    build_cameras_and_lights()
    for d in DOORS_CREATED:
        build_door_leaf(d["id"], d["hinge_x"], d["hinge_y"], d["leaf_w"], d["swing"])
    print(f"[EMERALD] Portas criadas: {len(DOORS_CREATED)}")
    build_route_visuals()
    build_marker_visuals()
    build_obstacle_visuals()
    build_hazard_visuals()
    print(f"[EMERALD] Rotas: {len(ROUTES_DATA)}, marcadores: 8, obstáculos: 4, perigos: 3")
    export_glb()
    bpy.ops.wm.save_as_mainfile(filepath=BLEND_OUT)
    print(f"[EMERALD] Blend salvo: {BLEND_OUT}")
    print("[EMERALD] P03 concluído.")

if __name__ == "__main__":
    main()