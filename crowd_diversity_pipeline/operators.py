from __future__ import annotations

import os

import bpy

from .core import build_export_output_path, build_metadata, write_metadata_sidecar


def _find_addon_preferences(context: bpy.types.Context):
    module_package = __package__ or __name__
    if module_package.endswith(".crowd_diversity_pipeline") and module_package != "crowd_diversity_pipeline":
        addon_id = module_package[: -len(".crowd_diversity_pipeline")]
    else:
        addon_id = "crowd_diversity_pipeline"

    for key in (addon_id, module_package, "crowd_diversity_pipeline"):
        addon = context.preferences.addons.get(key)
        if addon is not None and addon.preferences is not None:
            return addon.preferences

    for key, addon in context.preferences.addons.items():
        if "crowd_diversity" in key and addon.preferences is not None:
            return addon.preferences

    return None


class CROWD_OT_ExportAssets(bpy.types.Operator):
    bl_idname = "crowd_diversity.export_assets"
    bl_label = "Export Selected Assets"
    bl_description = "Export the selected rigged garment meshes as USD files and write metadata sidecars"

    def execute(self, context: bpy.types.Context) -> set[str]:
        prefs = _find_addon_preferences(context)
        if prefs is None:
            self.report({"ERROR"}, "Add-on preferences are unavailable. Re-enable the extension.")
            return {"CANCELLED"}

        library_root = prefs.library_root
        if not library_root:
            self.report({"ERROR"}, "Choose a library root before exporting.")
            return {"CANCELLED"}

        objects = [obj for obj in context.selected_objects if obj.type == "MESH"]
        if not objects:
            self.report({"ERROR"}, "Select one or more mesh objects to export.")
            return {"CANCELLED"}

        category = context.scene.crowd_diversity_category
        for obj in objects:
            export_path = build_export_output_path(library_root, category, obj.name)
            export_dir = os.path.dirname(export_path)
            os.makedirs(export_dir, exist_ok=True)

            bpy.ops.object.select_all(action="DESELECT")
            obj.select_set(True)
            context.view_layer.objects.active = obj
            bpy.ops.wm.usd_export(filepath=export_path, check_existing=False)

            metadata = build_metadata(
                category=category,
                object_name=obj.name,
                source_file=bpy.data.filepath,
            )
            write_metadata_sidecar(export_path, metadata)
            self.report({"INFO"}, f"Exported {obj.name} to {export_path}")

        return {"FINISHED"}


class CROWD_OT_RunFitCheck(bpy.types.Operator):
    bl_idname = "crowd_diversity.run_fit_check"
    bl_label = "Run Fit Check"
    bl_description = "Create a temporary duplicate of the selected garments and pose them for quick clipping review"

    def execute(self, context: bpy.types.Context) -> set[str]:
        objects = [obj for obj in context.selected_objects if obj.type == "MESH"]
        if not objects:
            self.report({"ERROR"}, "Select one or more mesh objects to fit-check.")
            return {"CANCELLED"}

        collection_name = "Crowd Diversity Fit Check"
        collection = bpy.data.collections.get(collection_name)
        if collection is None:
            collection = bpy.data.collections.new(collection_name)
            context.scene.collection.children.link(collection)

        for obj in objects:
            duplicate = obj.copy()
            duplicate.data = obj.data.copy()
            collection.objects.link(duplicate)

            armature = self._find_armature(context)
            if armature is None:
                self.report({"WARNING"}, f"No armature found for {obj.name}; skipping fit check setup.")
                continue

            temp_armature = armature.copy()
            temp_armature.data = armature.data.copy()
            collection.objects.link(temp_armature)
            temp_armature.name = f"{armature.name}_fit_check"

            modifier = duplicate.modifiers.new(name="Armature", type="ARMATURE")
            modifier.object = temp_armature
            self._apply_pose(temp_armature, context.scene.crowd_diversity_fit_check_pose)

            duplicate.select_set(True)
            context.view_layer.objects.active = duplicate

        return {"FINISHED"}

    def _find_armature(self, context: bpy.types.Context) -> bpy.types.Object | None:
        for obj in context.scene.objects:
            if obj.type == "ARMATURE":
                return obj
        return None

    def _apply_pose(self, armature: bpy.types.Object, pose_name: str) -> None:
        bpy.ops.object.select_all(action="DESELECT")
        armature.select_set(True)
        bpy.context.view_layer.objects.active = armature
        bpy.ops.object.mode_set(mode="POSE")

        for bone in armature.pose.bones:
            bone.rotation_euler.zero()

        if pose_name == "arms_up":
            for bone in armature.pose.bones:
                name = bone.name.lower()
                if "upper_arm" in name or "shoulder" in name:
                    if "left" in name or ".l" in name or name.endswith("l"):
                        bone.rotation_euler = (0.0, 0.0, 0.7)
                    elif "right" in name or ".r" in name or name.endswith("r"):
                        bone.rotation_euler = (0.0, 0.0, -0.7)
                elif "spine" in name and "spine" in name:
                    bone.rotation_euler = (0.15, 0.0, 0.0)
        elif pose_name == "legs_out":
            for bone in armature.pose.bones:
                name = bone.name.lower()
                if "thigh" in name or "leg" in name:
                    if "left" in name or ".l" in name or name.endswith("l"):
                        bone.rotation_euler = (0.0, 0.35, 0.0)
                    elif "right" in name or ".r" in name or name.endswith("r"):
                        bone.rotation_euler = (0.0, -0.35, 0.0)

        bpy.ops.object.mode_set(mode="OBJECT")
