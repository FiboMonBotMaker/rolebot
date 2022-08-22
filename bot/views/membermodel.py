from discord import SelectOption, Interaction, Role, ButtonStyle, InputTextStyle
from discord.ui import Button, View, Select, InputText, button
from views.modelutil import get_roles, get_select_options


class MemberView(View):
    def __init__(self, guild_id):
        super().__init__(timeout=180)
        self.roles = get_roles(guild_id=guild_id)


class MemberMainView(MemberView):
    def __init__(self, guild_id):
        super().__init__(guild_id=guild_id)

    @button(label="addition_role", row=0, style=ButtonStyle.green)
    async def add_role(self, _: Button, interaction: Interaction):
        v = AddingRoleView(guild_id=interaction.guild_id)
        await interaction.response.edit_message(content="*Adding Menu*", view=v)

    @button(label="remove_role", row=0, style=ButtonStyle.green)
    async def remove_role(self, _: Button, interaction: Interaction):
        v = RemoveRoleView(
            guild_id=interaction.guild_id,
            guild_roles=interaction.guild.roles,
        )
        await interaction.response.edit_message(content="*Remove Menu*", view=v)


class RemoveRoleView(MemberView):
    def __init__(self, guild_id, guild_roles):
        super().__init__(guild_id=guild_id)
        self.add_item(
            RemoveRoleSelect.get_instance(
                roles=self.roles,
                guild_roles=guild_roles,
            )
        )


class RemoveRoleSelect(Select["MemberView"]):
    async def callback(self, interaction: Interaction):
        remove_role_id = self.values[0]
        await interaction.response.edit_message(content="test", view=None)

    def get_instance(roles: list[int], guild_roles: list[Role]):
        options = get_select_options(roles=roles, guild_roles=guild_roles)
        return RemoveRoleSelect(placeholder="Select Role to Remove", options=options)


class AddingRoleView(MemberView):
    def __init__(self, guild_id):
        super().__init__(guild_id=guild_id)
