from telethon import TelegramClient, events
import asyncio
import time

# ===== ВАШИ ДАННЫЕ =====
api_id = 24700963
api_hash = "07406d99cb6f0fe82282056ff50735d0"
group_id = -1002110119056  # ID вашей группы
target_topic_id = 88  # ID темы
# =========================

# Время последнего ответа бота (глобальное)
last_reply_time = None  # None значит "ответов ещё не было"

client = TelegramClient("session", api_id, api_hash)

def get_topic_id(event):
    """Извлекает ID темы из сообщения"""
    message = event.message
    
    if hasattr(message, 'thread_id') and message.thread_id is not None:
        return message.thread_id
    
    if hasattr(message, 'reply_to') and message.reply_to:
        reply_to = message.reply_to
        
        if hasattr(reply_to, 'forum_topic') and reply_to.forum_topic:
            if hasattr(reply_to, 'reply_to_msg_id') and reply_to.reply_to_msg_id is not None:
                return reply_to.reply_to_msg_id
            
            if hasattr(reply_to, 'reply_to_top_id') and reply_to.reply_to_top_id is not None:
                return reply_to.reply_to_top_id
    
    return None

def can_reply():
    """Проверяет, можно ли ответить (не чаще 1 раза в час)"""
    global last_reply_time
    
    current_time = time.time()
    
    # Если бот ещё не отвечал
    if last_reply_time is None:
        return True
    
    # Проверяем, прошёл ли час (3600 секунд)
    time_passed = current_time - last_reply_time
    if time_passed >= 600:  # 1 час = 3600 секунд
        return True
    else:
        # Сколько осталось до следующего разрешённого ответа
        remaining = int(3600 - time_passed)
        minutes = remaining // 60
        seconds = remaining % 60
        print(f"⏳ Следующий ответ через {minutes} мин {seconds} сек")
        return False

@client.on(events.NewMessage(chats=[group_id]))
async def handler(event):
    global last_reply_time
    
    # Не отвечаем на свои сообщения
    if event.out:
        return
    
    # Получаем ID темы
    message_thread_id = get_topic_id(event)
    
    # Если тема не найдена
    if message_thread_id is None:
        print("⏩ Сообщение не из темы — игнорируем")
        return
    
    # Если target_topic_id не задан — выводим информацию
    if target_topic_id is None:
        print(f"ℹ️ Сообщение из темы с ID: {message_thread_id}")
        print(f"   Текст: {event.message.text[:50]}...")
        print(f"   Чтобы бот отвечал сюда, установите target_topic_id = {message_thread_id}")
        return
    
    # Проверяем, что сообщение из нужной темы
    if message_thread_id != target_topic_id:
        print(f"⏩ Игнорируем (тема {message_thread_id}, нужно {target_topic_id})")
        return
    
    print(f"📩 Получено в теме {target_topic_id}: {event.message.text}")
    
    # Проверяем глобальное ограничение (1 раз в час)
    if not can_reply():
        print("⏩ Пропускаем (глобальное ограничение: 1 ответ в час)")
        return
    
    # ⏳ ЗАДЕРЖКА 2 СЕКУНДЫ ПЕРЕД ОТВЕТОМ
    print("⏳ Ожидание 2 секунды перед ответом...")
    await asyncio.sleep(2)
    
    # Отправляем ответ
    try:
        await event.reply("Беру")
        
        # Запоминаем время ответа
        last_reply_time = time.time()
        
        print("✅ Ответ отправлен")
        print("📊 Следующий ответ будет доступен через 10 минут")
    except Exception as e:
        print(f"❌ Ошибка при отправке: {e}")

async def main():
    print("🔄 Подключаемся к Telegram...")
    await client.start()
    print("✅ Подключено успешно!")
    
    # Проверяем группу
    try:
        entity = await client.get_entity(group_id)
        print(f"📋 Группа: {entity.title}")
        print(f"   Это форум: {getattr(entity, 'forum', False)}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    await client.send_message("me", "Привет! Я работаю!")
    print("📨 Тестовое сообщение отправлено!")
    
    if target_topic_id is None:
        print("\n📌 Как узнать ID темы:")
        print("1. Откройте тему в Telegram")
        print("2. Нажмите на любое сообщение → 'Копировать ссылку'")
        print("3. В ссылке вида t.me/c/1234567890/11/3 второе число — это ID темы")
        print("4. Подставьте его в target_topic_id и перезапустите бота")
    else:
        print(f"🤖 Бот слушает тему с ID: {target_topic_id}")
        print("⏳ Задержка перед ответом: 2 секунды")
        print("⏱️ Глобальное ограничение: 1 ответ в час")
    
    print("Нажмите Ctrl+C для остановки")
    await client.run_until_disconnected()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
