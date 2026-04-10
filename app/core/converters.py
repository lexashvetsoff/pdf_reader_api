import xml.etree.ElementTree as ET
from typing import List, Dict, Any


def list_dict_to_xml_string(data: List[Dict[str, Any]], root_tag='root', element_tag='item') -> str:
    """Преобразует список словарей в XML-строку"""
    root = ET.Element(root_tag)
    for item in data:
        element = ET.SubElement(root, element_tag)
        for key, value in item.items():
            child = ET.SubElement(element, str(key))
            child.text = str(value)
    tree = ET.ElementTree(root)
    try:
        ET.indent(tree, space='    ', level=0)
    except AttributeError:
        pass
    # Возвращаем строку, а не пишем в файл
    import io
    with io.BytesIO() as f:
        tree.write(f, encoding='utf-8', xml_declaration=True)
        return f.getvalue().decode('utf-8')
