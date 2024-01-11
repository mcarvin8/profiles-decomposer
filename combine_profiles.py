import argparse
import logging
import os
import xml.etree.ElementTree as ET
from xml.dom import minidom

import parse_package


logging.basicConfig(format='%(message)s', level=logging.DEBUG)


def parse_args():
    """Function to parse command line arguments."""
    parser = argparse.ArgumentParser(description='A script to combine profile files.')
    parser.add_argument('-o', '--output', default='force-app/main/default/profiles')
    parser.add_argument('-m', '--manifest', default=None)
    args = parser.parse_args()
    return args


def read_individual_xmls(profile_directory, manifest):
    """Read each XML file."""
    individual_xmls = {}

    if manifest:
        package_profiles = parse_package.read_package_xml(manifest)
    else:
        package_profiles = None

    def process_profile_file(filepath, parent_profile_name):
        tree = ET.parse(filepath)
        root = tree.getroot()
        individual_xmls.setdefault(parent_profile_name, []).append(root)

    for root, _, files in os.walk(profile_directory):
        for filename in files:
            if filename.endswith('.xml') and not filename.endswith('.profile-meta.xml'):
                file_path = os.path.join(root, filename)
                relative_path = os.path.relpath(file_path, profile_directory)
                parent_profile_name = relative_path.split(os.path.sep)[0]
                if not manifest or (manifest and parent_profile_name in package_profiles):
                    process_profile_file(file_path, parent_profile_name)

    return individual_xmls, package_profiles


def has_subelements(element):
    """Check if an XML element has sub-elements."""
    return any(element.iter())


def merge_xml_content(individual_xmls):
    """Merge XMLs for each object."""
    merged_xmls = {}
    for parent_profile_name, individual_roots in individual_xmls.items():
        parent_profile_root = ET.Element('Profile', xmlns="http://soap.sforce.com/2006/04/metadata")

        for matching_root in individual_roots:
            tag = matching_root.tag
            # Check if the root has sub-elements
            if has_subelements(matching_root):
                # Create a new XML element for each sub-element
                child_element = ET.Element(tag)
                parent_profile_root.append(child_element)
                child_element.extend(matching_root)
            else:
                # Extract text content from single-element XML and append to the parent
                text_content = matching_root.text
                if text_content:
                    child_element = ET.Element(tag)
                    child_element.text = text_content
                    parent_profile_root.append(child_element)

        merged_xmls[parent_profile_name] = parent_profile_root

    return merged_xmls


def format_and_write_xmls(merged_xmls, profile_directory):
    """Create the final XMLs."""
    for parent_profile_name, parent_profile_root in merged_xmls.items():
        # Load the parent profile meta file with the single elements first
        existing_profile_file_path = os.path.join(profile_directory, parent_profile_name, f'{parent_profile_name}.profile-meta.xml')
        if os.path.exists(existing_profile_file_path):
            existing_tree = ET.parse(existing_profile_file_path)
            existing_root = existing_tree.getroot()

            # Iterate through the sub-elements in the existing profile
            for existing_sub_element in existing_root:
                # Check if the sub-element is not already present in the merged XML
                if not any(existing_sub_element.tag == child.tag for child in parent_profile_root):
                    parent_profile_root.append(existing_sub_element)

        parent_xml_str = ET.tostring(parent_profile_root, encoding='utf-8').decode('utf-8')
        formatted_xml = minidom.parseString(parent_xml_str).toprettyxml(indent="    ")

        # Remove extra new lines
        formatted_xml = '\n'.join(line for line in formatted_xml.split('\n') if line.strip())

        # Remove existing XML declaration
        formatted_xml = '\n'.join(line for line in formatted_xml.split('\n') if not line.strip().startswith('<?xml'))

        parent_profile_filename = os.path.join(profile_directory, f'{parent_profile_name}.profile-meta.xml')
        with open(parent_profile_filename, 'wb') as file:
            # Include encoding information in the XML header
            file.write(f'<?xml version="1.0" encoding="UTF-8"?>\n{formatted_xml}'.encode('utf-8'))


def combine_profiles(profile_directory, manifest):
    """Combine the profiles for deployments."""
    individual_xmls, package_profiles = read_individual_xmls(profile_directory, manifest)
    merged_xmls = merge_xml_content(individual_xmls)
    format_and_write_xmls(merged_xmls, profile_directory)

    if manifest:
        logging.info("The profiles for %s have been compiled for deployments.",
                     ', '.join(map(str, package_profiles)))
    else:
        logging.info('The profiles have been compiled for deployments.')


def main(output_directory, manifest):
    """Main function."""
    combine_profiles(output_directory, manifest)


if __name__ == '__main__':
    inputs = parse_args()
    main(inputs.output, inputs.manifest)
