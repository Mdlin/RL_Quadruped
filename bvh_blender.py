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


# Example usage
"""
#first_bvh = '__Flying.bvh'
#second_bvh = '__Run.bvh'
#i, j, k = 36, 95, 23  # example indices

#first_file_lines = read_bvh_frames(first_bvh)
#extracted_entries = extract_entries(first_file_lines, i, j)
#modify_second_bvh(extracted_entries, second_bvh, k)
"""

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

# Example usage
first_bvh = '__Flying.bvh'
second_bvh = '__Run.bvh'
output_bvh = '__Run2.bvh'  # Path for the new output file
i, j, k = 36, 95, 23  # example indices

first_file_lines = read_bvh_frames(first_bvh)
extracted_entries = extract_entries(first_file_lines, i, j)
modify_and_output_to_new_file(extracted_entries, second_bvh, output_bvh, i, j, k)
