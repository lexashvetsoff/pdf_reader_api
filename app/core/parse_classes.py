class TableSettings:
    def __init__(self, data):
        self.row_table_headers: int = data['row_table_headers']
        self.start_row_table: int = data['start_row_table']
        self.stop_row_table: int = data['stop_row_table']
        self.headings_on_every_page: bool = data['headings_on_every_page']
        self.count_row_heders_other_pages: int = data['count_row_heders_other_pages']
        self.series_and_expiration_date_combined: bool = data['series_and_expiration_date_combined']
        self.separator_series_and_expiration: str = data['separator_series_and_expiration']
        self.clear_string_series: bool = data['clear_string_series']
        self.proizv_price_and_sale_date_one_line: bool = data["proizv_price_and_sale_date_one_line"]
        self.opt_price_one_line: bool = data["opt_price_one_line"]
        self.two_page_table: bool = data["two_page_table"]
        self.remove_shift_tail_if_one_page: bool = data["remove_shift_tail_if_one_page"]
        self.check_headings_on_every_page: bool = data["check_headings_on_every_page"]
        self.table_shift_control: bool = data["table_shift_control"]
        self.three_copies_in_one_file: bool = data["three_copies_in_one_file"]


class OutputSettings:
    def __init__(self, data):
        self.output_format: str = data['output_format']


class ReestrColumns:
    def __init__(self, data):
        self.column_por_num: int = data['column_por_num']
        self.column_code_tov: int = data['column_code_tov']
        self.column_name_tov: int = data['column_name_tov']
        self.column_series: int = data['column_series']
        self.column_count: int = data['column_count']
        self.column_expiry_date: int = data['column_expiry_date']
        self.column_proizv: int = data['column_proizv']


class Reestr:
    def __init__(self, data):
        self.table_settings = TableSettings(data['table_settings'])
        self.columns = ReestrColumns(data['columns'])
        self.output_settings = OutputSettings(data['output_settings'])


class ProtocolColumns:
    def __init__(self, data):
        self.column_por_num: int = data['column_por_num']
        self.column_name_tov: int = data['column_name_tov']
        self.column_series: int = data['column_series']
        self.column_expiry_date: int = data['column_expiry_date']
        self.column_proizv: int = data['column_proizv']
        self.column_price_proizv_no_nds: int = data['column_price_proizv_no_nds']
        self.column_price_proizv_s_nds: int = data['column_price_proizv_s_nds']
        self.column_max_proizv_price: int = data['column_max_proizv_price']
        self.column_count: int = data['column_count']
        self.column_opt_price_no_nds: int = data['column_opt_price_no_nds']
        self.column_opt_price_s_nds: int = data['column_opt_price_s_nds']
        self.column_sale_date_proizv: int = data['column_sale_date_proizv']


class Protocol:
    def __init__(self, data):
        self.table_settings = TableSettings(data['table_settings'])
        self.columns = ProtocolColumns(data['columns'])
        self.output_settings = OutputSettings(data['output_settings'])


class ReestrOutputColumns:
    def __init__(self, data):
        self.column_por_num = data["column_por_num"]
        self.column_name_tov = data["column_name_tov"]
        self.column_code_tov = data["column_code_tov"]
        self.column_series = data["column_series"]
        self.column_expiry_date = data["column_expiry_date"]
        self.column_count = data["column_count"]
        self.column_proizv = data["column_proizv"]


class ProtocolOutputColumns:
    def __init__(self, data):
        self.column_por_num = data['column_por_num']
        self.column_name_tov = data['column_name_tov']
        self.column_series = data['column_series']
        self.column_expiry_date = data['column_expiry_date']
        self.column_proizv = data['column_proizv']
        self.column_price_proizv_no_nds = data['column_price_proizv_no_nds']
        self.column_price_proizv_s_nds = data['column_price_proizv_s_nds']
        self.column_max_proizv_price = data['column_max_proizv_price']
        self.column_count = data['column_count']
        self.column_opt_price_no_nds = data['column_opt_price_no_nds']
        self.column_opt_price_s_nds = data['column_opt_price_s_nds']
        self.column_sale_date_proizv = data['column_sale_date_proizv']


class Settings:
    def __init__(self, data_name_columns, data_params, type_data):
        # type_data: 'Reestr' or 'Protocol'
        if type_data == 'Reestr':
            self.out_colums = ReestrOutputColumns(data_name_columns['Reestr'])
            self.params = Reestr(data_params['Reestr'])
        elif type_data == 'Protocol':
            self.out_colums = ProtocolOutputColumns(data_name_columns['Protocol'])
            self.params = Protocol(data_params['Protocol'])
        else:
            raise ValueError
