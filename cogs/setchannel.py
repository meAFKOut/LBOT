import discord
from discord.ext import commands
from discord import app_commands
import json
import os

APPLICATIONS_FILE = "applications.json"

def save_applications_channel(channel_id):
    """Сохраняет ID канала заявок в файл."""
    data = {"applications_channel_id": channel_id}
    with open(APPLICATIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_applications_channel():
    """Загружает ID канала заявок из файла."""
    if os.path.exists(APPLICATIONS_FILE):
        with open(APPLICATIONS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("applications_channel_id", 0)
    return 0

class SetChannelCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.applications_channel_id = load_applications_channel()  # Загружаем ID канала при запуске

    @app_commands.command(name="setchannel", description="Настроить канал для заявок")
    async def setchannel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        """Настраивает текстовый канал для заявок."""
        self.applications_channel_id = channel.id
        save_applications_channel(channel.id)  # Сохраняем ID канала в файл
        embed = discord.Embed(
            title="✅ Канал настроен",
            description=f"Канал для заявок установлен: {channel.mention}",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)

    def get_applications_channel(self, guild):
        """Получает объект канала заявок."""
        return guild.get_channel(self.applications_channel_id)

async def setup(bot):
    await bot.add_cog(SetChannelCog(bot))