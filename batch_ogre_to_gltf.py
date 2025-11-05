import bpy
import sys
import os

# Make sure OgreImport.py in the same folder is importable
this_dir = os.path.dirname(os.path.abspath(__file__))
if this_dir not in sys.path:
    sys.path.append(this_dir)

import OgreImport  # your Kenshi/Ogre importer module


class DummyOperator:
    """Minimal stub to satisfy OgreImport.load(operator, ...)"""

    def report(self, types, message):
        print("REPORT", types, ":", message)


def import_ogre_mesh(mesh_path, xml_converter_path):
    """Use OgreImport.load() to import a single .mesh into the current scene.

    Returns a list of newly imported objects (meshes + armatures).
    """
    print(f"--- Importing {mesh_path}")

    # Snapshot objects before import
    before = set(bpy.data.objects.keys())

    # Call the importer; it modifies the scene and returns a status dict
    _result = OgreImport.load(
        operator=DummyOperator(),
        context=bpy.context,
        filepath=mesh_path,
        xml_converter=xml_converter_path,
        keep_xml=False,
        import_normals=False,   # avoid Blender 4.5's use_auto_smooth issue
        normal_mode="flat",
        import_shapekeys=True,
        import_animations=True,      # we’ll handle export errors below
        round_frames=True,
        use_selected_skeleton=False,
        import_materials=True,
    )

    # Snapshot objects after import
    after = set(bpy.data.objects.keys())
    new_names = sorted(after - before)

    new_objects = []
    for name in new_names:
        ob = bpy.data.objects.get(name)
        if ob is None:
            continue
        if ob.type in {"MESH", "ARMATURE"}:
            new_objects.append(ob)

    if not new_objects:
        print("WARNING: Import produced no new MESH/ARMATURE objects")

    return new_objects


def export_gltf_for_objects(objects, output_path):
    """Export given objects to a GLB using Blender's glTF exporter, with fallback if animations break."""
    print(f"--- Exporting to {output_path}")

    if not objects:
        print("WARNING: No objects to export, skipping", output_path)
        return

    # Clear selection
    for obj in bpy.data.objects:
        obj.select_set(False)

    # Select just the imported objects
    for ob in objects:
        try:
            ob.select_set(True)
        except ReferenceError:
            pass

    # Active: prefer armature if present
    active = next((o for o in objects if o.type == "ARMATURE"), objects[0])
    bpy.context.view_layer.objects.active = active

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # First try: with animations
    try:
        bpy.ops.export_scene.gltf(
            filepath=output_path,
            export_format='GLB',
            use_selection=True,
            export_skins=True,
            export_animations=True,
            export_yup=True,
        )
        return
    except Exception as e:
        print(f"!!! GLTF export WITH animations failed for {output_path}")
        print(f"    Error: {e}")

    # Fallback: retry without animations
    print(f"--- Retrying export WITHOUT animations: {output_path}")
    # Keep same selection & active object
    try:
        bpy.ops.export_scene.gltf(
            filepath=output_path,
            export_format='GLB',
            use_selection=True,
            export_skins=True,
            export_animations=False,   # <- key difference
            export_yup=True,
        )
        print(f"*** Exported {output_path} WITHOUT animations due to errors in animation data")
    except Exception as e2:
        print(f"!!! GLTF export WITHOUT animations also failed for {output_path}")
        print(f"    Error: {e2}")
        # Give up on this file but continue the batch
        return


def main():
    # Blender passes its own args; everything after "--" is ours.
    argv = sys.argv
    if "--" not in argv:
        print("Usage: blender -b -P batch_ogre_to_gltf.py -- <input_dir> <output_dir> <OgreXMLConverter.exe>")
        return
    argv = argv[argv.index("--") + 1:]

    if len(argv) < 3:
        print("Usage: blender -b -P batch_ogre_to_gltf.py -- <input_dir> <output_dir> <OgreXMLConverter.exe>")
        return

    input_dir = os.path.abspath(argv[0])
    output_dir = os.path.abspath(argv[1])
    xml_converter = os.path.abspath(argv[2])

    print("Input dir:  ", input_dir)
    print("Output dir: ", output_dir)
    print("XML conv:   ", xml_converter)

    # Walk all .mesh files recursively
    for root, dirs, files in os.walk(input_dir):
        for fname in files:
            if not fname.lower().endswith(".mesh"):
                continue

            mesh_path = os.path.join(root, fname)

            # Mirror folder structure in output
            rel = os.path.relpath(mesh_path, input_dir)
            base, _ = os.path.splitext(rel)
            out_path = os.path.join(output_dir, base + ".glb")

            # Reset scene
            bpy.ops.wm.read_factory_settings(use_empty=True)
            if bpy.ops.object.mode_set.poll():
                bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

            objs = import_ogre_mesh(mesh_path, xml_converter)

            # Wrap per-file export in try/except so one bad file doesn't kill the batch
            try:
                export_gltf_for_objects(objs, out_path)
            except Exception as e:
                print(f"!!! Unhandled error while exporting {mesh_path}")
                print(f"    Error: {e}")

            print(f"=== Finished {mesh_path} -> {out_path}\n")


if __name__ == "__main__":
    main()
