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

def create_mujoco_body(joint_name, offset):
    body = ET.Element("body", name=joint_name, pos=" ".join(map(str, offset)))
    # Add a geom to represent the joint visually
    geom = ET.SubElement(body, "geom", name=f"{joint_name}_geom", fromto="0 0 -0.05 0 0 -0.23", size=".045", density="982")
    # Add a site
    site = ET.SubElement(body, "site", name=f"{joint_name}_site", pos="0 0 -0.14", size="0.046 0.1", zaxis="0 0 1")
    return body

def convert_bvh_to_mujoco(bvh_filename, mujoco_filename):
    with open(bvh_filename, "r") as file:
        lines = file.readlines()

    mujoco = ET.Element("mujoco")
    worldbody = ET.SubElement(mujoco, "worldbody")

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
            create_mujoco_body(current_element.get('name'), data)
        elif label == "End":
            current_element = hierarchy_stack.pop()  # Go back to parent

    tree = ET.ElementTree(mujoco)
    tree.write(mujoco_filename, encoding='utf-8', xml_declaration=True)

# Example usage
convert_bvh_to_mujoco("input.bvh", "output.xml")
