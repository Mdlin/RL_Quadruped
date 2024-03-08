import numpy as np

def parse_bvh_hierarchy(bvh_file):
    with open(bvh_file, 'r') as f:
        lines = f.readlines()

    hierarchy = {}
    stack = []
    current_joint = None

    for line in lines:
        if "HIERARCHY" in line or "MOTION" in line:
            continue  # Skip lines until the hierarchy section

        line = line.strip()
        if "ROOT" in line or "JOINT" in line:
            joint_name = line.split()[1]
            hierarchy[joint_name] = {"offset": None, "parent": current_joint}
            if current_joint:
                if "children" not in hierarchy[current_joint]:
                    hierarchy[current_joint]["children"] = []
                hierarchy[current_joint]["children"].append(joint_name)
            stack.append(joint_name)
            current_joint = joint_name
        elif "OFFSET" in line:
            offset = [float(value) for value in line.split()[1:]]
            hierarchy[current_joint]["offset"] = offset
        elif "End" in line:
            current_joint = stack.pop()  # End Site has no further children, go back to parent
        elif "}" in line and stack:
            current_joint = stack.pop()  # Joint definition ended, go back to parent

    return hierarchy

def compute_joint_positions(hierarchy, joint_name, position=[0, 0, 0]):
    joint_pos = {}
    offset = hierarchy[joint_name]["offset"]
    new_position = [position[0] + offset[0], position[1] + offset[1], position[2] + offset[2]]
    joint_pos[joint_name] = new_position

    if "children" in hierarchy[joint_name]:
        for child in hierarchy[joint_name]["children"]:
            joint_pos.update(compute_joint_positions(hierarchy, child, new_position))

    return joint_pos

def approximate_height(joint_positions):
    max_height = max(pos[1] for pos in joint_positions.values())  # Assuming Y is the vertical axis
    min_height = min(pos[1] for pos in joint_positions.values())
    return max_height - min_height

bvh_file = "10_01.bvh"
hierarchy = parse_bvh_hierarchy(bvh_file)
joint_positions = compute_joint_positions(hierarchy, next(iter(hierarchy)))
model_height = approximate_height(joint_positions)

print(f"Approximate height of the model: {model_height}")

def scale_bvh(input_file, output_file, scale_factor):
    with open(input_file, 'r') as f:
        lines = f.readlines()

    in_hierarchy = False
    in_motion = False

    scaled_lines = []
    for line in lines:
        if "HIERARCHY" in line:
            in_hierarchy = True
            in_motion = False
        elif "MOTION" in line:
            in_hierarchy = False
            in_motion = True

        if in_hierarchy and "OFFSET" in line:
            parts = line.split()
            if len(parts) == 4:
                scaled_offsets = [str(float(part) * scale_factor) for part in parts[1:]]
                scaled_line = f"{parts[0]} {' '.join(scaled_offsets)}\n"
                scaled_lines.append(scaled_line)
            else:
                scaled_lines.append(line)
        else:
            scaled_lines.append(line)

    with open(output_file, 'w') as f:
        f.writelines(scaled_lines)


input_bvh = "CAT_Walk.bvh"
output_bvh = "outputscale.bvh"
scale_factor = 0.1

#scale_bvh(input_bvh, output_bvh, scale_factor)
