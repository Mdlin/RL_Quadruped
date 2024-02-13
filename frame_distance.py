import numpy as np
from numpy.linalg import norm


def cosine_similarity(vector1, vector2):
    """Calculate cosine similarity between two vectors."""
    return np.dot(vector1, vector2) / (norm(vector1) * norm(vector2))


def rotation_matrix(axis, theta):
    """
    Return the rotation matrix associated with counterclockwise rotation about
    the given axis by theta radians.
    """
    axis = np.asarray(axis)
    axis = axis / np.sqrt(np.dot(axis, axis))
    a = np.cos(theta / 2.0)
    b, c, d = -axis * np.sin(theta / 2.0)
    return np.array([[a * a + b * b - c * c - d * d, 2 * (b * c - a * d), 2 * (b * d + a * c)],
                     [2 * (b * c + a * d), a * a + c * c - b * b - d * d, 2 * (c * d - a * b)],
                     [2 * (b * d - a * c), 2 * (c * d + a * b), a * a + d * d - b * b - c * c]])


def calculate_similarity_score(frame_a, frame_b):
    """Calculate the similarity score between two frames using global rotations obtained through direct kinematics."""
    # Calculate global rotations for each frame using direct kinematics
    global_rotation_a = np.eye(3)  # Identity matrix for the initial frame
    global_rotation_b = np.eye(3)  # Identity matrix for the initial frame

    for i in range(frame_a.shape[0]):  # Assuming frame_a and frame_b have the same joint hierarchy
        # Calculate rotation matrices for each axis
        rotation_x_a = rotation_matrix([1, 0, 0], frame_a[i, 0])
        rotation_y_a = rotation_matrix([0, 1, 0], frame_a[i, 1])
        rotation_z_a = rotation_matrix([0, 0, 1], frame_a[i, 2])

        rotation_x_b = rotation_matrix([1, 0, 0], frame_b[i, 0])
        rotation_y_b = rotation_matrix([0, 1, 0], frame_b[i, 1])
        rotation_z_b = rotation_matrix([0, 0, 1], frame_b[i, 2])

        # Apply rotations in order: ZYX (yaw, pitch, roll)
        global_rotation_a = np.dot(rotation_z_a, np.dot(rotation_y_a, np.dot(rotation_x_a, global_rotation_a)))
        global_rotation_b = np.dot(rotation_z_b, np.dot(rotation_y_b, np.dot(rotation_x_b, global_rotation_b)))

    # Compute similarity score based on the Frobenius norm of the difference between the global rotations
    similarity_score = np.trace(np.dot(global_rotation_a.T, global_rotation_b)) / 3.0

    return abs(similarity_score)


def read_bvh_file(filename):
    """Read a BVH file and extract joint orientations for each frame."""
    with open(filename, 'r') as file:
        lines = file.readlines()

    # Find the index where motion data starts
    data_index = lines.index('MOTION\n') + 1

    # Extract frame count and joint count
    frame_count = int(lines[data_index].split()[1])
    joint_count = len(lines[data_index + 2].split()) // 3

    # Initialize array to store joint orientations for each frame
    joint_orientations = np.zeros((frame_count, joint_count, 3))

    # Extract joint orientations for each frame
    for i in range(frame_count):
        frame_data = lines[data_index + 2 + i].split()
        for j in range(joint_count):
            joint_data = frame_data[j * 3: (j + 1) * 3]
            joint_orientations[i, j] = np.array([float(x) for x in joint_data])

    return joint_orientations


# Read BVH files for motions 1 and 2
motion1_file = 'motion_modified_1.bvh'
motion2_file = 'motion_modified_2.bvh'

motion1_data = read_bvh_file(motion1_file)
motion2_data = read_bvh_file(motion2_file)

# Calculate similarity scores between corresponding frames of the two motions
similarity_scores = np.zeros((motion1_data.shape[0], motion2_data.shape[0]))

#for i in range(motion1_data.shape[0]):
#    for j in range(motion2_data.shape[0]):
#        similarity_scores[i, j] = calculate_similarity_score(motion1_data[i], motion2_data[j])

# Output the similarity scores
print("Similarity scores between corresponding frames of the two motions:")
print(similarity_scores)


def replace_zero_entries(bvh_file_1, bvh_file_2, output_file):
    """Replace zero entries in the first BVH file with entries from the second BVH file based on similarity scores."""
    with open(bvh_file_1, 'r') as file:
        lines_1 = file.readlines()
    with open(bvh_file_2, 'r') as file:
        lines_2 = file.readlines()

    # Find the index where motion data starts
    motion_index_1 = lines_1.index('MOTION\n') + 3
    motion_index_2 = lines_2.index('MOTION\n') + 3

    # Extract motion data
    motion_data_1 = lines_1[motion_index_1:]
    motion_data_2 = lines_2[motion_index_2:]

    # Split motion data into frames
    frames_1 = [list(map(float, frame.split())) for frame in motion_data_1]
    frames_2 = [list(map(float, frame.split())) for frame in motion_data_2]

    # Open the output file to write the modified motion data
    with open(output_file, 'w') as file:
        file.writelines(lines_1[:motion_index_1])  # Write the header of the first BVH file

        # Iterate through each frame of the first BVH file
        for frame_1 in frames_1:
            max_similarity_score = -1  # Initialize the maximum similarity score
            best_frame_2 = None  # Initialize the frame from the second BVH file with the highest similarity score

            # Compute similarity scores with all frames from the second BVH file
            for frame_2 in frames_2:
                similarity_score = calculate_similarity_score(np.array([frame_1]), np.array([frame_2]))
                if similarity_score > max_similarity_score:
                    max_similarity_score = similarity_score
                    best_frame_2 = frame_2

            # Replace zero entries in the first frame with entries from the selected frame in the second file
            modified_frame = [entry_1 if entry_1 != 0 else entry_2 for entry_1, entry_2 in zip(frame_1, best_frame_2)]

            # Write the modified frame to the output file
            file.write(' '.join(map(str, modified_frame)) + '\n')


# Example usage:
bvh_file_1 = 'motion_modified_1.bvh'  # First modified BVH file
bvh_file_2 = 'motion_modified_2.bvh'  # Second modified BVH file
output_file = 'motion_combined.bvh'  # Output file with zero entries replaced based on similarity scores

replace_zero_entries(bvh_file_1, bvh_file_2, output_file)