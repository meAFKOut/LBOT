import discord
from discord.ext import commands
from discord import app_commands
from views.staff_application import StaffApplicationView
from utils.time_utils import get_formatted_time

class SetupCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="setup", description="Создать сообщение для подачи заявок")
    async def setup(self, interaction: discord.Interaction):
        """Создаёт сообщение с кнопками для подачи заявок."""
        embed = discord.Embed(
            title="📝 НАБОР В СТАФФ СЕРВЕРА",
            description=(
                "Добро пожаловать в канал для подачи заявок на стафф!\n\n"
                "### Требования для всех должностей:\n"
                "• Возраст: 16+\n"
                "• Наличие микрофона\n"
                "• Активность\n"
                "• Знание правил сервера\n\n"
                "Выберите должность ниже, чтобы подать заявку."
            ),
            color=0x00ff00
        )
        embed.set_footer(text=f"Обновлено {get_formatted_time()}")
        view = StaffApplicationView(self.bot)
        await interaction.channel.send(embed=embed, view=view)
        await interaction.response.send_message("Сообщение для подачи заявок создано!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(SetupCog(bot))