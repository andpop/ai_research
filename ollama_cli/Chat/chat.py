# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "ollama",
# ]
# ///
import ollama

# Название вашей модели
MODEL_NAME = 'qwen2.5:1.5b'

# Список для хранения истории сообщений
messages = []

print(f"=== Чат с {MODEL_NAME} запущен ===")
print("Введите 'exit' или 'выход' для завершения.\n")

while True:
    # 1. Получаем ввод от пользователя
    user_input = input("Вы: ")
    
    # 2. Проверяем команду выхода
    if user_input.lower() in ['exit', 'quit', 'выход']:
        print("Завершение работы...")
        break
        
    # 3. Добавляем сообщение пользователя в историю
    messages.append({'role': 'user', 'content': user_input})
    
    # 4. Отправляем запрос к локальному Ollama
    response = ollama.chat(model=MODEL_NAME, messages=messages)
    
    # 5. Извлекаем и печатаем ответ
    ai_response = response['message']['content']
    print(f"Qwen: {ai_response}\n")
    
    # 6. Добавляем ответ модели в историю, чтобы она помнила контекст
    messages.append({'role': 'assistant', 'content': ai_response})
