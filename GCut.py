###!/usr/bin/env python
bl_info = {
    "name": "GCut",
    "author": "Alex McKonst",
    "version": (1, 7, 10),
    "blender": (2, 79, 0),
    "location": "Mesh",
    "description": "",
    "warning": "WIP",
    "wiki_url": "",
    "tracker_url": "",
    "category": "UI"}

import bpy

def sel(SEL):
    """Here second seleted all vertex
    """
    import bmesh
    if bpy.context.mode == 'OBJECT':
        bpy.ops.object.editmode_toggle()
    mesh = bmesh.from_edit_mesh(bpy.context.object.data)
    for v in mesh.verts:
        v.select = SEL
    for v in mesh.edges:
        v.select = SEL
    for v in mesh.faces:
        v.select = SEL
def nornorm():
    sel(False)
    #   trigger viewport update
    bpy.context.scene.objects.active = bpy.context.scene.objects.active
    bpy.ops.mesh.select_all(action='TOGGLE')
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.mesh.select_all(action='TOGGLE')
    bpy.ops.object.editmode_toggle()               
class GCmsh(bpy.types.Operator):
    bl_idname = "scene.gcmsh"
    bl_label = "gcmsh"
    bl_options = {"REGISTER", "UNDO"}
    optn= bpy.props.EnumProperty(
        items = [('INTERSECT', 'INTERSECT', 'INTERSECT'),
                ('DIFFERENCE', 'DIFFERENCE', 'DIFFERENCE'),
                ('UNION', 'UNION', 'UNION')],
        default = 'DIFFERENCE')

    def execute(self, context):
        # Screen_Orient
        bpy.ops.transform.select_orientation(orientation='VIEW')
        bpy.ops.gpencil.convert(type='POLY', use_realtime=False, use_timing_data=True)
        bpy.context.scene.objects.active = bpy.data.objects['GP_Layer']
        bpy.ops.object.convert(target='MESH')

        sel(True)

        bpy.ops.mesh.extrude_region_move(MESH_OT_extrude_region={"mirror":False}, 
                TRANSFORM_OT_translate={"value":(0, 0, 100), 
                                        "constraint_axis":(False, False, True), 
                                        "constraint_orientation":'VIEW'})
        bpy.ops.mesh.select_all(action='INVERT')
        # extrude out
        bpy.ops.mesh.extrude_region_move(MESH_OT_extrude_region={"mirror":False}, 
                TRANSFORM_OT_translate={"value":(0, 0, -100), 
                                        "constraint_axis":(False, False, True), 
                                        "constraint_orientation":'VIEW'})
        sel(True)
        bpy.ops.object.editmode_toggle()
        # CUT
        bpy.ops.scene.gcut()

        return {'FINISHED'}

class GCUT(bpy.types.Operator):
    bl_idname = "scene.gcut"
    bl_label = "gcut"
    bl_options = {"REGISTER", "UNDO"}
    
    optn= bpy.props.EnumProperty(
    items = [('INTERSECT', 'INTERSECT', 'INTERSECT'),
            ('DIFFERENCE', 'DIFFERENCE', 'DIFFERENCE'),
            ('UNION', 'UNION', 'UNION')],
    default = 'DIFFERENCE')

    
    def execute(self, context):
        if len(bpy.context.selected_objects) ==2:
            frst = bpy.context.scene.objects.active
            frst.select = False
            bpy.context.scene.objects.active = bpy.context.selected_objects[0]         
            scnd = bpy.context.scene.objects.active
            scnd.select = True
            sel(False)
            bpy.ops.object.editmode_toggle()
            
            thrd = bpy.context.scene.objects.active
            frst.select = True
            Vor=bpy.context.window.screen.areas[3].spaces[0].transform_orientation
        #JOIN
            bpy.ops.object.join()
            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.intersect_boolean(operation=self.optn)
            # def orient
            bpy.ops.object.editmode_toggle()
            nornorm()
            bpy.ops.transform.select_orientation(orientation=Vor)
        else:
            self.report({'INFO'}, "Select 2 objets")
        return {'FINISHED'}

class GCSl(bpy.types.Operator):
    bl_idname = "scene.gslice"
    bl_label = "gslice"
    bl_options = {"REGISTER", "UNDO"}
class CCyli(bpy.types.Operator):
    bl_idname = "scene.ccyli"
    bl_label = "Ccyli"
    bl_options = {"REGISTER", "UNDO"}
    
    prof= bpy.props.EnumProperty(
    items = [('circle', 'circle', 'circle'),
            ('square', 'square', 'square'),
            ('triangle', 'triangle', 'triangle')],
            name = '',
    default = 'circle')
    cylrad = bpy.props.FloatProperty(
        name = 'Radius',
        default = 0.2
        )
    cstm = bpy.props.IntProperty(
        name = 'custom angle',
        default = 0,
        min = -360,
        max = 360
        )
    def execute(self, context):
        # Screen_Orient
        sel(False)
        bpy.ops.object.editmode_toggle()
        frst = bpy.context.scene.objects.active
        V1 = bpy.context.window.screen.areas[3].spaces[0].region_3d.view_rotation.to_euler()
        ViewCord = V1[0], V1[1], V1[2]
        Vor=bpy.context.window.screen.areas[3].spaces[0].transform_orientation
        bpy.ops.transform.select_orientation(orientation='VIEW')
        bpy.ops.mesh.primitive_cylinder_add(
            vertices = 4 if self.prof == 'square' else 3 if self.prof != 'circle' else 32,
            depth = 100,
            radius=self.cylrad, view_align=True, 
            enter_editmode=False,
            rotation=(ViewCord)
            )
        if self.prof != 'circle':
            import math                    
        frst.select = True     
        bpy.ops.scene.gcut(optn='DIFFERENCE')
        return {'FINISHED'}
        
class GC(bpy.types.Panel):
    bl_label = "GCUT"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    
    def draw(self, contex):      
        layout = self.layout  
        layout.operator("scene.gcmsh", text='GPCutter')
        if bpy.context.object and bpy.context.object.type == 'MESH':
            layout.operator("scene.ccyli", text='Fast_Hole')
            layout.operator("scene.gcut", text='Bisecta')
    
def register():
    bpy.utils.register_class(CCyli)
    bpy.utils.register_class(GCmsh)
    bpy.utils.register_class(GCUT)
    bpy.utils.register_class(GC)

def unregister():
    bpy.utils.unregister_class(GC)
    bpy.utils.unregister_class(GCUT)
    bpy.utils.unregister_class(GCmsh)
    bpy.utils.unregister_class(CCyli)


if __name__ == "__main__":
   register()
