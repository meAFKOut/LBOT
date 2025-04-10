import discord
from discord.ext import commands
from discord import app_commands
from utils.file_utils import load_data, save_data
from datetime import datetime, timedelta

# IDs for roles and report channel
STAFF_ROLE_ID = 1358087527096913980
MUTE_ROLE_ID = 1358864989020094717
REPORT_CHANNEL_ID = 1359753956481564682

# Load punishment data from JSON file
punishments_data = load_data("punishments_data.json")

def parse_duration(duration_str: str):
    """Parse a duration string (e.g., '1d', '1month', '1min') into timedelta."""
    duration_str = duration_str.lower()
    if duration_str.endswith("d"):
        return timedelta(days=int(duration_str[:-1]))
    elif duration_str.endswith("month"):
        return timedelta(days=int(duration_str[:-5]) * 30)
    elif duration_str.endswith("min"):
        return timedelta(minutes=int(duration_str[:-3]))
    else:
        raise ValueError("Invalid time format. Use '1d', '1month', '1min'.")

class PunishmentModal(discord.ui.Modal):
    def __init__(self, user: discord.Member, action: str):
        super().__init__(title=f"{action.capitalize()} пользователя")
        self.user = user
        self.action = action
        self.add_item(discord.ui.TextInput(label="Причина", placeholder="Укажите причину", required=True))
        self.add_item(discord.ui.TextInput(label="Время", placeholder="Например: 1д, 1мес, 1мин", required=True))

    async def on_submit(self, interaction: discord.Interaction):
        """Обработчик отправки модального окна"""
        try:
            reason = self.children[0].value
            duration_str = self.children[1].value
            duration = parse_duration(duration_str)
            end_time = datetime.utcnow() + duration

            # Отправка отчёта в канал
            report_channel = interaction.guild.get_channel(REPORT_CHANNEL_ID)
            if not report_channel:
                await interaction.response.send_message(embed=self.create_embed("⚠️ Ошибка", "Канал для отчётов не найден.", discord.Color.orange()), ephemeral=True)
                return

            if self.action == "мут":
                # Выдать мут
                mute_role = interaction.guild.get_role(MUTE_ROLE_ID)
                if mute_role not in self.user.roles:
                    await self.user.add_roles(mute_role, reason=f"{reason} (по решению {interaction.user})")
                    await report_channel.send(embed=self.create_embed(
                        "🔇 Мут выдан",
                        f"**Пользователь:** {self.user.mention}\n**Время:** {duration_str}\n**Причина:** {reason}\n**Выдал:** {interaction.user.mention}",
                        discord.Color.red()
                    ))
                    punishments_data.setdefault(self.user.id, {"mutes": 0, "warns": 0, "bans": 0})
                    punishments_data[self.user.id]["mutes"] += 1
                    await interaction.response.send_message(embed=self.create_embed(
                        "✅ Успех",
                        f"Пользователю {self.user.mention} был выдан мут на {duration_str}. Причина: {reason}.",
                        discord.Color.green()
                    ), ephemeral=True)
                else:
                    await interaction.response.send_message(embed=self.create_embed(
                        "⚠️ Ошибка",
                        f"Пользователь {self.user.mention} уже имеет мут.",
                        discord.Color.orange()
                    ), ephemeral=True)

            elif self.action == "предупреждение":
                # Добавить предупреждение
                punishments_data.setdefault(self.user.id, {"mutes": 0, "warns": 0, "bans": 0})
                punishments_data[self.user.id]["warns"] += 1

                await report_channel.send(embed=self.create_embed(
                    "⚠️ Предупреждение выдано",
                    f"**Пользователь:** {self.user.mention}\n**Время:** {duration_str}\n**Причина:** {reason}\n**Выдал:** {interaction.user.mention}",
                    discord.Color.gold()
                ))
                await interaction.response.send_message(embed=self.create_embed(
                    "✅ Успех",
                    f"Пользователю {self.user.mention} было выдано предупреждение. Причина: {reason}.",
                    discord.Color.green()
                ), ephemeral=True)

        except ValueError:
            await interaction.response.send_message(embed=self.create_embed(
                "❌ Ошибка",
                "Укажите корректное время (например: '1д', '1мес', '1мин').",
                discord.Color.red()
            ), ephemeral=True)

    def create_embed(self, title, description, color):
        """Создаёт Embed для сообщений."""
        embed = discord.Embed(title=title, description=description, color=color)
        embed.set_footer(text="Система управления наказаниями", icon_url="https://cdn-icons-png.flaticon.com/512/1827/1827504.png")
        embed.timestamp = datetime.utcnow()
        return embed


class StaffPanelView(discord.ui.View):
    def __init__(self, member: discord.Member, author: discord.Member):
        super().__init__(timeout=None)
        self.member = member
        self.author = author
        self.add_item(MuteButton(member))
        self.add_item(WarnButton(member))
        self.add_item(RemoveMuteButton(member))
        self.add_item(RemoveWarnButton(member))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Проверка, что только автор команды может использовать кнопки"""
        if interaction.user != self.author:
            await interaction.response.send_message(embed=self.create_embed(
                "❌ Доступ запрещён",
                "Вы не можете использовать эту панель.",
                discord.Color.red()
            ), ephemeral=True)
            return False
        return True

    def create_embed(self, title, description, color):
        """Создаёт Embed для сообщений."""
        embed = discord.Embed(title=title, description=description, color=color)
        embed.set_footer(text="Система управления наказаниями", icon_url="https://cdn-icons-png.flaticon.com/512/1827/1827504.png")
        embed.timestamp = datetime.utcnow()
        return embed


class MuteButton(discord.ui.Button):
    def __init__(self, member: discord.Member):
        super().__init__(label="Выдать мут", style=discord.ButtonStyle.secondary, emoji="🔇")
        self.member = member

    async def callback(self, interaction: discord.Interaction):
        modal = PunishmentModal(self.member, action="мут")
        await interaction.response.send_modal(modal)


class WarnButton(discord.ui.Button):
    def __init__(self, member: discord.Member):
        super().__init__(label="Дать предупреждение", style=discord.ButtonStyle.primary, emoji="⚠️")
        self.member = member

    async def callback(self, interaction: discord.Interaction):
        modal = PunishmentModal(self.member, action="предупреждение")
        await interaction.response.send_modal(modal)


class RemoveMuteButton(discord.ui.Button):
    def __init__(self, member: discord.Member):
        super().__init__(label="Снять мут", style=discord.ButtonStyle.success, emoji="✅")
        self.member = member

    async def callback(self, interaction: discord.Interaction):
        # Получаем роль мута и канал для отчётов
        mute_role = interaction.guild.get_role(MUTE_ROLE_ID)
        report_channel = interaction.guild.get_channel(REPORT_CHANNEL_ID)

        # Проверяем, есть ли у пользователя роль мута
        if mute_role and mute_role in self.member.roles:
            # Снимаем роль мута
            await self.member.remove_roles(mute_role, reason=f"Снятие мута по решению {interaction.user}")
            
            # Отправляем отчёт в канал
            if report_channel:
                await report_channel.send(embed=self.create_embed(
                    "✅ Мут снят",
                    f"**Пользователь:** {self.member.mention}\n**Снял:** {interaction.user.mention}",
                    discord.Color.green()
                ))
            
            # Отправляем сообщение об успешном снятии мута
            await interaction.response.send_message(embed=self.create_embed(
                "✅ Успех",
                f"Мут с пользователя {self.member.mention} снят.",
                discord.Color.green()
            ), ephemeral=True)
        else:
            # Если роли мута нет, отправляем сообщение об ошибке
            await interaction.response.send_message(embed=self.create_embed(
                "⚠️ Ошибка",
                f"У пользователя {self.member.mention} нет роли мута.",
                discord.Color.orange()
            ), ephemeral=True)

    def create_embed(self, title, description, color):
        """Создаёт Embed для сообщений."""
        embed = discord.Embed(title=title, description=description, color=color)
        embed.set_footer(text="Система управления наказаниями", icon_url="https://cdn-icons-png.flaticon.com/512/1827/1827504.png")
        embed.timestamp = datetime.utcnow()
        return embed

class RemoveWarnButton(discord.ui.Button):
    def __init__(self, member: discord.Member):
        super().__init__(label="Удалить предупреждение", style=discord.ButtonStyle.danger, emoji="❌")
        self.member = member

    async def callback(self, interaction: discord.Interaction):
        report_channel = interaction.guild.get_channel(REPORT_CHANNEL_ID)

        if punishments_data.get(self.member.id, {}).get("warns", 0) > 0:
            punishments_data[self.member.id]["warns"] -= 1
            await report_channel.send(embed=self.create_embed(
                "❌ Предупреждение снято",
                f"**Пользователь:** {self.member.mention}\n**Снял:** {interaction.user.mention}",
                discord.Color.green()
            ))
            await interaction.response.send_message(embed=self.create_embed(
                "✅ Успех",
                f"Одно предупреждение пользователя {self.member.mention} было удалено.",
                discord.Color.green()
            ), ephemeral=True)
        else:
            await interaction.response.send_message(embed=self.create_embed(
                "⚠️ Ошибка",
                f"У пользователя {self.member.mention} нет активных предупреждений.",
                discord.Color.orange()
            ), ephemeral=True)

    def create_embed(self, title, description, color):
        """Создаёт Embed для сообщений."""
        embed = discord.Embed(title=title, description=description, color=color)
        embed.set_footer(text="Система управления наказаниями", icon_url="https://cdn-icons-png.flaticon.com/512/1827/1827504.png")
        embed.timestamp = datetime.utcnow()
        return embed


class StaffPanelCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="staffpanel", description="Панель управления участником.")
    @app_commands.describe(member="Выберите участника для управления.")
    async def staffpanel(self, interaction: discord.Interaction, member: discord.Member):
        """Команда для вызова панели управления участником."""
        # Проверяем роль пользователя
        if STAFF_ROLE_ID not in [role.id for role in interaction.user.roles]:
            await interaction.response.send_message(embed=self.create_embed(
                "❌ Доступ запрещён",
                "У вас нет доступа к этой команде.",
                discord.Color.red()
            ), ephemeral=True)
            return

        # Создаём Embed с информацией об участнике
        user_punishments = punishments_data.get(member.id, {"mutes": 0, "warns": 0, "bans": 0})
        embed = discord.Embed(
            title="Staff Panel",
            description=f"Управление для пользователя: {member.mention}",
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
        embed.add_field(name="ID Участника", value=member.id, inline=True)
        embed.add_field(name="Имя", value=member.name, inline=True)
        embed.add_field(
            name="Дата присоединения",
            value=member.joined_at.strftime("%Y-%m-%d") if member.joined_at else "Неизвестно",
            inline=True
        )
        embed.add_field(name="История наказаний", value=(
            f"Мутов: {user_punishments['mutes']}\n"
            f"Предупреждений: {user_punishments['warns']}\n"
            f"Банов: {user_punishments['bans']}"
        ), inline=False)

        # Отправляем Embed с кнопками
        view = StaffPanelView(member, interaction.user)
        await interaction.response.send_message(embed=embed, view=view)

    def create_embed(self, title, description, color):
        """Создаёт Embed для сообщений."""
        embed = discord.Embed(title=title, description=description, color=color)
        embed.set_footer(text="Система управления наказаниями", icon_url="https://cdn-icons-png.flaticon.com/512/1827/1827504.png")
        embed.timestamp = datetime.utcnow()
        return embed


async def setup(bot):
    await bot.add_cog(StaffPanelCog(bot))