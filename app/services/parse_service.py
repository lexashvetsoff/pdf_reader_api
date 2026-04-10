from typing import Dict, Any, Union, List
from app.core.parse_classes import Settings
from app.core.parser import parse_pdf
from app.core.exceptions import SettingsNotFoundError
from app.core.converters import list_dict_to_xml_string


def run_parsing(
    pdf_path: str,
    code: str,
    doc_type: str,
    raw_settings: Dict[str, Any],
    requested_output_format: str = None
):
    if code not in raw_settings:
        raise SettingsNotFoundError(f"Код поставщика '{code}' не найден в settings.json")
    
    # Создаём объект Settings так же, как в original main.py
    settings_obj = Settings(
        raw_settings['output_columns_name'],
        raw_settings[code],
        doc_type
    )
    
    results = parse_pdf(pdf_path, settings_obj, doc_type)
    
    output_fmt = requested_output_format or settings_obj.params.output_settings.output_format
    if output_fmt == "json":
        return results, "json"
    elif output_fmt == "xml":
        xml_str = list_dict_to_xml_string(results)
        return xml_str, "xml"
    else:
        raise ValueError(f"Неподдерживаемый формат: {output_fmt}")
