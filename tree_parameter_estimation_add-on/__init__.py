from . import TreeParameterEstimation

bl_info = {
    "name" : "Tree Parameter Estimation",
    "description" : "This addon lets you create trees from a point cloud by estimating its parameters.",
    "author" : "Anej Umek",
    "version" : (1, 0),
    "blender" : (5, 1, 0),
    "location" : "View3D > Sidebar > Tree Parameter Estimation",
    "warning" : "Need to have installed Modular Tree add-on",
    "category" : "Object",
}

def register():
    TreeParameterEstimation.register()

def unregister():
    TreeParameterEstimation.unregister()