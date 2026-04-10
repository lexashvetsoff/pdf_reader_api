import re
from datetime import datetime


from app.core.exceptions import PriceParsingError


def clear_series(text: str) -> str:
    """Удаляет из серии буквы и пробелы"""
    return re.sub(r'[\sа-яА-ЯёЁ]', '', text)


def parse_price_and_date_one_line(text: str):
    """
    Парсит строку вида '1 234,56 7 890,12 31.12.2024'
    Возвращает (price_no_nds, price_with_nds, date)
    """
    # Очищаем от лишних переносов
    _text = text.replace('\n00', '')
    _text = _text.replace(',\n', ',00 ')
    
    # Ищем все числа (целые или с двумя десятичными знаками)
    numbers = re.findall(r'[\d\s]+(?:,\d{2})?', _text)
    # Ищем дату
    date_match = re.search(r'\d{2}\.\d{2}\.\d{4}', _text)
    
    # Фильтруем числа: убираем пустые строки и преобразуем в float
    valid_numbers = []
    for num_str in numbers:
        num_str = num_str.strip()
        if num_str:
            # Заменяем пробелы и запятую на точку
            num_str = num_str.replace(' ', '').replace(',', '.')
            try:
                valid_numbers.append(float(num_str))
            except ValueError:
                pass
    
    if len(valid_numbers) >= 2 and date_match:
        date = datetime.strptime(date_match.group(), '%d.%m.%Y').date()
        return valid_numbers[0], valid_numbers[1], date
    else:
        raise PriceParsingError(f"Не удалось найти два числа и дату в строке: {text}")


def parse_opt_price(text: str):
    """
    Парсит строку с двумя ценами: '1 234,56 7 890,12'
    Возвращает (price_no_nds, price_with_nds)
    """
    _text = text.replace('\n00', '')
    _text = _text.replace(',\n', ',00 ')
    _text = _text.replace('\n', ' ')
    
    numbers = re.findall(r'[\d\s]+(?:,\d{2})?', _text)
    valid_numbers = []
    for num_str in numbers:
        num_str = num_str.strip()
        if num_str:
            num_str = num_str.replace(' ', '').replace(',', '.')
            try:
                valid_numbers.append(float(num_str))
            except ValueError:
                pass
    
    if len(valid_numbers) >= 2:
        return valid_numbers[0], valid_numbers[1]
    else:
        raise PriceParsingError(f"Не удалось найти два числа в строке: {text}")
