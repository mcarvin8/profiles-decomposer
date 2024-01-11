import logging
import sys
import xml.etree.ElementTree as ET

logging.basicConfig(format='%(message)s', level=logging.DEBUG)
PROFILE_TYPE = ['Profile']
ns = {'sforce': 'http://soap.sforce.com/2006/04/metadata'}

def read_package_xml(package_path):
    """Read the package.xml file to get a list of Profile names."""
    profiles = []
    tree = ET.parse(package_path)
    root = tree.getroot()

    for metadata_type in root.findall('sforce:types', ns):
        metadata_name = metadata_type.find('sforce:name', ns).text
        if metadata_name in PROFILE_TYPE:
            metadata_members = metadata_type.findall('sforce:members', ns)
            for member in metadata_members:
                profiles.append(member.text)
    if not profiles:
        logging.info('Profiles were not found in the package.')
        logging.info('Skipping profiles compilation.')
        sys.exit(0)
    return profiles
