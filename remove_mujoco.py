import xml.etree.ElementTree as ET

def remove_duplicate_geoms(mujoco_xml_file):
    # Load the MuJoCo XML file
    tree = ET.parse(mujoco_xml_file)
    root = tree.getroot()

    # Keep track of geom names
    geom_names = set()
    # Store geoms and their parents for potential removal
    geoms_to_remove = []

    # Iterate through all elements in the tree to find geoms and their parents
    for parent in root.iter():
        for geom in list(parent.findall('geom')):
            geom_name = geom.get("name")
            if geom_name in geom_names:
                # If the geom name is a duplicate, mark it and its parent for removal
                geoms_to_remove.append((parent, geom))
            else:
                geom_names.add(geom_name)

    # Remove the marked geoms from their respective parents
    for parent, geom in geoms_to_remove:
        parent.remove(geom)

    # Save the modified tree back to the file
    tree.write(mujoco_xml_file, encoding='utf-8', xml_declaration=True)

# Example usage
remove_duplicate_geoms("output.xml")
