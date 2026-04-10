import os
import re
from typing import List, Dict, Any
import pdfplumber
from datetime import datetime

from app.core.utils import clear_series, parse_price_and_date_one_line, parse_opt_price
from app.core.exceptions import ParsingError
from app.core.parse_classes import Settings


def parse_pdf(pdf_path: str, settings_obj: Settings, doc_type: str) -> List[Dict[str, Any]]:
    """
    Выполняет парсинг PDF-файла и возвращает список записей.
    settings_obj – экземпляр класса Settings
    doc_type – "Reestr" или "Protocol"
    """
    tables_data = []
    count_pages = 0
    
    with pdfplumber.open(pdf_path) as pdf:
        table_settings = {
            "vertical_strategy": "lines",
            "horizontal_strategy": "lines",
            "snap_tolerance": 4,
        }
        count_pages = len(pdf.pages)
        stop_on_page = 0

        if settings_obj.params.table_settings.three_copies_in_one_file:
            if count_pages % 3 == 0:
                stop_on_page = int(count_pages / 3)
            elif count_pages % 2 == 0:
                stop_on_page = int(count_pages / 2)

        for page in pdf.pages:
            if stop_on_page != 0 and page.page_number > stop_on_page:
                break

            tables = page.extract_tables(table_settings)
            if len(tables) == 0 and page.page_number == 1:
                if page.images:
                    raise ParsingError("Изображение вместо таблицы")
                else:
                    raise ParsingError("Нет таблиц в документе")

            for table in tables:
                # Обработка многостраничных таблиц (как в оригинале)
                if page.page_number > 1:
                    if settings_obj.params.table_settings.table_shift_control:
                        if tables[-1][-1][1] is None:
                            break
                        if 'подпись уполномоченного лица' in str(tables[-1][-1][1]):
                            break
                    else:
                        if tables[-1][-1][0] is None:
                            break

                    if settings_obj.params.table_settings.headings_on_every_page:
                        cur_table = table[settings_obj.params.table_settings.count_row_heders_other_pages:]
                    else:
                        cur_table = table
                else:
                    cur_table = table

                if settings_obj.params.table_settings.two_page_table and page.page_number % 2 == 0:
                    continue

                strip_row = False
                if settings_obj.params.table_settings.table_shift_control:
                    if doc_type == 'Protocol':
                        if len(cur_table[0]) in (21, 23):
                            strip_row = True
                    else:
                        if len(cur_table[0]) in (16, 10):
                            strip_row = True

                for row in cur_table:
                    if strip_row:
                        row = row[1:]
                    if any(cell and str(cell).strip() for cell in row):
                        tables_data.append([str(cell).strip() if cell else "" for cell in row])

    results = []
    row_start = settings_obj.params.table_settings.start_row_table
    if settings_obj.params.table_settings.remove_shift_tail_if_one_page:
        if count_pages == 1:
            row_stop = len(tables_data)
        else:
            row_stop = -settings_obj.params.table_settings.stop_row_table if settings_obj.params.table_settings.stop_row_table != 0 else len(tables_data)
    else:
        row_stop = -settings_obj.params.table_settings.stop_row_table if settings_obj.params.table_settings.stop_row_table != 0 else len(tables_data)

    for row_table in tables_data[row_start:row_stop]:
        skip_row = False
        for cell in row_table:
            if 'МНН' in cell or 'Мнн' in cell or 'мнн' in cell:
                skip_row = True
                break
        
        if not skip_row:
            if doc_type == 'Reestr':
                if settings_obj.params.columns.column_por_num is None:
                    skip_row = True
                if not row_table[0] and not row_table[1]:
                    skip_row = True
            if doc_type == 'Protocol':
                if not row_table[settings_obj.params.columns.column_name_tov]:
                    skip_row = True
            if settings_obj.params.table_settings.check_headings_on_every_page:
                if row_table[settings_obj.params.columns.column_series].strip().lower() == 'серия':
                    skip_row = True

        if skip_row:
            continue

        name_tov = str(row_table[settings_obj.params.columns.column_name_tov]).replace('\n', ' ')
        name_proizvod = str(row_table[settings_obj.params.columns.column_proizv]).replace('\n', ' ')

        if settings_obj.params.table_settings.series_and_expiration_date_combined:
            combined_str = str(row_table[settings_obj.params.columns.column_series])
            parts = combined_str.split(sep=settings_obj.params.table_settings.separator_series_and_expiration)
            series = parts[0].strip()
            expiration_date = parts[1].strip() if len(parts) > 1 else ''
        else:
            series = str(row_table[settings_obj.params.columns.column_series])
            expiration_date = str(row_table[settings_obj.params.columns.column_expiry_date]) if settings_obj.params.columns.column_expiry_date is not None else ''
        
        if series and series[0] == "'":
            series = series[1:]
        series = series.replace('\n', '')
        if expiration_date and expiration_date[0] == "'":
            expiration_date = expiration_date[1:]

        data = {}
        if doc_type == 'Reestr':
            out_cols = settings_obj.out_colums
            data[out_cols.column_por_num] = row_table[settings_obj.params.columns.column_por_num]
            if settings_obj.params.columns.column_code_tov is not None:
                data[out_cols.column_code_tov] = row_table[settings_obj.params.columns.column_code_tov]
            data[out_cols.column_name_tov] = name_tov
            data[out_cols.column_series] = series
            if settings_obj.params.columns.column_count is not None:
                data[out_cols.column_count] = row_table[settings_obj.params.columns.column_count]
            data[out_cols.column_expiry_date] = expiration_date
            data[out_cols.column_proizv] = name_proizvod

        else:  # Protocol
            out_cols = settings_obj.out_colums
            if settings_obj.params.columns.column_por_num is not None:
                data[out_cols.column_por_num] = row_table[settings_obj.params.columns.column_por_num]
            data[out_cols.column_name_tov] = name_tov
            if settings_obj.params.table_settings.clear_string_series:
                series = clear_series(series)
            data[out_cols.column_series] = series
            if settings_obj.params.columns.column_expiry_date is not None:
                data[out_cols.column_expiry_date] = expiration_date
            data[out_cols.column_proizv] = name_proizvod
            if settings_obj.params.columns.column_max_proizv_price is not None:
                data[out_cols.column_max_proizv_price] = row_table[settings_obj.params.columns.column_max_proizv_price]

            if not settings_obj.params.table_settings.proizv_price_and_sale_date_one_line:
                if settings_obj.params.columns.column_price_proizv_no_nds is not None:
                    data[out_cols.column_price_proizv_no_nds] = row_table[settings_obj.params.columns.column_price_proizv_no_nds]
                if settings_obj.params.columns.column_price_proizv_s_nds is not None:
                    data[out_cols.column_price_proizv_s_nds] = row_table[settings_obj.params.columns.column_price_proizv_s_nds]
                if settings_obj.params.columns.column_sale_date_proizv is not None:
                    data[out_cols.column_sale_date_proizv] = row_table[settings_obj.params.columns.column_sale_date_proizv]
            else:
                text_cell = row_table[settings_obj.params.columns.column_price_proizv_no_nds]
                price_no_nds, price_nds, sale_date = parse_price_and_date_one_line(text_cell)
                data[out_cols.column_price_proizv_no_nds] = price_no_nds
                data[out_cols.column_price_proizv_s_nds] = price_nds
                data[out_cols.column_sale_date_proizv] = sale_date

            if settings_obj.params.columns.column_count is not None:
                data[out_cols.column_count] = row_table[settings_obj.params.columns.column_count]

            if not settings_obj.params.table_settings.opt_price_one_line:
                if settings_obj.params.columns.column_opt_price_no_nds is not None:
                    data[out_cols.column_opt_price_no_nds] = row_table[settings_obj.params.columns.column_opt_price_no_nds]
                if settings_obj.params.columns.column_opt_price_s_nds is not None:
                    data[out_cols.column_opt_price_s_nds] = row_table[settings_obj.params.columns.column_opt_price_s_nds]
            else:
                text_cell = row_table[settings_obj.params.columns.column_opt_price_no_nds] if settings_obj.params.columns.column_opt_price_no_nds is not None else ''
                if text_cell:
                    opt_no, opt_nds = parse_opt_price(text_cell)
                    data[out_cols.column_opt_price_no_nds] = opt_no
                    data[out_cols.column_opt_price_s_nds] = opt_nds
                else:
                    data[out_cols.column_opt_price_no_nds] = '-'
                    data[out_cols.column_opt_price_s_nds] = '-'

        results.append(data)

    return results
