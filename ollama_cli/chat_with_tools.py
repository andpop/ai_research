# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "ollama",
# ]
# ///

import os
import ollama
import tools

MODEL_NAME = 'qwen2.5:1.5b'


def execute_tool_call(tool_call) -> str:
    """Выполняет вызов инструмента и возвращает результат."""
    name = tool_call['function']['name']
    args = tool_call['function'].get('arguments', {})
    
    print(f"  🔧 Модель вызывает: {name}({args})")
    
    func = tools.FUNCTIONS.get(name)
    if func is None:
        return f'Неизвестная функция: {name}'
    
    return func(**args)


def main():
    # Инициализируем модуль инструментов
    working_dir = os.getcwd()
    tools.init_tools(working_dir)
    
    # Получаем описания и промпт
    tool_definitions = tools.get_tool_definitions()
    system_prompt = tools.get_system_prompt()
    
    messages = [{'role': 'system', 'content': system_prompt}]
    
    print(f"=== Чат с {MODEL_NAME} запущен ===")
    print(f"Рабочая директория: {working_dir}")
    print(f"Загружено инструментов: {len(tool_definitions)}")
    print(f"Лог-файл: {os.path.abspath(tools.LOG_FILE)}")
    print("Введите 'exit' или 'выход' для завершения.\n")
    
    while True:
        user_input = input("Вы: ").strip()
        
        if user_input.lower() in ['exit', 'quit', 'выход']:
            print("Завершение работы...")
            break
        if not user_input:
            continue
            
        messages.append({'role': 'user', 'content': user_input})
        
        # Внутренний цикл: модель может вызвать несколько инструментов подряд
        while True:
            try:
                response = ollama.chat(
                    model=MODEL_NAME,
                    messages=messages,
                    tools=tool_definitions,
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


if __name__ == '__main__':
    main()
