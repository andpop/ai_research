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


def _safe_path(path: str) -> str:
    """Нормализует путь и ограничивает его рабочей директорией.
    
    - Если путь абсолютный — берём только имя файла/директории.
    - Если путь выходит за пределы рабочей директории (через ../) — обрезаем.
    """
    # Защита от абсолютных путей, которые модель может выдумать
    if os.path.isabs(path):
        path = os.path.basename(path)
    
    # Собираем полный путь и нормализуем (убираем ../, ./ и т.д.)
    full_path = os.path.normpath(os.path.join(get_working_dir(), path))
    
    # Защита от выхода за пределы рабочей директории
    wd = os.path.normpath(get_working_dir())
    if not full_path.startswith(wd + os.sep) and full_path != wd:
        # Если путь выходит за пределы — берём только базовое имя
        return os.path.join(wd, os.path.basename(path))
    
    return full_path


# ====== Реализации функций ======

def read_file(path: str) -> str:
    """Прочитать содержимое текстового файла."""
    full_path = _safe_path(path)
    
    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        available = list_files('.')
        return f'Ошибка: файл "{path}" не найден в {get_working_dir()}.\nДоступные файлы:\n{available}'
    except IsADirectoryError:
        return f'Ошибка: "{path}" — это директория, а не файл.'
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
        full_path = _safe_path(directory)
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


def create_item(path: str, item_type: str = 'file') -> str:
    """Создать новый файл или директорию.
    
    Args:
        path: Относительный путь к создаваемому объекту.
        item_type: 'file' для создания файла, 'directory' для директории.
    """
    full_path = _safe_path(path)
    
    try:
        if os.path.exists(full_path):
            return f'Ошибка: "{path}" уже существует.'
        
        if item_type == 'directory':
            os.makedirs(full_path, exist_ok=True)
            return f'✅ Директория "{path}" успешно создана.'
        elif item_type == 'file':
            # Создаём родительскую директорию, если её нет
            parent = os.path.dirname(full_path)
            if parent and not os.path.exists(parent):
                os.makedirs(parent, exist_ok=True)
            # Создаём пустой файл
            with open(full_path, 'w', encoding='utf-8') as f:
                pass
            return f'✅ Файл "{path}" успешно создан.'
        else:
            return f'Ошибка: неизвестный тип "{item_type}". Используйте "file" или "directory".'
    except Exception as e:
        return f'Ошибка создания: {e}'


def write_file(path: str, content: str) -> str:
    """Записать текстовое содержимое в файл.
    
    Если файла нет — он будет создан.
    Если файл существует — его содержимое будет полностью перезаписано.
    
    Args:
        path: Относительный путь к файлу.
        content: Текстовое содержимое для записи.
    """
    full_path = _safe_path(path)
    
    try:
        # Создаём родительскую директорию, если её нет
        parent = os.path.dirname(full_path)
        if parent and not os.path.exists(parent):
            os.makedirs(parent, exist_ok=True)
        
        # Проверяем, что это не директория
        if os.path.isdir(full_path):
            return f'Ошибка: "{path}" — это директория, нельзя записать в неё как в файл.'
        
        existed = os.path.exists(full_path)
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Считаем количество записанных символов для отчёта
        char_count = len(content)
        line_count = content.count('\n') + (1 if content and not content.endswith('\n') else 0)
        
        if existed:
            return f'✅ Файл "{path}" перезаписан. Записано {char_count} символов, {line_count} строк.'
        else:
            return f'✅ Файл "{path}" создан. Записано {char_count} символов, {line_count} строк.'
    except Exception as e:
        return f'Ошибка записи в файл: {e}'


# Словарь-диспетчер: имя функции -> её реализация
FUNCTIONS = {
    'read_file': read_file,
    'append_log': append_log,
    'list_files': list_files,
    'create_item': create_item,
    'write_file': write_file,
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
        {
            'type': 'function',
            'function': {
                'name': 'create_item',
                'description': (
                    'Создать новый пустой файл или новую директорию. '
                    'Если объект с таким именем уже существует — вернётся ошибка. '
                    'Родительские директории создаются автоматически.'
                ),
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'path': {
                            'type': 'string',
                            'description': 'Относительный путь к создаваемому объекту. Например: "new_file.txt" или "docs/archive".',
                        },
                        'item_type': {
                            'type': 'string',
                            'enum': ['file', 'directory'],
                            'description': 'Что создать: "file" (файл) или "directory" (директорию). По умолчанию — "file".',
                        },
                    },
                    'required': ['path'],
                },
            },
        },
        {
            'type': 'function',
            'function': {
                'name': 'write_file',
                'description': (
                    'Записать текстовое содержимое в файл. '
                    'Если файла нет — он будет создан. '
                    'Если файл существует — его содержимое будет ПОЛНОСТЬЮ ПЕРЕЗАПИСАНО. '
                    'Родительские директории создаются автоматически.'
                ),
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'path': {
                            'type': 'string',
                            'description': 'Относительный путь к файлу. Например: "notes.txt" или "docs/readme.md".',
                        },
                        'content': {
                            'type': 'string',
                            'description': 'Текстовое содержимое для записи в файл.',
                        },
                    },
                    'required': ['path', 'content'],
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
4. Для записи в новый файл используй write_file (он создаст файл автоматически)
5. Для создания пустого файла или директории используй create_item
6. Будь осторожен с write_file — он ПЕРЕЗАПИСЫВАЕТ существующие файлы без предупреждения
"""
