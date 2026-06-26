from __future__ import annotations

import os

import bpy

_MODULE_PACKAGE = __package__ or __name__
if _MODULE_PACKAGE.endswith(".crowd_diversity_pipeline") and _MODULE_PACKAGE != "crowd_diversity_pipeline":
    ADDON_ID = _MODULE_PACKAGE[: -len(".crowd_diversity_pipeline")]
else:
    ADDON_ID = "crowd_diversity_pipeline"


def _normalize_windows_dir_path(path_value: str) -> str:
    if os.name != "nt" or not path_value:
        return path_value
    return os.path.normpath(path_value).replace("/", "\\")


def _update_library_root(self, _context: bpy.types.Context) -> None:
    normalized = _normalize_windows_dir_path(self.library_root)
    if normalized != self.library_root:
        self.library_root = normalized


class CROWD_Preferences(bpy.types.AddonPreferences):
    bl_idname = ADDON_ID

    library_root: bpy.props.StringProperty(
        name="Library Root",
        description="Folder that will hold exported USD assets and JSON metadata",
        subtype="DIR_PATH",
        default=_normalize_windows_dir_path(os.path.expanduser("~/crowd_diversity_library")),
        update=_update_library_root,
    )

    def draw(self, context: bpy.types.Context) -> None:
        normalized = _normalize_windows_dir_path(self.library_root)
        if normalized != self.library_root:
            self.library_root = normalized
        layout = self.layout
        layout.prop(self, "library_root")


def _find_addon_preferences(context: bpy.types.Context):
    for key in (ADDON_ID, __package__ or __name__, "crowd_diversity_pipeline"):
        addon = context.preferences.addons.get(key)
        if addon is not None and addon.preferences is not None:
            return addon.preferences

    for name, addon in context.preferences.addons.items():
        if "crowd_diversity" in name and addon.preferences is not None:
            return addon.preferences

    return None


class CROWD_PT_Panel(bpy.types.Panel):
    bl_label = "Crowd Diversity"
    bl_idname = "CROWD_PT_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Crowd Diversity"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context: bpy.types.Context) -> None:
        layout = self.layout
        prefs = _find_addon_preferences(context)

        if prefs is None:
            layout.label(text="Crowd Diversity add-on not fully loaded.", icon="ERROR")
            return

        box = layout.box()
        box.label(text="Library Output")
        box.prop(prefs, "library_root")

        box = layout.box()
        box.label(text="Selected Asset Types")
        selected_meshes = [obj for obj in context.selected_objects if obj.type == "MESH"]

        if not selected_meshes:
            box.label(text="Select one or more mesh objects to assign types.")
        else:
            for obj in selected_meshes:
                row = box.row(align=True)
                row.label(text=obj.name)
                row.prop(obj, "crowd_diversity_category", text="")

        layout.separator()
        box = layout.box()
        box.label(text="Fit Check")
        box.prop(context.scene, "crowd_diversity_fit_check_pose")
        box.operator("crowd_diversity.run_fit_check", text="Run Fit Check")

        layout.separator()
        layout.operator("crowd_diversity.export_assets", text="Export Selected Assets")
