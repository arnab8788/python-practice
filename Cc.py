import xml.etree.ElementTree as ET
from typing import List, Dict
import os

SQL_KEYWORDS = ['SQL QUERY', 'PRE SQL', 'POST SQL', 'Sql Query', 'Pre SQL', 'Post SQL']

def parse_xml(file_path: str) -> ET.Element:
    tree = ET.parse(file_path)
    return tree.getroot()

def extract_queries(xml_path: str) -> List[Dict]:
    root = parse_xml(xml_path)
    queries = []
    for folder in root.findall('.//FOLDER'):
        folder_name = folder.attrib.get('NAME', '')

        # Index all mappings by name
        mappings = {m.attrib['NAME']: m for m in folder.findall('.//MAPPING')}

        # Worklet instance mapping: {instance_name: reusable_worklet_name}
        worklet_instance_map = {}
        for workflow in folder.findall('.//WORKFLOW'):
            for task_instance in workflow.findall('.//TASKINSTANCE'):
                if task_instance.attrib.get('TYPE') == 'Worklet':
                    worklet_instance_map[task_instance.attrib['NAME']] = task_instance.attrib['TASKNAME']

        for workflow in folder.findall('.//WORKFLOW'):
            wf_name = workflow.attrib.get('NAME')
            sessions_in_workflow = workflow.findall('.//SESSION')

            # Find sessions directly under workflow or inside worklet instances
            for session in sessions_in_workflow:
                queries += process_session(
                    session=session,
                    folder_name=folder_name,
                    workflow_name=wf_name,
                    mappings=mappings,
                    worklet_name='',
                    worklet_instance_name=''
                )

        # Process standalone worklets and relate them to workflows via instance map
        for worklet in folder.findall('.//WORKLET'):
            worklet_name = worklet.attrib.get('NAME')
            for workflow in folder.findall('.//WORKFLOW'):
                wf_name = workflow.attrib.get('NAME')
                for task_instance in workflow.findall('.//TASKINSTANCE'):
                    if task_instance.attrib.get('TASKNAME') == worklet_name:
                        worklet_instance_name = task_instance.attrib['NAME']
                        for session in worklet.findall('.//SESSION'):
                            queries += process_session(
                                session=session,
                                folder_name=folder_name,
                                workflow_name=wf_name,
                                mappings=mappings,
                                worklet_name=worklet_name,
                                worklet_instance_name=worklet_instance_name
                            )
    return queries

def process_session(session, folder_name, workflow_name, mappings, worklet_name, worklet_instance_name) -> List[Dict]:
    session_name = session.attrib.get('NAME')
    mapping_name = session.attrib.get('MAPPINGNAME')
    results = []

    # Step 1: Session-level SQLs
    for attr in session.findall('.//ATTRIBUTE'):
        name = attr.attrib.get('NAME', '').upper()
        value = (attr.text or '').strip()
        if value and any(k in name for k in SQL_KEYWORDS):
            results.append(make_record(folder_name, workflow_name, worklet_name, worklet_instance_name,
                                       session_name, '', mapping_name, '', '', '', name, value))

    # Step 2: Transformation-level SQLs in session overrides
    for s_inst in session.findall('.//SESSTRANSFORMATIONINST'):
        trans_inst = s_inst.attrib.get('TRANSFORMATIONINSTNAME')
        trans_name = s_inst.attrib.get('TRANSFORMATIONNAME')
        trans_type = s_inst.attrib.get('TRANSFORMATIONTYPE')
        inst_name = s_inst.attrib.get('INSTANCE')

        for attr in session.findall(f".//ATTRIBUTE[@TRANSFORMATIONINSTNAME='{trans_inst}']"):
            name = attr.attrib.get('NAME', '').upper()
            value = (attr.text or '').strip()
            if value and any(k in name for k in SQL_KEYWORDS):
                results.append(make_record(folder_name, workflow_name, worklet_name, worklet_instance_name,
                                           session_name, inst_name, mapping_name, trans_name,
                                           trans_inst, trans_type, name, value))

    # Step 3: Mapping-level transformation SQLs (not overridden)
    if mapping_name in mappings:
        mapping = mappings[mapping_name]
        for instance in mapping.findall('.//INSTANCE'):
            trans_name = instance.attrib.get('TRANSFORMATION_NAME', instance.attrib['NAME'])
            trans_inst = instance.attrib['NAME']
            trans_type = instance.attrib.get('TYPE', '')
            for trans in mapping.findall('./TRANSFORMATION'):
                if trans.attrib.get('NAME') == trans_name:
                    for attr in trans.findall('.//TABLEATTRIBUTE'):
                        name = attr.attrib.get('NAME', '').upper()
                        value = attr.attrib.get('VALUE', '').strip()
                        if value and any(k in name for k in SQL_KEYWORDS):
                            results.append(make_record(folder_name, workflow_name, worklet_name, worklet_instance_name,
                                                       session_name, '', mapping_name, trans_name,
                                                       trans_inst, trans_type, name, value))
    return results

def make_record(folder, workflow, worklet, worklet_inst, session, session_inst,
                mapping, trans, trans_inst, trans_type, query_type, query) -> Dict:
    return {
        'Folder Name': folder,
        'Workflow Name': workflow,
        'Worklet Name': worklet,
        'Worklet Instance Name': worklet_inst,
        'Session Name': session,
        'Session Instance Name': session_inst,
        'Mapping Name': mapping,
        'Transformation Name': trans,
        'Transformation Instance Name': trans_inst,
        'Transformation Type': trans_type,
        'Query Type': query_type,
        'Query': query
    }

# Example usage
if __name__ == "__main__":
    file_path = "wf_m_LOAD_DSPOLICY_CLONE.XML.txt"
    all_queries = extract_queries(file_path)
    print(f"\n✅ Extracted {len(all_queries)} queries:\n")
    for q in all_queries:
        print(q)
