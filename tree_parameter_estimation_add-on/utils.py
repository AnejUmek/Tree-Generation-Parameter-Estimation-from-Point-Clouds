import random

def create_node_tree_setup(node_tree, nodes_to_add, links_to_add):
    all_nodes = {}
    for id, properties in nodes_to_add.items():
        node_type = properties["type"]
        new_node = node_tree.nodes.new(type = node_type)
        all_nodes[id] = new_node
        for property_name, property in properties.items():
            if property_name == "type":
                pass            
            elif property_name == "inputs":
                for input_name, input_value in property.items():
                    new_node.inputs[input_name].default_value = input_value
            elif property_name == "location":
                new_node.location.x = property["x"]
                new_node.location.y = property["y"]
            else:
                setattr(new_node, property_name, property)

    for link in links_to_add:
        node_out, name_out, node_in, name_in = link
        node_tree.links.new(all_nodes[node_out].outputs[name_out], all_nodes[node_in].inputs[name_in])
    
    return all_nodes

def assign_tree_node_values(tree_nodes, values_dict):
    for id in values_dict.keys():
        current_tree_node = tree_nodes[id]
        for input_key, value in values_dict[id].items():
            if input_key == "crown_shape":
                current_tree_node.crown_shape = value
            else:
                current_tree_node.inputs[input_key].property_value = value

def create_random_tree_changing_parameters():
    
    length_low = 8
    length_high = 40
    trunk_length = random.uniform(length_low, length_high)
    trunk_start_radius = 0.03 * trunk_length**0.75 * random.uniform(0.8, 1.2)
    
    branches1_length = (((trunk_length - length_low) / (length_high - length_low)) * 0.3 + ((length_high - trunk_length) / (length_high - length_low)) * 0.5) * random.uniform(0.8, 1.2) * trunk_length
    branches1_density = (((trunk_length - length_low) / (length_high - length_low)) * 2 + ((length_high - trunk_length) / (length_high - length_low)) * 6) * random.uniform(0.8, 1.2)
    branches1_up_attraction = random.uniform(-0.5, 0.5)
    branches1_crown_shape = random.choice(['CYLINDRICAL', 'CONICAL', 'SPHERICAL', 'HEMISPHERICAL', 'TAPERED_CYLINDRICAL', 'INVERSE_CONICAL', 'TEND_FLAME'])
    
    tree_nodes_changing_parameters = {
        "trunk" : {
            "Seed": random.randint(0, 2**16),
            "Length": trunk_length,
            "Start Radius": trunk_start_radius,
        },
        "branches1" : {
            "Seed": random.randint(0, 2**16),
            "Length": branches1_length,
            "Density": branches1_density,
            "Up Attraction": branches1_up_attraction,
            "crown_shape": branches1_crown_shape,
        },
    }
    # removed 'FLAME' crown_shape because it crashes blender- Segmentation fault (core dumped)
    # same crash occurs with 'CONICAL' shape with low trunk length and low branch length
    
    return tree_nodes_changing_parameters