import bpy

create_point_cloud = bpy.data.texts["create_point_cloud.py"].as_module()
estimate_parameters = bpy.data.texts["estimate_parameters.py"].as_module()

def print_parameters(parameters, title):
    print(title)
    print(f"{'Trunk length':^25}: {parameters['trunk']['Length']:.2f}")
    print(f"{'Trunk width':^25}: {parameters['trunk']['Start Radius']:.2f}")
    print(f"{'Branches length':^25}: {parameters['branches1']['Length']:.2f}")
    print(f"{'Branches density':^25}: {parameters['branches1']['Density']:.2f}")
    print(f"{'Branches up attraction':^25}: {parameters['branches1']['Up Attraction']:.2f}")
    print(f"{'Branches crown shape':^25}: {parameters['branches1']['crown_shape']}")

class CreatePointCloud(bpy.types.Operator):
    """Create a random tree and point cloud."""

    bl_idname = "tree_parameter_estimation.create_random_tree"
    bl_label = "Create Point Cloud"
    
    def execute(self, context):
        parameters = create_point_cloud.create_point_cloud()
        
        print_parameters(parameters, "PARAMETERS OF GENERATED TREE")
        return {"FINISHED"}
    

class TreeParameterEstimationOperator(bpy.types.Operator):
    """Estimate the parameters of the point cloud tree and add the tree with those parameters into the scene."""
    
    bl_idname = "tree_parameter_est7imation.estimate_parameters"
    bl_label = "Estimate Parameters"
    
    def execute(self, context):
        
        parameters = estimate_parameters.inference()
        if parameters:
            print_parameters(parameters, "PARAMETERS OF ESTIMATED TREE")
            estimate_parameters.create_tree_from_parameters(parameters)
        return {"FINISHED"}


class TreeParameterEstimationPanel(bpy.types.Panel):
    bl_label = "Tree Parameter Estimation"
    bl_idname = "VIEW3D_PT_TreeParameterEstimationPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Tree Paramamter Estimation"
    
    def draw(self, context):
        layout = self.layout
        
        row = layout.row()
        row.operator(CreatePointCloud.bl_idname)
        
        row = layout.row()
        row.operator(TreeParameterEstimationOperator.bl_idname)
        
def register():
    bpy.utils.register_class(TreeParameterEstimationPanel)
    bpy.utils.register_class(CreatePointCloud)
    bpy.utils.register_class(TreeParameterEstimationOperator)

def unregister():
    bpy.utils.unregister_class(TreeParameterEstimationPanel)
    bpy.utils.unregister_class(CreatePointCloud)
    bpy.utils.unregister_class(TreeParameterEstimationOperator)
    
if __name__ == "__main__":
    register()