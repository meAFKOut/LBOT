import discord

# ID ролей для каждой должности
ROLE_IDS = {
    "Support": [1358082179581870141, 1358087527096913980],
    "Moderator": [1358087527096913980, 1358081072809906217],
    "Eventer": [1358087527096913980, 1358082214004396102],
}

class StaffApplicationView(discord.ui.View):
    def __init__(self, applicant_id=None, category=None):
        """
        View для взаимодействия с заявками. 
        Если applicant_id и category не переданы, View используется для кнопок выбора заявок.
        """
        super().__init__(timeout=None)
        if applicant_id and category:
            self.add_item(AcceptButton(applicant_id, category))
            self.add_item(RejectButton(applicant_id, category))
        else:
            self.add_item(CategorySelect())

class CategorySelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Moderator", description="Подать заявку на модератора", emoji="🛡️"),
            discord.SelectOption(label="Support", description="Подать заявку на саппорта", emoji="🛟"),
            discord.SelectOption(label="Eventer", description="Подать заявку на ивентера", emoji="🎮")
        ]
        super().__init__(placeholder="Выберите должность", options=options, custom_id="category_select")

    async def callback(self, interaction: discord.Interaction):
        modal = ApplicationModal(self.values[0])  # Передаём категорию в модальное окно
        await interaction.response.send_modal(modal)

class ApplicationModal(discord.ui.Modal):
    def __init__(self, category):
        """Модальное окно для заполнения заявки."""
        super().__init__(title=f"Заявка на {category}")
        self.category = category
        self.add_item(discord.ui.TextInput(label="Ваш возраст", placeholder="Введите ваш возраст", required=True))
        self.add_item(discord.ui.TextInput(label="Ваш опыт", placeholder="Опишите ваш опыт", required=True))

    async def on_submit(self, interaction: discord.Interaction):
        """Обработка отправки заявки."""
        # Получаем канал для заявок
        set_channel_cog = interaction.client.get_cog("SetChannelCog")
        if not set_channel_cog:
            await interaction.response.send_message("⚠️ Канал для заявок не настроен!", ephemeral=True)
            return

        applications_channel = set_channel_cog.get_applications_channel(interaction.guild)
        if not applications_channel:
            await interaction.response.send_message("⚠️ Канал для заявок не настроен! Обратитесь к администратору.", ephemeral=True)
            return

        # Создаём embed с заявкой
        embed = discord.Embed(
            title=f"Новая заявка на {self.category}",
            description=f"От: {interaction.user.mention} ({interaction.user.id})",
            color=0x00ff00
        )
        embed.add_field(name="Возраст", value=self.children[0].value, inline=False)
        embed.add_field(name="Опыт", value=self.children[1].value, inline=False)
        embed.set_footer(text="Используйте кнопки ниже для обработки заявки")

        # Добавляем кнопки для принятия/отклонения
        view = StaffApplicationView(applicant_id=interaction.user.id, category=self.category)
        await applications_channel.send(embed=embed, view=view)
        await interaction.response.send_message("✅ Ваша заявка успешно отправлена!", ephemeral=True)

class AcceptButton(discord.ui.Button):
    def __init__(self, applicant_id, category):
        super().__init__(label="Принять", style=discord.ButtonStyle.success, emoji="✅", custom_id=f"accept_{applicant_id}_{category}")
        self.applicant_id = applicant_id
        self.category = category

    async def callback(self, interaction: discord.Interaction):
        """Принять заявку."""
        guild = interaction.guild
        member = guild.get_member(self.applicant_id)

        if not member:
            await interaction.response.send_message("⚠️ Пользователь не найден.", ephemeral=True)
            return

        roles = [guild.get_role(role_id) for role_id in ROLE_IDS[self.category] if guild.get_role(role_id)]
        await member.add_roles(*roles)
        embed = discord.Embed(
    title="✅ Заявка Принята",
    description=f"Ваша заявка на позицию **{self.category}** была принята.",
    color=discord.Color.green()  # Красный цвет для обозначения ошибки/отклонения
        )

        await member.send(embed=embed)
        await interaction.response.send_message(f"✅ Пользователь {member.mention} принят.", ephemeral=True)

class RejectButton(discord.ui.Button):
    def __init__(self, applicant_id, category):
        super().__init__(label="Отклонить", style=discord.ButtonStyle.danger, emoji="❌", custom_id=f"reject_{applicant_id}_{category}")
        self.applicant_id = applicant_id
        self.category = category

    async def callback(self, interaction: discord.Interaction):
        """Отклонить заявку."""
        guild = interaction.guild
        member = guild.get_member(self.applicant_id)

        if not member:
            await interaction.response.send_message("⚠️ Пользователь не найден.", ephemeral=True)
            return

        embed = discord.Embed(
    title="❌ Заявка отклонена",
    description=f"Ваша заявка на позицию **{self.category}** была отклонена.",
    color=discord.Color.red()  # Красный цвет для обозначения ошибки/отклонения
    )

        await member.send(embed=embed)
        await interaction.response.send_message(f"❌ Заявка пользователя {member.mention} отклонена.", ephemeral=True)