import discord
from discord.ext import commands
import asyncio

from config import TOKEN


# Конфигурация

INTENTS = discord.Intents.default()
INTENTS.message_content = True  # Для чтения содержимого сообщений
INTENTS.members = True  # Для работы с участниками сервера
INTENTS.guilds = True  # Для работы с серверами

# Создание экземпляра бота
bot = commands.Bot(command_prefix="!", intents=INTENTS)

# Событие готовности
@bot.event
async def on_ready():
    """Событие, возникающее, когда бот готов к работе."""
    try:
        # Синхронизация всех слэш-команд
        await bot.tree.sync()
        print(f"Слэш-команды синхронизированы. Бот запущен как {bot.user}.")
    except Exception as e:
        print(f"Ошибка синхронизации слэш-команд: {e}")

# Асинхронная загрузка расширений (Cog'ов)
async def load_extensions():
    """Функция для загрузки всех необходимых Cog'ов."""
    extensions = [
        "cogs.staffpanel",  # Панель управления участниками
        "cogs.setchannel",  # Настройка канала для заявок
        # Добавьте другие Cog'и, если нужно
    ]
    for extension in extensions:
        try:
            await bot.load_extension(extension)
            print(f"Загружен Cog: {extension}")
        except Exception as e:
            print(f"Не удалось загрузить Cog {extension}: {e}")

# Основной запуск бота
async def main():
    """Основной входной метод для запуска бота."""
    async with bot:
        await load_extensions()  # Загрузка всех Cog'ов
        await bot.start(TOKEN)  # Запуск бота

# Точка входа
if __name__ == "__main__":
    asyncio.run(main())
