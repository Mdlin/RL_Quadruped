import numpy as np
import xml.etree.ElementTree as ET

def parse_bvh_line(line):
    parts = line.strip().split()
    if not parts:
        return None, None
    label = parts[0]
    if label in {"ROOT", "JOINT", "End"}:
        return label, parts[1] if len(parts) > 1 else None
    elif label == "OFFSET":
        return "OFFSET", list(map(float, parts[1:]))
    return None, None

# def parse_bvh_line(line):
#    parts = line.strip().split()
#    if not parts:
#        return None, None
#    label = parts
#    if label in {'ROOT'}:
#        return label


def create_mujoco_body(joint_name, offset):
    body = ET.Element("body", name=joint_name, pos=" ".join(map(str, offset)))
    # Add a sp/home/miko/bojian/RL_Quadruped1/Cat/CAT_Walk.bvhhere geom to represent the joint visually when the body is created
    geom = ET.SubElement(body, "geom", name=f"{joint_name}_geom", type="sphere", size="0.5")  # Sphere size is arbitrary
    return body

def convert_bvh_to_mujoco(bvh_filename, mujoco_filename):
    with open(bvh_filename, "r") as file:
        lines = file.readlines()

    mujoco = ET.Element("mujoco")
    worldbody = ET.SubElement(mujoco, "worldbody")
    # Add the floor geometry
    ET.SubElement(worldbody, "geom", name="floor", type="plane", conaffinity="1", size="100 100 .2")

    current_element = worldbody
    hierarchy_stack = []

    for line in lines:
        label, data = parse_bvh_line(line)
        if label == "ROOT" or label == "JOINT":
            joint_name = data
            # Wait to set offset until we know what it is
            body = ET.Element("body", name=joint_name)
            current_element.append(body)
            hierarchy_stack.append(current_element)
            current_element = body
        elif label == "OFFSET":
            # Set the position of the body and add the geom now that we have the offset
            current_element.set("pos", " ".join(map(str, data)))
            ET.SubElement(current_element, "geom", name=f"{current_element.get('name')}_geom", type="sphere", size="0.05")
        elif label == "End":
            current_element = hierarchy_stack.pop()  # Go back to parent

    tree = ET.ElementTree(mujoco)
    tree.write(mujoco_filename, xml_declaration=True, encoding='utf-8', method="xml")

# Example usage

convert_bvh_to_mujoco("CAT_Walk.bvh", "output.xml")
