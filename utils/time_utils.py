from datetime import datetime

def get_formatted_time():
    """Возвращает текущее время в формате строки."""
    now = datetime.now()
    return now.strftime("%d.%m.%Y • %H:%M")