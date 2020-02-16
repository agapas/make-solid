# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8-80 compliant>

bl_info = {
	'name': 'Make Solid',
	'author': 'Agnieszka Pas',
	'version': (2, 0, 0),
	'blender': (2, 81, 0),
	'location': 'Properties > Window > Object',
	'description': 'Make non manifold object for 3d print',
	'wiki_url': 'https://github.com/agapas/make-solid#readme',
	'category': 'Object',
}


import bpy
import bmesh
from bpy.types import (
	Operator,
	Panel,
	)
from bl_ui.properties_object import ObjectButtonsPanel


def prepare_meshes():
	bpy.ops.object.make_single_user(object=True, obdata=True)
	bpy.ops.object.convert()
	bpy.ops.object.join()

	bpy.ops.object.mode_set(mode='EDIT')

	# selection dance for proper results
	bpy.ops.mesh.select_all(action='DESELECT')
	bpy.ops.mesh.select_all(action='SELECT')
	bpy.context.tool_settings.mesh_select_mode = (True, True, True)

	bpy.ops.mesh.normals_make_consistent(inside=False)
	bpy.ops.mesh.separate(type='LOOSE')
	bpy.ops.object.mode_set(mode='OBJECT')


def prepare_mesh(obj, select_action):
	scene = bpy.context.scene
	layer = bpy.context.view_layer

	active_object = layer.objects.active
	layer.objects.active = obj
	bpy.ops.object.mode_set(mode='EDIT')

	# reveal hidden vertices in mesh
	bpy.ops.mesh.reveal()

	# mesh cleanup
	bpy.ops.mesh.select_all(action='SELECT')
	bpy.ops.mesh.separate(type='LOOSE')
	bpy.ops.mesh.delete_loose()

	bpy.ops.mesh.select_all(action='SELECT')
	bpy.ops.mesh.remove_doubles(threshold=0.0001)

	bpy.ops.mesh.select_all(action='SELECT')
	bpy.ops.mesh.fill_holes(sides=0)

	bpy.ops.mesh.select_all(action='SELECT')
	bpy.ops.mesh.quads_convert_to_tris()

	# back to previous settings
	bpy.ops.mesh.select_all(action=select_action)
	bpy.ops.object.mode_set(mode='OBJECT')
	layer.objects.active = active_object


def cleanup_mesh(obj):
	mesh = obj.data
	bm = bmesh.new()
	bm.from_mesh(mesh)
	bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0001)
	bm.to_mesh(mesh)
	bm.free()


def add_modifier(active, selected):
	bool_modifier = active.modifiers.new(name='Boolean', type='BOOLEAN')
	bool_modifier.object = selected
	bool_modifier.show_viewport = False
	bool_modifier.show_render = False
	bool_modifier.operation = 'UNION'
	try:
		bool_modifier.solver = 'CARVE'
	except:
		pass

	bpy.ops.object.modifier_apply(modifier='Boolean')

	view_layer = bpy.context.view_layer
	layer_collection = bpy.context.layer_collection or view_layer.active_layer_collection
	collection = layer_collection.collection
	collection.objects.unlink(selected)

	bpy.data.objects.remove(selected)


def make_solid_batch():
	active = bpy.context.active_object
	selected = bpy.context.selected_objects

	selected.remove(active)

	prepare_mesh(active, 'DESELECT')

	for sel in selected:
		prepare_mesh(sel, 'SELECT')
		add_modifier(active, sel)
		cleanup_mesh(active)


def is_manifold(self):
	mesh = bpy.context.active_object.data
	bm = bmesh.new()
	bm.from_mesh(mesh)

	for edge in bm.edges:
		if not edge.is_manifold:
			bm.free()
			self.report({'ERROR'}, "Boolean operation result is non-manifold")
			return False

	bm.free()
	return True


class OBP_OT_MakeSolidOperator(Operator):
	"""Boolean Union on all selected objects"""
	bl_idname = "object.make_solid"
	bl_label = "Make Solid"
	bl_options = {'REGISTER', 'UNDO'}

	mode = 'UNION'

	def execute(self, context):
		layer_objects = bpy.context.view_layer.objects
		active = layer_objects.active
		selected = layer_objects.selected

		if active is None or len(selected) < 2:
			self.report({'WARNING'}, "Select at least 2 objects")
			return {'CANCELLED'}
		else:
			prepare_meshes()
			make_solid_batch()
			is_manifold(self)

		return {'FINISHED'}


class OBP_PT_MakeSolidPanel(ObjectButtonsPanel, Panel):
	bl_idname = "OBP_PT_MakeSolidPanel"
	bl_label = "Make Solid"
	bl_options = {'DEFAULT_CLOSED'}
	bl_order = 11

	def draw(self, context):
		layout = self.layout
		col = layout.column()
		row = col.row()
		row.operator("object.make_solid", text="Combine Objects")

classes = (
	OBP_PT_MakeSolidPanel,
	OBP_OT_MakeSolidOperator,
	)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)


def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)


# if __name__ == "__main__":
# 	register()
