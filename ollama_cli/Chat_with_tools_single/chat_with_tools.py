# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "ollama",
# ]
# ///

import os
import json
from datetime import datetime
import ollama

MODEL_NAME = 'qwen2.5:1.5b'
LOG_FILE = 'chat.log'

# Запоминаем рабочую директорию при старте
WORKING_DIR = os.getcwd()

# ====== Описание инструментов ======
tools = [
    {
        'type': 'function',
        'function': {
            'name': 'read_file',
            'description': f'Прочитать содержимое текстового файла. Путь указывается ОТНОСИТЕЛЬНО рабочей директории: {WORKING_DIR}. НЕ придумывай пути — используй имя файла как есть, например "notes.txt".',
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
            'description': f'Показать список файлов в рабочей директории ({WORKING_DIR}) или указанной поддиректории. Полезно, чтобы узнать, какие файлы существуют.',
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


# ====== Реализации функций ======
def read_file(path: str) -> str:
    # Защита от абсолютных путей, которые модель может выдумать
    # Нормализуем путь относительно рабочей директории
    if os.path.isabs(path):
        # Если модель дала абсолютный путь, берём только имя файла
        path = os.path.basename(path)
    
    full_path = os.path.join(WORKING_DIR, path)
    
    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        # Подсказываем модели, какие файлы есть рядом
        available = list_files('.')
        return f'Ошибка: файл "{path}" не найден в {WORKING_DIR}.\nДоступные файлы:\n{available}'
    except Exception as e:
        return f'Ошибка чтения файла: {e}'


def append_log(message: str) -> str:
    try:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        line = f'[{timestamp}] {message}\n'
        log_path = os.path.join(WORKING_DIR, LOG_FILE)
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(line)
        return f'Запись успешно добавлена в {LOG_FILE}.'
    except Exception as e:
        return f'Ошибка записи в лог: {e}'


def list_files(directory: str = '.') -> str:
    try:
        full_path = os.path.join(WORKING_DIR, directory)
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


FUNCTIONS = {
    'read_file': read_file,
    'append_log': append_log,
    'list_files': list_files,
}


def execute_tool_call(tool_call) -> str:
    name = tool_call['function']['name']
    args = tool_call['function'].get('arguments', {})
    
    print(f"  🔧 Модель вызывает: {name}({args})")
    
    func = FUNCTIONS.get(name)
    if func is None:
        return f'Неизвестная функция: {name}'
    
    return func(**args)


# ====== Системный промпт с контекстом ======
SYSTEM_PROMPT = f"""Ты помощник с доступом к файлам. 
Текущая рабочая директория: {WORKING_DIR}

ВАЖНЫЕ ПРАВИЛА:
1. Используй ТОЛЬКО относительные пути (например, "notes.txt"), НЕ придумывай абсолютные пути вроде "/path/..."
2. Если не уверен в имени файла — сначала вызови list_files, чтобы посмотреть, какие файлы есть
3. Имена файлов пиши точно так, как их назвал пользователь
"""

messages = [{'role': 'system', 'content': SYSTEM_PROMPT}]

print(f"=== Чат с {MODEL_NAME} запущен ===")
print(f"Рабочая директория: {WORKING_DIR}")
print(f"Доступные инструменты: read_file, append_log, list_files")
print(f"Лог-файл: {os.path.abspath(LOG_FILE)}")
print("Введите 'exit' или 'выход' для завершения.\n")

while True:
    user_input = input("Вы: ").strip()
    
    if user_input.lower() in ['exit', 'quit', 'выход']:
        print("Завершение работы...")
        break
    if not user_input:
        continue
        
    messages.append({'role': 'user', 'content': user_input})
    
    while True:
        try:
            response = ollama.chat(
                model=MODEL_NAME,
                messages=messages,
                tools=tools,
            )
        except Exception as e:
            print(f"\n❌ Ошибка при вызове модели: {e}")
            break
            
        assistant_message = response['message']
        tool_calls = assistant_message.get('tool_calls')
        
        if tool_calls:
            messages.append(assistant_message)
            
            for tool_call in tool_calls:
                result = execute_tool_call(tool_call)
                print(f"  ✅ Результат: {result}")
                
                messages.append({
                    'role': 'tool',
                    'name': tool_call['function']['name'],
                    'content': result,
                })
            continue
        
        ai_response = assistant_message.get('content', '')
        if ai_response:
            print(f"Qwen: {ai_response}\n")
        messages.append(assistant_message)
        break
