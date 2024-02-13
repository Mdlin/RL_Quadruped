def modify_bvh_motion(bvh_file, start_idx, end_idx, output_file_1, output_file_2):
    with open(bvh_file, 'r') as file:
        lines = file.readlines()

    # Find the index where motion data starts
    motion_index = lines.index('MOTION\n') + 3

    # Extract motion data
    motion_data = lines[motion_index:]

    # Split motion data into frames
    frames = [frame.split() for frame in motion_data]

    # Modify motion data for the first output file
    modified_frames_1 = []
    modified_frames_2 = []
    for frame in frames:
        modified_frame_1 = frame.copy()
        modified_frame_2 = frame.copy()
        for idx in range(start_idx, end_idx + 1):
            modified_frame_1[idx] = '0'
        for idx in range(len(frame)):
            if idx < start_idx or idx > end_idx:
                modified_frame_2[idx] = '0'
        modified_frames_1.append(modified_frame_1)
        modified_frames_2.append(modified_frame_2)

    # Write out two new BVH files with modified motion data
    with open(output_file_1, 'w') as file:
        file.writelines(lines[:motion_index])
        for frame in modified_frames_1:
            file.write(' '.join(frame) + '\n')

    with open(output_file_2, 'w') as file:
        file.writelines(lines[:motion_index])
        for frame in modified_frames_2:
            file.write(' '.join(frame) + '\n')


# Example usage:
bvh_file = 'out.bvh'  # Path to the original BVH file
start_idx = 24  # Start index of the range of channels to set to zero
end_idx = 83  # End index of the range of channels to set to zero
output_file_1 = 'motion_modified_1.bvh'  # Output file with specified range set to zero
output_file_2 = 'motion_modified_2.bvh'  # Output file with every other channel set to zero

modify_bvh_motion(bvh_file, start_idx, end_idx, output_file_1, output_file_2)
