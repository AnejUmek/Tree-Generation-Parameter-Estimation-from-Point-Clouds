nodes_to_add = {
    "meshGrid" : {
        "type" : "GeometryNodeMeshGrid",
        "inputs" : {
          "Size X" : 30,
          "Size Y" : 30,
          "Vertices X" : 151,  
          "Vertices Y" : 151,  
        },
        "location" : {
            "x" : -400,
            "y" : 200,
        },
    },
    "meshToPoints" : {
        "type" : "GeometryNodeMeshToPoints",
        "mode" : "VERTICES",
        "inputs" : {
          "Radius" : 0.05,
        },
        "location" : {
            "x" : -200,
            "y" : 200,
        },
    },
    "deleteGeometry" : {
        "type" : "GeometryNodeDeleteGeometry",
        "domain" : "POINT",
        "mode" : "ALL",
        "location" : {
            "x" : 0,
            "y" : 200,
        },
    },
    "objectInfo" : {
        "type" : "GeometryNodeObjectInfo",
        "transform_space" : "RELATIVE",
        #"inputs" : {
        #    "Object" : tree,
        #},
        "location" : {
            "x" : -600,
            "y" : -100,
        },
    },
    "raycast" : {
        "type" : "GeometryNodeRaycast",
        "data_type" : "FLOAT",
        "inputs" : {
            "Interpolation" : "Interpolated",
            "Ray Direction" : (0.0, 0.0, -1.0),
            "Ray Length" : 50,
        },
        "location" : {
            "x" : -400,
            "y" : -100,
        },
    },
    "booleanMath" : {
        "type" : "FunctionNodeBooleanMath",
        "operation" : "NOT",
        "location" : {
            "x" : -200,
            "y" : 0,
        },
    },
    "setPosition" : {
        "type" : "GeometryNodeSetPosition",
        "location" : {
            "x" : 200,
            "y" : 0,
        },
    },
    "pointsToVertices" : {
        "type" : "GeometryNodePointsToVertices", 
        "location" : {
            "x" : 400,
            "y" : 0,
        },
    },
    "groupOutput" : {
        "type" : "NodeGroupOutput",
        "location" : {
            "x" : 600,
            "y" : 0,
        },
    },
}

links_to_add = [
    ["meshGrid", "Mesh", "meshToPoints", "Mesh"],
    ["meshToPoints", "Points", "deleteGeometry", "Geometry"],
    ["objectInfo", "Geometry", "raycast", "Target Geometry"],
    ["raycast", "Is Hit", "booleanMath", "Boolean"],
    ["booleanMath", "Boolean", "deleteGeometry", "Selection"],
    ["deleteGeometry", "Geometry", "setPosition", "Geometry"],
    ["raycast", "Hit Position", "setPosition", "Position"],
    ["setPosition", "Geometry", "pointsToVertices", "Points"],
    ["pointsToVertices", "Mesh", "groupOutput", "Geometry"]
]

tree_nodes_to_add = {
    "treeMesher" : {
        "type" : "mt_MesherNode",
        "radial_resolution" : 8,
        "location" : {
            "x" : -400,
            "y" : 0,
        },
    },
    "trunk" : {
        "type" : "mt_TrunkNode",
        "location" : {
            "x" : -200,
            "y" : 0,
        },
    },
    "branches1" : {
        "type" : "mt_BranchNode",
        "location" : {
            "x" : 0,
            "y" : 0,
        },
    },
    #"branches2" : {
    #    "type" : "mt_BranchNode",
    #    "location" : {
    #        "x" : 200,
    #        "y" : 0,
    #    },
    #}
}

tree_links_to_add = [
    ["treeMesher", "Tree", "trunk", "Tree"],
    ["trunk", "Tree", "branches1", "Tree"],
    #["branches1", "Tree", "branches2", "Tree"],
]

tree_nodes_non_changing_parameters = {
    "trunk" : {
        "End Radius":  0.05,
        "Shape": 0.7,
        "Up Attraction": 1.0,
        "Resolution": 3.0,
        "Randomness": 0.1,
    },
    "branches1" : {
        "Start": 0.15,
        "End": 1.0,
        "Start Angle": 60,
        "Randomness": 0.5,
        "Flatness": 0.2,
        "Gravity": 10.0,
        "Stiffness": 0.0,
        "Split Chance": 0.5,
        "Split Radius": 0.8,
        "Split Angle": 35,
        "Phillotaxis": 137.5,
        "Break Chance": 0.0,
        "Resolution": 3.0,
        "Start Radius": 0.4,
    },
}

dataset_folder_name = "dataset2"
point_clouds_folder_name = "point_clouds"
meshes_folder_name = "meshes"
parameters_folder_name = "parameters"

"""
TRUNK
    Seed
    Length
    Start Radius
    End Radius = 0.05
    Shape = 0.7
    Up Attraction = 1.0
    Resolution = 3.0
    Randomness = 0.1

BRANCHES
    Seed
    Start = 0.15
    End = 1.0
    Length
    Density
    Start Angle = 60
    Randomness = 0.5
    Flatness = 0.2
    Up Attraction
    Gravity = 10.0
    Stiffness = 0.0
    Split Chance = 0.5
    Split Radius = 0.8
    Split Angle = 35
    Phillotaxis = 137.5
    Break Chance = 0.0
    Resolution = 3.0
    Start Radius = 0.4
    crown_shape ['CYLINDRICAL', 'CONICAL', 'SPHERICAL', 'HEMISPHERICAL', 'TAPERED_CYLINDRICAL', 'FLAME', 'INVERSE_CONICAL', 'TEND_FLAME']
"""