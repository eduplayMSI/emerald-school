"""
P07_materials.py — EMERALD-SCARLATE NORDESTE
Biblioteca PBR de materiais com valores calibrados para glTF/Three.js.
Sem texturas externas, sem UV unwrap. Idempotente. Trabalha sobre o .blend P06.
"""
import bpy
import os

# ============================================================ #
# 0. CAMINHOS
# ============================================================ #
def resolve_project_root():
    if bpy.data.filepath:
        p = os.path.dirname(bpy.data.filepath)
        return os.path.dirname(p) if os.path.basename(p).lower() == "blender" else p
    env = os.environ.get("EMERALD_ROOT")
    if env and os.path.isdir(env):
        return env
    home = os.path.expanduser("~")
    for c in (os.path.join(home, "Desktop", "EMERALD-SCHOOL"),
              os.path.join(home, "Documents", "EMERALD-SCHOOL"),
              os.path.join(home, "OneDrive", "Desktop", "EMERALD-SCHOOL"),
              os.path.join(home, "EMERALD-SCHOOL")):
        if os.path.isdir(c):
            return c
    d = os.path.join(home, "Desktop")
    return os.path.join(d if os.path.isdir(d) else home, "EMERALD-SCHOOL")

PROJECT_ROOT = resolve_project_root()
GLB_OUT   = os.path.join(PROJECT_ROOT, "assets", "EMERALD_SCHOOL.glb")
BLEND_OUT = os.path.join(PROJECT_ROOT, "blender", "EMERALD_SCHOOL.blend")
print(f"[EMERALD][P07] PROJECT_ROOT = {PROJECT_ROOT}")
for d in (os.path.dirname(GLB_OUT), os.path.dirname(BLEND_OUT)):
    os.makedirs(d, exist_ok=True)

# ============================================================ #
# 1. PRÉ-VERIFICAÇÕES
# ============================================================ #
def check_environment():
    v = bpy.app.version
    print(f"[EMERALD][P07] Blender {v[0]}.{v[1]}.{v[2]}")
    if v[0] < 5 or (v[0] == 5 and v[1] < 2):
        raise RuntimeError("Blender 5.2+ exigido.")
    if not hasattr(bpy.ops.export_scene, "gltf"):
        raise RuntimeError("Habilite Preferences → Add-ons → glTF 2.0.")
    if bpy.ops.export_scene.gltf.get_rna_type() is None:
        raise RuntimeError("Operador glTF sem RNA.")
    print("[EMERALD][P07] Exportador glTF OK.")

def verify_base():
    root = bpy.data.collections.get("EMERALD_GENERATED")
    if root is None:
        raise RuntimeError(
            "Base ausente: coleção EMERALD_GENERATED não encontrada.\n"
            "Execute P03_accessibility.py → P06_surfaces.py antes de P07."
        )
    for obj_name in ("SITE_TERRAIN", "FLOOR_CORRIDOR"):
        if not bpy.data.objects.get(obj_name):
            raise RuntimeError(
                f"Base incompleta: objeto '{obj_name}' ausente.\n"
                "P06 requer P03 executado e salvo."
            )
    print("[EMERALD][P07] Base P03+P06 detectada.")

# ============================================================ #
# 2. BIBLIOTECA DE MATERIAIS
#    Estrutura: name -> (category, base_color_rgba, roughness, metallic, alpha)
# ============================================================ #
MATERIAL_LIBRARY = {
    # ---- WALLS (2) ----
    "EM_M_wall_plaster_white":   ("walls",     (0.95, 0.93, 0.89, 1.0), 0.88, 0.00, 1.0),
    "EM_M_wall_sun_yellow":      ("walls",     (0.96, 0.82, 0.25, 1.0), 0.85, 0.00, 1.0),

    # ---- FLOORS (5) ----
    "EM_M_floor_ceramic_beige":  ("floors",    (0.82, 0.76, 0.65, 1.0), 0.55, 0.00, 1.0),
    "EM_M_floor_wood_ceramic":   ("floors",    (0.79, 0.66, 0.46, 1.0), 0.60, 0.00, 1.0),
    "EM_M_floor_vinyl_white":    ("floors",    (0.98, 0.97, 0.95, 1.0), 0.60, 0.00, 1.0),
    "EM_M_floor_ceramic_grey":   ("floors",    (0.61, 0.64, 0.66, 1.0), 0.55, 0.00, 1.0),
    "EM_M_floor_ceramic_cafe":   ("floors",    (0.75, 0.79, 0.81, 1.0), 0.55, 0.00, 1.0),

    # ---- ROOFS (2) ----
    "EM_M_roof_terracotta":      ("roofs",     (0.72, 0.26, 0.20, 1.0), 0.72, 0.00, 1.0),
    "EM_M_roof_metal":           ("roofs",     (0.78, 0.78, 0.80, 1.0), 0.45, 0.70, 1.0),

    # ---- STRUCTURE (2) ----
    "EM_M_column_concrete":      ("structure", (0.88, 0.86, 0.82, 1.0), 0.80, 0.00, 1.0),
    "EM_M_column_orange":        ("structure", (0.92, 0.58, 0.30, 1.0), 0.60, 0.00, 1.0),

    # ---- WOOD / DOORS (2) ----
    "EM_M_door_wood":            ("wood",      (0.48, 0.33, 0.20, 1.0), 0.70, 0.00, 1.0),
    "EM_M_door_frame_white":     ("metal",     (0.92, 0.92, 0.92, 1.0), 0.55, 0.00, 1.0),

    # ---- GLASS (1) ----
    "EM_M_glass_window":         ("glass",     (0.72, 0.86, 0.95, 1.0), 0.05, 0.00, 0.40),

    # ---- GROUND / VEGETATION (6) ----
    "EM_M_ground_grass_base":    ("ground",     (0.55, 0.68, 0.35, 1.0), 0.95, 0.00, 1.0),
    "EM_M_grass_light":          ("vegetation", (0.60, 0.72, 0.40, 1.0), 0.95, 0.00, 1.0),
    "EM_M_grass_medium":         ("vegetation", (0.52, 0.65, 0.32, 1.0), 0.95, 0.00, 1.0),
    "EM_M_grass_dark":           ("vegetation", (0.44, 0.56, 0.27, 1.0), 0.95, 0.00, 1.0),
    "EM_M_earth":                ("ground",     (0.62, 0.52, 0.40, 1.0), 0.95, 0.00, 1.0),
    "EM_M_bush":                 ("vegetation", (0.28, 0.48, 0.24, 1.0), 0.90, 0.00, 1.0),

    # ---- PLAYGROUND (3) ----
    "EM_M_sand_playground":      ("playground", (0.83, 0.77, 0.62, 1.0), 0.95, 0.00, 1.0),
    "EM_M_patio_rubber":         ("playground", (0.72, 0.30, 0.28, 1.0), 0.85, 0.00, 1.0),
    "EM_M_playground_equipment": ("playground", (0.22, 0.60, 0.78, 1.0), 0.55, 0.20, 1.0),

    # ---- SURFACES (P06) (5) ----
    "EM_M_grout":                ("surfaces",   (0.55, 0.50, 0.45, 1.0), 0.95, 0.00, 1.0),
    "EM_M_skirting":             ("surfaces",   (0.72, 0.66, 0.58, 1.0), 0.80, 0.00, 1.0),
    "EM_M_threshold":            ("surfaces",   (0.78, 0.72, 0.62, 1.0), 0.55, 0.10, 1.0),
    "EM_M_drain":                ("surfaces",   (0.38, 0.38, 0.42, 1.0), 0.50, 0.40, 1.0),
    "EM_M_paving_line":          ("surfaces",   (0.55, 0.52, 0.50, 1.0), 0.85, 0.00, 1.0),
}

# Mapeamento: material antigo → material novo
OLD_TO_NEW = {
    # P01-P03
    "EM_floor_beige":   "EM_M_floor_ceramic_beige",
    "EM_floor_class":   "EM_M_floor_wood_ceramic",
    "EM_floor_berc":    "EM_M_floor_vinyl_white",
    "EM_floor_wc":      "EM_M_floor_ceramic_grey",
    "EM_floor_cafe":    "EM_M_floor_ceramic_cafe",
    "EM_wall_yellow":   "EM_M_wall_sun_yellow",
    "EM_wall_white":    "EM_M_wall_plaster_white",
    "EM_roof_tile":     "EM_M_roof_terracotta",
    "EM_roof_metal":    "EM_M_roof_metal",
    "EM_column":        "EM_M_column_concrete",
    "EM_column_accent": "EM_M_column_orange",
    "EM_door_wood":     "EM_M_door_wood",
    "EM_door_frame":    "EM_M_door_frame_white",
    "EM_glass":         "EM_M_glass_window",
    "EM_ground":        "EM_M_ground_grass_base",
    "EM_sand":          "EM_M_sand_playground",
    "EM_patio_rubber":  "EM_M_patio_rubber",
    "EM_play_equip":    "EM_M_playground_equipment",
    # P06
    "P06_grout":        "EM_M_grout",
    "P06_skirt":        "EM_M_skirting",
    "P06_grass_a":      "EM_M_grass_light",
    "P06_grass_b":      "EM_M_grass_medium",
    "P06_grass_c":      "EM_M_grass_dark",
    "P06_earth":        "EM_M_earth",
    "P06_drain":        "EM_M_drain",
    "P06_pave_line":    "EM_M_paving_line",
    "P06_threshold":    "EM_M_threshold",
    "P06_bush":         "EM_M_bush",
}

# Materiais técnicos que NÃO devem ser tocados
PROTECTED = {
    "EM_invisible", "EM_route_line",
    "EM_marker_info", "EM_marker_obst", "EM_marker_haz",
    "EM_door_metal",  # reservado
}

# ============================================================ #
# 3. CONSTRUÇÃO DE MATERIAIS (idempotente: cria ou atualiza)
# ============================================================ #
def configure_bsdf(m, category, color, roughness, metallic, alpha):
    m.use_nodes = True
    nt = m.node_tree
    bsdf = next((n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if bsdf is None:
        bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
        out = next((n for n in nt.nodes if n.type == "OUTPUT_MATERIAL"), None)
        if out:
            nt.links.new(bsdf.outputs[0], out.inputs[0])

    def _set(key, val):
        if key in bsdf.inputs:
            bsdf.inputs[key].default_value = val

    _set("Base Color", color)
    _set("Roughness", roughness)
    _set("Metallic", metallic)

    if alpha < 1.0:
        _set("Alpha", alpha)
        m.blend_method = "BLEND"
        m.use_backface_culling = False
    else:
        _set("Alpha", 1.0)
        m.blend_method = "OPAQUE"
        m.use_backface_culling = True

    # Metadata
    m["emerald_material_id"] = m.name
    m["emerald_category"] = category
    m["emerald_p07"] = True
    m["emerald_web_compat"] = "three@0.160.0"
    m["emerald_textures"] = "none"   # explícito: sem texturas externas
    m["emerald_uv_required"] = False

def build_materials():
    created = 0
    updated = 0
    for name, (cat, color, rough, metal, alpha) in MATERIAL_LIBRARY.items():
        m = bpy.data.materials.get(name)
        if m is None:
            m = bpy.data.materials.new(name)
            created += 1
        else:
            updated += 1
        configure_bsdf(m, cat, color, rough, metal, alpha)
    print(f"[EMERALD][P07] Materiais: {created} criados, {updated} atualizados (total {len(MATERIAL_LIBRARY)}).")
    return created, updated

# ============================================================ #
# 4. APLICAÇÃO DO MAPEAMENTO
# ============================================================ #
def apply_mapping():
    root = bpy.data.collections["EMERALD_GENERATED"]
    swapped = 0
    skipped = 0
    for obj in root.all_objects:
        for slot in obj.material_slots:
            if slot.material is None:
                continue
            old = slot.material.name
            if old in PROTECTED:
                continue
            new_name = OLD_TO_NEW.get(old)
            if new_name is None:
                continue
            new_mat = bpy.data.materials.get(new_name)
            if new_mat is None:
                print(f"[EMERALD][P07][WARN] material alvo ausente: {new_name}")
                skipped += 1
                continue
            slot.material = new_mat
            swapped += 1
    print(f"[EMERALD][P07] Swaps de material: {swapped} (skipped {skipped}).")
    return swapped

# ============================================================ #
# 5. PURGA DE ÓRFÃOS (só remove se 0 usuários)
# ============================================================ #
def purge_orphans():
    purged = 0
    for old_name in list(OLD_TO_NEW.keys()):
        m = bpy.data.materials.get(old_name)
        if m is None:
            continue
        if m.users == 0:
            try:
                bpy.data.materials.remove(m)
                purged += 1
            except Exception:
                pass
    print(f"[EMERALD][P07] Materiais órfãos purgados: {purged}.")
    return purged

# ============================================================ #
# 6. AUDITORIA (informativa)
# ============================================================ #
def audit_materials():
    root = bpy.data.collections["EMERALD_GENERATED"]
    used = {}
    for obj in root.all_objects:
        for slot in obj.material_slots:
            if slot.material is None:
                continue
            name = slot.material.name
            used.setdefault(name, 0)
            used[name] += 1
    print("[EMERALD][P07] Inventário de materiais em uso:")
    for name in sorted(used.keys()):
        m = bpy.data.materials.get(name)
        if m and m.get("emerald_category"):
            print(f"  · {name:32s} [{m['emerald_category']:12s}] {used[name]:4d} slots")
        else:
            print(f"  · {name:32s} [técnico    ] {used[name]:4d} slots")

# ============================================================ #
# 7. EXPORTAÇÃO
# ============================================================ #
def export_glb():
    for o in bpy.context.selected_objects:
        o.select_set(False)
    root = bpy.data.collections.get("EMERALD_GENERATED")
    if root is None:
        raise RuntimeError("EMERALD_GENERATED ausente na exportação.")
    EXCLUDE = ("MARKER_SPHERE_", "OBSTACLE_SPHERE_", "HAZARD_SPHERE_", "ROUTE_RIBBON_")
    count = 0
    for o in root.all_objects:
        if o.type not in {"MESH", "EMPTY"}:
            continue
        if any(o.name.startswith(p) for p in EXCLUDE):
            continue
        o.select_set(True)
        count += 1
    if count == 0:
        raise RuntimeError("Nada para exportar.")
    rna = bpy.ops.export_scene.gltf.get_rna_type()
    sup = {p.identifier for p in rna.properties}
    kw = dict(filepath=GLB_OUT, export_format="GLB", use_selection=True,
              export_yup=True, export_apply=False, export_animations=False)
    if "export_extras" in sup: kw["export_extras"] = True
    if "export_materials" in sup: kw["export_materials"] = "EXPORT"
    if "export_cameras" in sup: kw["export_cameras"] = False
    if "export_lights" in sup: kw["export_lights"] = False
    bpy.ops.export_scene.gltf(**kw)
    if not os.path.exists(GLB_OUT) or os.path.getsize(GLB_OUT) == 0:
        raise RuntimeError("GLB não gerado.")
    size_mb = os.path.getsize(GLB_OUT) / (1024 * 1024)
    print(f"[EMERALD][P07] GLB: {GLB_OUT} ({size_mb:.2f} MB, {count} objetos)")

# ============================================================ #
# 8. MAIN
# ============================================================ #
def main():
    check_environment()
    verify_base()
    created, updated = build_materials()
    swapped = apply_mapping()
    purged = purge_orphans()
    audit_materials()
    export_glb()
    bpy.ops.wm.save_as_mainfile(filepath=BLEND_OUT)
    print(f"[EMERALD][P07] Blend salvo: {BLEND_OUT}")
    print("[EMERALD][P07] Concluído. Teste em http://localhost:8000/")

if __name__ == "__main__":
    main()