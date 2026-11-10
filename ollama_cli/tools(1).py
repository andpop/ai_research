"""
Модуль инструментов (tools) для чат-бота.
Содержит описания функций для модели и их реализации.
"""

import os
from datetime import datetime

LOG_FILE = 'chat.log'

# Рабочая директория — устанавливается при инициализации
_WORKING_DIR = None


def init_tools(working_dir: str) -> None:
    """Инициализирует модуль инструментов рабочей директорией."""
    global _WORKING_DIR
    _WORKING_DIR = working_dir


def get_working_dir() -> str:
    return _WORKING_DIR or os.getcwd()


# ====== Реализации функций ======

def read_file(path: str) -> str:
    """Прочитать содержимое текстового файла."""
    # Защита от галлюцинаций: если модель дала абсолютный путь, берём только имя
    if os.path.isabs(path):
        path = os.path.basename(path)
    
    full_path = os.path.join(get_working_dir(), path)
    
    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        available = list_files('.')
        return f'Ошибка: файл "{path}" не найден в {get_working_dir()}.\nДоступные файлы:\n{available}'
    except Exception as e:
        return f'Ошибка чтения файла: {e}'


def append_log(message: str) -> str:
    """Добавить строку в лог-файл журнала."""
    try:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        line = f'[{timestamp}] {message}\n'
        log_path = os.path.join(get_working_dir(), LOG_FILE)
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(line)
        return f'Запись успешно добавлена в {LOG_FILE}.'
    except Exception as e:
        return f'Ошибка записи в лог: {e}'


def list_files(directory: str = '.') -> str:
    """Показать список файлов в директории."""
    try:
        full_path = os.path.join(get_working_dir(), directory)
        if not os.path.isdir(full_path):
            return f'Директория "{directory}" не найдена.'
        
        items = []
        for item in sorted(os.listdir(full_path)):
            item_path = os.path.join(full_path, item)
            prefix = '📁 ' if os.path.isdir(item_path) else '📄 '
            items.append(f'{prefix}{item}')
        
        if not items:
            return f'Директория "{directory}" пуста.'
        
        return '\n'.join(items)
    except Exception as e:
        return f'Ошибка чтения директории: {e}'


# Словарь-диспетчер: имя функции -> её реализация
FUNCTIONS = {
    'read_file': read_file,
    'append_log': append_log,
    'list_files': list_files,
}


# ====== Описания инструментов для модели ======

def get_tool_definitions() -> list:
    """Возвращает JSON-схемы инструментов с подставленной рабочей директорией."""
    wd = get_working_dir()
    return [
        {
            'type': 'function',
            'function': {
                'name': 'read_file',
                'description': (
                    f'Прочитать содержимое текстового файла. '
                    f'Путь указывается ОТНОСИТЕЛЬНО рабочей директории: {wd}. '
                    f'НЕ придумывай пути — используй имя файла как есть, например "notes.txt".'
                ),
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'path': {
                            'type': 'string',
                            'description': 'Имя файла или относительный путь. Например: "notes.txt" или "docs/readme.md".',
                        }
                    },
                    'required': ['path'],
                },
            },
        },
        {
            'type': 'function',
            'function': {
                'name': 'append_log',
                'description': 'Добавить строку в лог-файл журнала. Строка автоматически снабжается временной меткой.',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'message': {
                            'type': 'string',
                            'description': 'Текст, который нужно записать в лог.',
                        }
                    },
                    'required': ['message'],
                },
            },
        },
        {
            'type': 'function',
            'function': {
                'name': 'list_files',
                'description': (
                    f'Показать список файлов в рабочей директории ({wd}) '
                    f'или указанной поддиректории. Полезно, чтобы узнать, какие файлы существуют.'
                ),
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'directory': {
                            'type': 'string',
                            'description': 'Путь к директории (относительно рабочей). По умолчанию — текущая директория.',
                        }
                    },
                    'required': [],
                },
            },
        },
    ]


def get_system_prompt() -> str:
    """Возвращает системный промпт с информацией о рабочей директории."""
    wd = get_working_dir()
    return f"""Ты помощник с доступом к файлам. 
Текущая рабочая директория: {wd}

ВАЖНЫЕ ПРАВИЛА:
1. Используй ТОЛЬКО относительные пути (например, "notes.txt"), НЕ придумывай абсолютные пути вроде "/path/..."
2. Если не уверен в имени файла — сначала вызови list_files, чтобы посмотреть, какие файлы есть
3. Имена файлов пиши точно так, как их назвал пользователь
"""

