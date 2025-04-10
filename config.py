
import discord

# Конфигурация
TOKEN = ""  # Укажите токен бота
OWNER_ID = 1164946920180031498  # Ваш Discord ID
INTENTS = discord.Intents.default()
INTENTS.message_content = True
INTENTS.members = True