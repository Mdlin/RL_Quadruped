def read_bvh_frames(filename):
    """ Read the BVH file and return the lines after 'Frame Time:' """
    with open(filename, 'r') as file:
        lines = file.readlines()

    frame_time_index = next(i for i, line in enumerate(lines) if 'Frame Time:' in line)
    return lines[frame_time_index + 1:]


def extract_entries(lines, i, j):
    """ Extract entries from the ith to jth position in each line """
    extracted_entries = []
    for line in lines:
        entries = line.split()
        extracted_entries.append(entries[i:j + 1])
    return extracted_entries


def modify_second_bvh(first_file_entries, second_file, k):
    """ Modify the second BVH file by inserting entries from the first file after the kth entry """
    with open(second_file, 'r') as file:
        lines = file.readlines()

    frame_time_index = next(i for i, line in enumerate(lines) if 'Frame Time:' in line)
    modified_lines = lines[:frame_time_index + 1]

    # Process each line, inserting the entries from the first file at the specified position
    for line_num, line in enumerate(lines[frame_time_index + 1:]):
        if line_num >= len(first_file_entries):
            break  # Stop if the first file has fewer frames than this line number in the second file

        entries = line.split()
        # Insert the entries from the first file after the kth entry of the second file's line
        new_line_entries = entries[:k] + first_file_entries[line_num] + entries[k:]
        modified_line = ' '.join(new_line_entries)
        modified_lines.append(modified_line + '\n')

    with open(second_file, 'w') as file:
        file.writelines(modified_lines)



def count_total_channels(bvh_file):
    """ Count the total number of channels in the BVH file's hierarchy """
    total_channels = 0
    in_hierarchy = False

    with open(bvh_file, 'r') as file:
        for line in file:
            # Check if the hierarchy section has started
            if 'HIERARCHY' in line:
                in_hierarchy = True
            elif 'MOTION' in line:
                break  # End of the hierarchy section

            if in_hierarchy and line.strip().startswith('CHANNELS'):
                # Extract the number of channels from this line
                parts = line.split()
                if len(parts) > 1:
                    try:
                        channels = int(parts[1])
                        total_channels += channels
                    except ValueError:
                        print(f"Warning: Non-integer channel count in line: {line.strip()}")

    return total_channels

# Example usage
# bvh_file = '__Run.bvh'
# print("Total Channels:", count_total_channels(bvh_file))

def modify_and_output_to_new_file(first_file_entries, second_file, output_file, i, j, k):
    """ Modify the second BVH file based on the first file's entries and output to a new file """
    with open(second_file, 'r') as file:
        lines = file.readlines()

    frame_time_index = next(i for i, line in enumerate(lines) if 'Frame Time:' in line)
    modified_lines = lines[:frame_time_index + 1]
    second_file_frame_count = len(lines) - frame_time_index - 1

    for line_num, first_file_line in enumerate(first_file_entries):
        if line_num < second_file_frame_count:
            entries = lines[frame_time_index + 1 + line_num].split()
            new_line_entries = entries[:k] + first_file_line + entries[k:]
        else:
            new_line_entries = ['0'] * k + first_file_line + ['0'] * (j - i + 1)

        modified_line = ' '.join(new_line_entries)
        modified_lines.append(modified_line + '\n')

    with open(output_file, 'w') as file:
        file.writelines(modified_lines)


def get_joint_channel_index(bvh_file, joint_name):
    """Get the index of the first channel associated with the specified joint."""
    with open(bvh_file, 'r') as file:
        lines = file.readlines()

    # Find the index where joint information starts
    joint_index = -1
    for idx, line in enumerate(lines):
        if line.strip().startswith('JOINT {}'.format(joint_name.upper())):
            joint_index = idx
            break

    if joint_index == -1:
        print("Joint '{}' not found in the BVH file.".format(joint_name))
        return None

    # Find the line where channels are defined for the joint
    channels_line_index = lines.index('OFFSET 0.00 0.00 0.00\n', joint_index) + 1

    # Extract the channels associated with the joint
    channels = lines[channels_line_index].split()[1:]

    # Determine the number of channels (each channel could have 3 or 6 values)
    num_channels = len(channels)
    if num_channels % 3 == 0:
        num_channels = num_channels // 3
    else:
        num_channels = num_channels // 6

    # Find the index of the first channel associated with the joint
    first_channel_index = channels_line_index + 1

    return first_channel_index

# Example usage:
bvh_file = 'Ostrich.bvh'  # Assuming motion1.bvh contains the BVH data
joint_name = 'Bip01_Pelvis'  # Name of the joint you want to find the index of its first channel

first_channel_index = get_joint_channel_index(bvh_file, joint_name)
if first_channel_index is not None:
    print("Index of the first channel associated with joint '{}': {}".format(joint_name, first_channel_index))


# Example usage
# first_bvh = 'Flying.bvh'
# second_bvh = 'GoatRun.bvh'
# output_bvh = 'out3.bvh'  # Path for the new output file
# i, j, k = 36, 95, 23  # example indices

# first_file_lines = read_bvh_frames(first_bvh)
# extracted_entries = extract_entries(first_file_lines, i, j)
# modify_and_output_to_new_file(extracted_entries, second_bvh, output_bvh, i, j, k)

print(count_total_channels('Crab.bvh'))
print(count_total_channels('Ostrich.bvh'))
print(count_total_channels('Flying.bvh'))
print(count_total_channels('out.bvh'))

first_bvh = 'Crab.bvh'
second_bvh = 'OstrichAtt.bvh'
output_bvh = 'out1.bvh'  # Path for the new output file
i, j, k = 228, 323, 293  # example indices

first_file_lines = read_bvh_frames(first_bvh)
extracted_entries = extract_entries(first_file_lines, i, j)
modify_and_output_to_new_file(extracted_entries, second_bvh, output_bvh, i, j, k)