import xml.etree.ElementTree as ET
import os
from typing import List, Dict

QUERY_KEYWORDS = ['SQL QUERY', 'PRE SQL', 'POST SQL', 'Sql Query', 'Pre SQL', 'Post SQL']

def extract_queries_from_informatica_xml(xml_file: str) -> List[Dict]:
    tree = ET.parse(xml_file)
    root = tree.getroot()
    queries = []

    folders = root.findall('.//FOLDER')
    for folder in folders:
        folder_name = folder.attrib['NAME']

        reusable_lookups = {}
        reusable_sessions = {}
        mappings = {m.attrib['NAME']: m for m in folder.findall('.//MAPPING')}

        # Cache reusable lookups
        for mapping in mappings.values():
            for trans in mapping.findall('./TRANSFORMATION'):
                if trans.attrib.get('TYPE') == 'Lookup Procedure' and trans.attrib.get('REUSABLE') == 'YES':
                    reusable_lookups[trans.attrib['NAME']] = trans

        # Sessions can be in workflows or worklets
        for wf_type in ['WORKFLOW', 'WORKLET']:
            for wf in folder.findall(f'.//{wf_type}'):
                workflow_name = wf.attrib['NAME']
                for session in wf.findall('.//SESSION'):
                    session_name = session.attrib['NAME']
                    mapping_name = session.attrib.get('MAPPINGNAME', '')
                    reusable_sessions[session_name] = session

                    queries += extract_session_attributes(
                        session=session,
                        folder_name=folder_name,
                        workflow_name=workflow_name,
                        session_name=session_name,
                        mapping_name=mapping_name,
                        reusable_lookups=reusable_lookups,
                        mappings=mappings,
                        is_worklet=(wf_type == 'WORKLET'),
                        worklet_name=workflow_name if wf_type == 'WORKLET' else ''
                    )

    return queries

def extract_session_attributes(session, folder_name, workflow_name, session_name,
                               mapping_name, reusable_lookups, mappings, is_worklet, worklet_name):
    results = []
    for attr in session.findall('.//ATTRIBUTE'):
        name = attr.attrib.get('NAME', '').upper()
        value = (attr.text or '').strip()
        if value and any(keyword in name for keyword in QUERY_KEYWORDS):
            results.append({
                'Folder Name': folder_name,
                'Workflow Name': workflow_name,
                'Worklet Name': worklet_name if is_worklet else '',
                'Worklet Instance Name': '',
                'Session Name': session_name,
                'Session Instance Name': '',
                'Mapping Name': mapping_name,
                'Transformation Name': '',  # Sometimes embedded in ATTRIBUTE name
                'Transformation Instance Name': '',
                'Transformation Type': '',
                'Query Type': name,
                'Query': value
            })

    # Check if session references transformations
    for s_inst in session.findall('.//SESSTRANSFORMATIONINST'):
        trans_name = s_inst.attrib.get('TRANSFORMATIONNAME')
        trans_type = s_inst.attrib.get('TRANSFORMATIONTYPE')
        inst_name = s_inst.attrib.get('TRANSFORMATIONINSTNAME')
        for attr in session.findall(f".//ATTRIBUTE[@TRANSFORMATIONINSTNAME='{inst_name}']"):
            name = attr.attrib.get('NAME', '').upper()
            value = (attr.text or '').strip()
            if value and any(keyword in name for keyword in QUERY_KEYWORDS):
                results.append({
                    'Folder Name': folder_name,
                    'Workflow Name': workflow_name,
                    'Worklet Name': worklet_name if is_worklet else '',
                    'Worklet Instance Name': '',
                    'Session Name': session_name,
                    'Session Instance Name': s_inst.attrib.get('INSTANCE'),
                    'Mapping Name': mapping_name,
                    'Transformation Name': trans_name,
                    'Transformation Instance Name': inst_name,
                    'Transformation Type': trans_type,
                    'Query Type': name,
                    'Query': value
                })

    # Also extract from mapping if defined there
    if mapping_name in mappings:
        results += extract_mapping_level_queries(
            mappings[mapping_name],
            folder_name,
            workflow_name,
            session_name,
            mapping_name,
            is_worklet,
            worklet_name
        )
    return results

def extract_mapping_level_queries(mapping, folder_name, workflow_name, session_name, mapping_name, is_worklet, worklet_name):
    results = []
    for instance in mapping.findall('.//INSTANCE'):
        inst_name = instance.attrib['NAME']
        trans_type = instance.attrib['TYPE']
        trans_ref = instance.attrib.get('TRANSFORMATION_NAME', inst_name)

        # Match transformation by name
        trans_node = next((t for t in mapping.findall('./TRANSFORMATION') if t.attrib['NAME'] == trans_ref), None)
        if not trans_node:
            continue

        for attr in trans_node.findall('.//TABLEATTRIBUTE'):
            name = attr.attrib.get('NAME', '').upper()
            value = (attr.attrib.get('VALUE') or '').strip()
            if value and any(keyword in name for keyword in QUERY_KEYWORDS):
                results.append({
                    'Folder Name': folder_name,
                    'Workflow Name': workflow_name,
                    'Worklet Name': worklet_name if is_worklet else '',
                    'Worklet Instance Name': '',
                    'Session Name': session_name,
                    'Session Instance Name': '',
                    'Mapping Name': mapping_name,
                    'Transformation Name': trans_ref,
                    'Transformation Instance Name': inst_name,
                    'Transformation Type': trans_type,
                    'Query Type': name,
                    'Query': value
                })
    return results

# Example usage
if __name__ == "__main__":
    input_path = 'wf_m_LOAD_DSPOLICY_CLONE.XML.txt'  # Change as needed
    queries = extract_queries_from_informatica_xml(input_path)
    for q in queries:
        print(q)
