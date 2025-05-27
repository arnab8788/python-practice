import xml.etree.ElementTree as ET
from typing import List, Dict

QUERY_KEYWORDS = ['SQL QUERY', 'PRE SQL', 'POST SQL']

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

        for mapping in mappings.values():
            for trans in mapping.findall('./TRANSFORMATION'):
                if trans.attrib.get('TYPE') == 'Lookup Procedure' and trans.attrib.get('REUSABLE') == 'YES':
                    reusable_lookups[trans.attrib['NAME']] = trans

        workflows = folder.findall('.//WORKFLOW')
        for workflow in workflows:
            workflow_name = workflow.attrib['NAME']

            # Step 1: Map worklet instance names to actual reusable worklet names
            worklet_instance_map = {}
            for task_inst in workflow.findall('.//TASKINSTANCE'):
                if task_inst.attrib.get('TYPE') == 'Worklet':
                    instance_name = task_inst.attrib['NAME']
                    ref_name = task_inst.attrib.get('TASKNAME')  # this is the actual reusable worklet name
                    worklet_instance_map[instance_name] = ref_name

            # Step 2: Handle direct sessions
            for session in workflow.findall('.//SESSION'):
                session_name = session.attrib['NAME']
                mapping_name = session.attrib.get('MAPPINGNAME', '')
                queries += extract_session_attributes(
                    session=session,
                    folder_name=folder_name,
                    workflow_name=workflow_name,
                    session_name=session_name,
                    mapping_name=mapping_name,
                    reusable_lookups=reusable_lookups,
                    mappings=mappings,
                    is_worklet=False,
                    worklet_name='',
                    worklet_instance_name=''
                )

            # Step 3: Handle sessions inside worklets
            for worklet in folder.findall('.//WORKLET'):
                worklet_name = worklet.attrib['NAME']
                for session in worklet.findall('.//SESSION'):
                    session_name = session.attrib['NAME']
                    mapping_name = session.attrib.get('MAPPINGNAME', '')

                    # Resolve instance name from the workflow if used
                    for inst_name, wk_name in worklet_instance_map.items():
                        if wk_name == worklet_name:
                            queries += extract_session_attributes(
                                session=session,
                                folder_name=folder_name,
                                workflow_name=workflow_name,
                                session_name=session_name,
                                mapping_name=mapping_name,
                                reusable_lookups=reusable_lookups,
                                mappings=mappings,
                                is_worklet=True,
                                worklet_name=worklet_name,
                                worklet_instance_name=inst_name
                            )

    return queries

def extract_session_attributes(session, folder_name, workflow_name, session_name,
                               mapping_name, reusable_lookups, mappings, is_worklet,
                               worklet_name, worklet_instance_name):
    results = []
    for attr in session.findall('.//ATTRIBUTE'):
        name = attr.attrib.get('NAME', '').upper()
        value = (attr.text or '').strip()
        if value and any(keyword in name for keyword in QUERY_KEYWORDS):
            results.append({
                'Folder Name': folder_name,
                'Workflow Name': workflow_name,
                'Worklet Name': worklet_name if is_worklet else '',
                'Worklet Instance Name': worklet_instance_name if is_worklet else '',
                'Session Name': session_name,
                'Session Instance Name': '',
                'Mapping Name': mapping_name,
                'Transformation Name': '',
                'Transformation Instance Name': '',
                'Transformation Type': '',
                'Query Type': name,
                'Query': value
            })

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
                    'Worklet Instance Name': worklet_instance_name if is_worklet else '',
                    'Session Name': session_name,
                    'Session Instance Name': s_inst.attrib.get('INSTANCE'),
                    'Mapping Name': mapping_name,
                    'Transformation Name': trans_name,
                    'Transformation Instance Name': inst_name,
                    'Transformation Type': trans_type,
                    'Query Type': name,
                    'Query': value
                })

    if mapping_name in mappings:
        results += extract_mapping_level_queries(
            mappings[mapping_name],
            folder_name,
            workflow_name,
            session_name,
            mapping_name,
            is_worklet,
            worklet_name,
            worklet_instance_name
        )
    return results

def extract_mapping_level_queries(mapping, folder_name, workflow_name, session_name,
                                  mapping_name, is_worklet, worklet_name, worklet_instance_name):
    results = []
    for instance in mapping.findall('.//INSTANCE'):
        inst_name = instance.attrib['NAME']
        trans_type = instance.attrib['TYPE']
        trans_ref = instance.attrib.get('TRANSFORMATION_NAME', inst_name)

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
                    'Worklet Instance Name': worklet_instance_name if is_worklet else '',
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
    path = 'wf_m_LOAD_VPASONE_To_NLZ_DELETE_DSPOLICYMISCVALUE.XML.txt'  # or any other XML
    result = extract_queries_from_informatica_xml(path)
    for row in result:
        print(row)p
