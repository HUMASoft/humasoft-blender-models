bl_info = {
    "name": "Soft Neck Control",
    "description": "Script that allows to interact in real-time with the soft-neck model, show orientations, calculate inverse kinematic and motor rotations",
    "author": "Raul de Santos rico (rasantos@it.uc3m.es)",
    "version": (1, 0, 0),
    "blender": (2, 80, 0),
    "location": "3D View > Mode Pose> Soft Neck Control",
    "warning": "Experimenta",
    "wiki_url": "https://github.com/HUMASoft/humasoft-blender-models",
    "tracker_url": "https://github.com/HUMASoft/humasoft-blender-models/issues",
    "category": "Development"
}

import bpy
from bpy.app.handlers import persistent
import math

class CustomPropertyGroup(bpy.types.PropertyGroup):
    
    # Motion update functions
    def updatePitch(self, context):
        softArmature = bpy.data.objects['Armature']
        softArmature.pose.bones["Bone.001"].rotation_euler[2]  = self.pitch / 5
        
    def updateRoll(self, context):
        softArmature = bpy.data.objects['Armature']
        softArmature.pose.bones["Bone.001"].rotation_euler[0]  =  self.roll / 5

    def updateIoInput(self, context):
        if self.enableIoInput:
            self.enablePrInput = False
            
    def updatePrInput(self, context):
        if self.enablePrInput:
            self.enableIoInput = False

    def updateInc(self, context):
        return
     
    def updateOri(self, context):
        return
       
    def updateMask(self, context):
        if bpy.data.objects["Mask"].hide_viewport:
            bpy.data.objects["Mask"].hide_viewport = False
            bpy.data.objects["Mask"].hide_render = False
        else:
            bpy.data.objects["Mask"].hide_viewport = True
            bpy.data.objects["Mask"].hide_render = True
            
    coilDiameter = 1.6 #cm
    
    enableMask: bpy.props.BoolProperty (name='Enable Mask', default=False, description='Enable or disable Mask', update=updateMask)
    enablePrInput: bpy.props.BoolProperty (name='Input:', default=False, description='Enable or Pitch & Roll orientation system', update=updatePrInput)
    enableIoInput: bpy.props.BoolProperty (name='Input:', default=False, description='Enable or Pitch & Roll orientation system', update=updateIoInput)
    pitch : bpy.props.FloatProperty(name='Pitch', subtype='ANGLE', precision=2, min=math.radians(-40), max=math.radians(40), update=updatePitch)
    roll  : bpy.props.FloatProperty(name='Roll', subtype='ANGLE', precision=2, min=math.radians(-40), max=math.radians(40) , update=updateRoll)
    inclination  : bpy.props.FloatProperty(name='Inclination', subtype='ANGLE', precision=2, min=math.radians(-40), max=math.radians(40), update=updateInc)
    orientation  : bpy.props.FloatProperty(name='Orientation', subtype='ANGLE', precision=2, min=math.radians(0), max=math.radians(360), update=updateOri)
    thread1 : bpy.props.FloatProperty(name='Thread 1', subtype='DISTANCE', precision=2)
    thread2 : bpy.props.FloatProperty(name='Thread 2', subtype='DISTANCE', precision=2)
    thread3 : bpy.props.FloatProperty(name='Thread 3', subtype='DISTANCE', precision=2)
    motor1 : bpy.props.FloatProperty(name='Motor 1', subtype='FACTOR', min=-1, max=1)
    motor2 : bpy.props.FloatProperty(name='Motor 2', subtype='FACTOR', min=-1, max=1)
    motor3 : bpy.props.FloatProperty(name='Motor 3', subtype='FACTOR', min=-1, max=1)
    
    locTh01u = bpy.data.objects['thread01.up'].matrix_world.to_translation()
    locTh02u = bpy.data.objects['thread02.up'].matrix_world.to_translation()
    locTh03u = bpy.data.objects['thread03.up'].matrix_world.to_translation()
    locTh01d = bpy.data.objects['thread01.down'].matrix_world.to_translation()
    locTh02d = bpy.data.objects['thread02.down'].matrix_world.to_translation()
    locTh03d = bpy.data.objects['thread03.down'].matrix_world.to_translation()
    
    initLengthTh01 = (locTh01u - locTh01d).length
    initLengthTh02 = (locTh02u - locTh02d).length
    initLengthTh03 = (locTh03u - locTh03d).length
    
class OBJECT_PT_SoftNeckControlPanel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = 'Soft Neck Control'
    bl_context = 'posemode'
    bl_category = 'Soft Neck Control'

    def draw(self, context):
        layout = self.layout
        layout.label(text="Options:")
        layout.prop(context.scene.custom_props, 'enableMask')
        layout.label(text="Orientation System:")
        layout.prop(context.scene.custom_props, 'enablePrInput')
        layout.prop(context.scene.custom_props, 'pitch')
        layout.prop(context.scene.custom_props, 'roll')
        layout.prop(context.scene.custom_props, 'enableIoInput')
        layout.prop(context.scene.custom_props, 'inclination')
        layout.prop(context.scene.custom_props, 'orientation')
        layout.label(text="Thread output values:")
        layout.prop(context.scene.custom_props, 'thread1')
        layout.prop(context.scene.custom_props, 'thread2')
        layout.prop(context.scene.custom_props, 'thread3')
        layout.label(text="Motor rotation output values:")
        layout.prop(context.scene.custom_props, 'motor1')
        layout.prop(context.scene.custom_props, 'motor2')
        layout.prop(context.scene.custom_props, 'motor3')
        layout.operator('softneck.home', text = 'Home Position')
        
class OBJECT_OT_Home(bpy.types.Operator):

    bl_idname = 'softneck.home'
    bl_label = 'Home Postion'
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def execute(self, context):
        home()
        properties = bpy.context.scene.custom_props
        properties.pitch       = 0
        properties.roll        = 0
        properties.inclination = 0
        properties.orientation = 0
        return {'FINISHED'}

# Persistent Handler: https://docs.blender.org/api/current/bpy.app.handlers.html#persistent-handler-example

#@persistent
def run(scene):
    softArmature = bpy.data.objects['Armature']
    properties = bpy.context.scene.custom_props
    
    locTh01u = bpy.data.objects['thread01.up'].matrix_world.to_translation()
    locTh02u = bpy.data.objects['thread02.up'].matrix_world.to_translation()
    locTh03u = bpy.data.objects['thread03.up'].matrix_world.to_translation()
    locTh01d = bpy.data.objects['thread01.down'].matrix_world.to_translation()
    locTh02d = bpy.data.objects['thread02.down'].matrix_world.to_translation()
    locTh03d = bpy.data.objects['thread03.down'].matrix_world.to_translation()
    
    if(properties.enablePrInput):
        properties.inclination = math.sqrt(math.pow(properties.pitch,2) + math.pow(properties.roll,2))
        properties.orientation = ( 2*math.pi - math.atan2(properties.roll, -properties.pitch)) % (2*math.pi)
        
    if(properties.enableIoInput):
        properties.pitch = - properties.inclination * math.cos(properties.orientation)
        properties.roll  = - properties.inclination * math.sin(properties.orientation) 
        
    if not properties.enablePrInput and not properties.enableIoInput:       
        properties.pitch = softArmature.pose.bones["Bone.001"].rotation_euler[2] * 5
        properties.roll  = softArmature.pose.bones["Bone.001"].rotation_euler[0] * 5
        properties.inclination = math.sqrt(math.pow(properties.pitch,2) + math.pow(properties.roll,2))
        properties.orientation = ( 2*math.pi - math.atan2(properties.roll, -properties.pitch)) % (2*math.pi)
    
    currentLengthTh01 = (locTh01u - locTh01d).length
    currentLengthTh02 = (locTh02u - locTh02d).length
    currentLengthTh03 = (locTh03u - locTh03d).length
    
    properties.thread1 = properties.initLengthTh01 - currentLengthTh01
    properties.thread2 = properties.initLengthTh02 - currentLengthTh02
    properties.thread3 = properties.initLengthTh03 - currentLengthTh03

    properties.motor1 = properties.thread1 * 100 / (properties.coilDiameter * math.pi)
    properties.motor2 = properties.thread2 * 100 / (properties.coilDiameter * math.pi)
    properties.motor3 = properties.thread3 * 100 / (properties.coilDiameter * math.pi)
    
    ac01 = bpy.data.objects['ArmatureCoil01']
    ac02 = bpy.data.objects['ArmatureCoil02']
    ac03 = bpy.data.objects['ArmatureCoil03']
    
    ac01.pose.bones["BoneCoil01"].rotation_euler[0] = math.radians( properties.motor1 * 360 )
    ac02.pose.bones["BoneCoil02"].rotation_euler[0] = math.radians( properties.motor2 * 360 )
    ac03.pose.bones["BoneCoil03"].rotation_euler[0] = math.radians( properties.motor3 * 360 )
    
    
def home():
    softArmature = bpy.data.objects['Armature']
    softArmature.pose.bones["Bone.001"].rotation_euler = (0,0,0)
    
def register():
    #register property group class
    bpy.utils.register_class(CustomPropertyGroup)
    #this one especially, it adds the property group class to the scene context (instantiates it)
    bpy.types.Scene.custom_props = bpy.props.PointerProperty(type=CustomPropertyGroup)    
    bpy.utils.register_class(OBJECT_PT_SoftNeckControlPanel)
    bpy.utils.register_class(OBJECT_OT_Home)
    bpy.app.handlers.depsgraph_update_post.append(run)
    bpy.app.handlers.frame_change_pre.append(run)
    
def unregister():
    del bpy.types.Scene.custom_props
    bpy.utils.unregister_class(OBJECT_PT_SoftNeckControlPanel)
    bpy.utils.unregister_class(OBJECT_OT_Home)
    
#a quick line to autorun the script from the text editor when we hit 'run script'
if __name__ == '__main__':
    bpy.ops.object.mode_set(mode='POSE')
    home()
    register()