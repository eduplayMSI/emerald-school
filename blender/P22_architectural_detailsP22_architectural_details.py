"""
P22_architectural_details.py — EMERALD-SCARLATE NORDESTE
Adiciona maçanetas, dobradiças, esquadrias de janela e interruptores.
"""
import bpy
import bmesh
import math
import os

def resolve_project_root():
    if bpy.data.filepath:
        p = os.path.dirname(bpy.data.filepath)
        return os.path.dirname(p) if os.path.basename(p).lower() == "blender" else p
    home = os.path.expanduser("~")
    return os.path.join(home, "Desktop", "EMERALD-SCHOOL")

PROJECT_ROOT = resolve_project_root()
GLB_OUT = os.path.join(PROJECT_ROOT, "assets", "EMERALD_SCHOOL.glb")
BLEND_OUT = os.path.join(PROJECT_ROOT, "blender", "EMERALD_SCHOOL.blend")

WALL_T = 0.15
DOOR_H = 2.10

# ============================================================ #
# 1. SETUP
# ============================================================ #
def setup_collection():
    root = bpy.data.collections.get("EMERALD_GENERATED")
    if not root:
        raise RuntimeError("EMERALD_GENERATED não encontrada.")
    coll_name = "P22_ARCHITECTURAL_DETAILS"
    coll = bpy.data.collections.get(coll_name)
    if coll:
        for obj in list(coll.all_objects):
            bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.collections.remove(coll)
    coll = bpy.data.collections.new(coll_name)
    root.children.link(coll)
    return coll

def get_mat(name, color, rough=0.5, metal=0.0):
    m = bpy.data.materials.get(name)
    if not m:
        m = bpy.data.materials.new(name)
        m.use_nodes = True
        bsdf = next((n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
        if bsdf:
            bsdf.inputs["Base Color"].default_value = (*color, 1.0)
            bsdf.inputs["Roughness"].default_value = rough
            bsdf.inputs["Metallic"].default_value = metal
    return m

def make_box(name, center, size, mat, coll, parent=None):
    sx, sy, sz = size
    hx, hy, hz = sx/2, sy/2, sz/2
    verts = [(-hx,-hy,-hz),(hx,-hy,-hz),(hx,hy,-hz),(-hx,hy,-hz),
             (-hx,-hy,hz),(hx,-hy,hz),(hx,hy,hz),(-hx,hy,hz)]
    faces = [(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]
    me = bpy.data.meshes.new(name + "_mesh")
    me.from_pydata(verts, [], faces)
    me.update()
    o = bpy.data.objects.new(name, me)
    o.location = center
    if parent:
        o.parent = parent
    o.data.materials.append(mat)
    coll.objects.link(o)
    mod = o.modifiers.new(name="Bevel", type='BEVEL')
    mod.width = 0.003
    mod.segments = 1
    return o

def make_cylinder(name, center, radius, depth, mat, coll, parent=None, rot=(0,0,0)):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=radius, radius2=radius, depth=depth)
    me = bpy.data.meshes.new(name + "_mesh")
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    o.location = center
    o.rotation_euler = rot
    if parent:
        o.parent = parent
    o.data.materials.append(mat)
    coll.objects.link(o)
    return o

# ============================================================ #
# 2. DETALHES DE PORTA
# ============================================================ #
def build_door_details(coll):
    handle_mat = get_mat("EM_M_METAL_HANDLE", (0.72, 0.68, 0.60), rough=0.25, metal=0.9)
    hinge_mat = get_mat("EM_M_METAL_HINGE", (0.65, 0.63, 0.58), rough=0.35, metal=0.85)

    count = 0
    for piv in bpy.data.objects:
        if not piv.name.startswith("DOOR_PIVOT_"): continue
        door_id = piv.name.replace("DOOR_PIVOT_", "")
        leaf = next((c for c in piv.children if c.name.startswith("DOOR_LEAF_")), None)
        if not leaf: continue

        leaf_w = leaf.dimensions.x
        leaf_h = leaf.dimensions.z

        # MAÇANETAS (alavanca) em ambas as faces
        handle_x = leaf_w / 2 - 0.08
        handle_z_local = 1.05 - leaf_h / 2

        for side, y_sign in [("IN", -1), ("OUT", 1)]:
            y = y_sign * 0.045
            make_cylinder(f"EM_DETAIL_HANDLE_{door_id}_{side}_ROSE",
                         (handle_x, y, handle_z_local),
                         radius=0.025, depth=0.015, mat=handle_mat,
                         coll=coll, parent=leaf, rot=(math.pi/2, 0, 0))
            make_box(f"EM_DETAIL_HANDLE_{door_id}_{side}_LEVER",
                    (handle_x - 0.06, y, handle_z_local),
                    (0.12, 0.02, 0.02),
                    handle_mat, coll, parent=leaf)
            count += 2

        # DOBRADIÇAS (3 por porta, face externa)
        for i, world_z in enumerate([0.20, 1.05, 1.90]):
            z_local = world_z - leaf_h / 2
            make_box(f"EM_DETAIL_HINGE_{door_id}_{i+1}",
                    (-leaf_w/2 + 0.008, 0.028, z_local),
                    (0.03, 0.006, 0.10),
                    hinge_mat, coll, parent=leaf)
            count += 1

    print(f"[P22] {count} detalhes de porta criados.")

# ============================================================ #
# 3. DETALHES DE JANELA
# ============================================================ #
def build_window_details(coll):
    frame_mat = get_mat("EM_M_WINDOW_FRAME", (0.88, 0.88, 0.88), rough=0.4, metal=0.6)

    count = 0
    for glass in bpy.data.objects:
        if "_GLASS" not in glass.name: continue
        if not glass.name.startswith("WALL_"): continue

        gl = glass.location
        gd = glass.dimensions
        along_x = gd.y < gd.x

        width = (gd.x if along_x else gd.y) + 0.10
        sill_z, top_z = 0.90, 2.10
        center_z = 1.50
        height = top_z - sill_z
        ft = 0.04  # espessura do perfil
        fd = 0.06  # profundidade (atravessa a parede)

        def fbox(suffix, pos, size):
            return make_box(f"EM_DETAIL_WIN_{glass.name}_{suffix}", pos, size, frame_mat, coll)

        if along_x:
            cx, cy = gl.x, gl.y
            fbox("BOT",   (cx, cy, sill_z + ft/2),      (width, fd, ft))
            fbox("TOP",   (cx, cy, top_z - ft/2),       (width, fd, ft))
            fbox("LEFT",  (cx - width/2 + ft/2, cy, center_z), (ft, fd, height))
            fbox("RIGHT", (cx + width/2 - ft/2, cy, center_z), (ft, fd, height))
            fbox("MULL",  (cx, cy, center_z),           (ft, fd, height))
        else:
            cx, cy = gl.x, gl.y
            fbox("BOT",   (cx, cy, sill_z + ft/2),      (fd, width, ft))
            fbox("TOP",   (cx, cy, top_z - ft/2),       (fd, width, ft))
            fbox("LEFT",  (cx, cy - width/2 + ft/2, center_z), (fd, ft, height))
            fbox("RIGHT", (cx, cy + width/2 - ft/2, center_z), (fd, ft, height))
            fbox("MULL",  (cx, cy, center_z),           (fd, ft, height))

        count += 5

    print(f"[P22] {count} peças de esquadria em {count//5} janelas.")

# ============================================================ #
# 4. INTERRUPTORES
# ============================================================ #
def build_switches(coll):
    switch_mat = get_mat("EM_M_SWITCH", (0.92, 0.92, 0.92), rough=0.5, metal=0.0)
    count = 0

    for piv in bpy.data.objects:
        if not piv.name.startswith("DOOR_PIVOT_"): continue
        door_id = piv.name.replace("DOOR_PIVOT_", "")
        hx, hy, _ = piv.location
        if abs(hy) < 0.5: continue  # pula pivôs fora do corredor

        sign = 1 if hy > 0 else -1
        wall_face = hy - sign * (WALL_T / 2)
        switch_y = wall_face - sign * 0.015
        switch_x = hx - 0.20

        make_box(f"EM_DETAIL_SWITCH_{door_id}",
                (switch_x, switch_y, 1.10),
                (0.08, 0.02, 0.12),
                switch_mat, coll)
        count += 1

    print(f"[P22] {count} interruptores criados.")

# ============================================================ #
# 5. EXPORTAÇÃO
# ============================================================ #
def export_final():
    for o in bpy.context.selected_objects: o.select_set(False)
    root = bpy.data.collections.get("EMERALD_GENERATED")
    EXCLUDE = ("MARKER_SPHERE_", "OBSTACLE_SPHERE_", "HAZARD_SPHERE_", "ROUTE_RIBBON_")
    count = 0
    for o in root.all_objects:
        if o.type not in {"MESH", "EMPTY", "LIGHT"}: continue
        if any(o.name.startswith(p) for p in EXCLUDE): continue
        o.select_set(True)
        count += 1
    bpy.ops.export_scene.gltf(
        filepath=GLB_OUT, export_format="GLB",
        use_selection=True, export_yup=True,
        export_apply=True, export_animations=False,
        export_lights=True, export_extras=True
    )
    print(f"[P22] GLB Exportado: {GLB_OUT} ({count} objetos)")

if __name__ == "__main__":
    coll = setup_collection()
    build_door_details(coll)
    build_window_details(coll)
    build_switches(coll)
    export_final()
    bpy.ops.wm.save_as_mainfile(filepath=BLEND_OUT)
    print("[P22] Blend salvo. Detalhes arquitetônicos aplicados.")