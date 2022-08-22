from lib.dbutil import create_talbe, primary_key, delete, insert
from discord import Interaction, Role, ButtonStyle, InputTextStyle, Colour, ApplicationCommandError
from discord.ui import Button, View, Select, InputText, Modal, button
from views.modelutil import get_roles, get_select_options


# DataBaseがそもそも動いてなかったらここで止まると思われる
create_talbe(
    table_name="roles",
    columns=[
        "guild_id bigint",
        "role_id bigint",
        "INDEX guids_index(guild_id)",
        primary_key(["guild_id", "role_id"])
    ])


def delete_role(guild_id: int, role_id: int):
    delete(
        table_name="roles",
        where=f"guild_id = {guild_id} AND role_id = {role_id}"
    )


def insert_role(guild_id: int, role_id: int):
    insert(
        table_name="roles",
        values=[[str(guild_id), str(role_id)]]
    )


class AdminBaseView(View):
    def __init__(self, guild_id):
        super().__init__(timeout=180)
        self.roles = get_roles(guild_id=guild_id)

    @button(label="Exit", row=4, style=ButtonStyle.red)
    async def exit_menu(self, _: Button, interaction: Interaction):
        await interaction.response.edit_message(content="Bye", view=None)


class AdminReturnBaseView(AdminBaseView):
    def __init__(self, guild_id):
        super().__init__(guild_id=guild_id)

    @button(label="Main menu", row=3, style=ButtonStyle.grey)
    async def main_menu(self, _: Button, interaction: Interaction):
        await interaction.response.edit_message(content="*Main Menu*", view=AdminMainView(interaction.guild_id))


class AdminMainView(AdminBaseView):
    def __init__(self, guild_id):
        super().__init__(guild_id=guild_id)

    @button(label="Addition Role", row=0, style=ButtonStyle.blurple)
    async def add_role(self, _: Button, interaction: Interaction):
        m = AddingRoleModal()
        await interaction.response.send_modal(modal=m)
        await interaction.edit_original_message(content="Send modal", view=None)

    @button(label="Remove Role", row=1, style=ButtonStyle.blurple)
    async def remove_role(self, _: Button, interaction: Interaction):
        try:
            v = RemoveRoleView(
                guild_id=interaction.guild_id,
                guild_roles=interaction.guild.roles,
            )
        except ApplicationCommandError as e:
            await interaction.response.edit_message(content=f"**Error!!**\n*{e}*")
        await interaction.response.edit_message(content="*Remove Menu*", view=v)


class RemoveRoleView(AdminReturnBaseView):
    def __init__(self, guild_id, guild_roles):
        super().__init__(guild_id=guild_id)
        self.add_item(
            RemoveRoleSelect.get_instance(
                roles=self.roles,
                guild_roles=guild_roles,
            )
        )


class RemoveRoleSelect(Select["RemoveRoleView"]):
    async def callback(self, interaction: Interaction):
        remove_role_id = int(self.values[0])
        target_role = interaction.guild.get_role(remove_role_id)
        role_name = target_role.name
        await target_role.delete()
        delete_role(guild_id=interaction.guild_id, role_id=remove_role_id)
        v = AdminMainView(guild_id=interaction.guild_id)
        await interaction.response.edit_message(content=f"Removed the Role: **{role_name}**", view=v)

    def get_instance(roles: list[int], guild_roles: list[Role]):
        options = get_select_options(roles=roles, guild_roles=guild_roles)
        return RemoveRoleSelect(placeholder="Select Role to Remove", options=options)


class AddingRoleModal(Modal):
    def __init__(self):
        super().__init__(title="Adding Role")
        self.add_item(
            InputText(
                style=InputTextStyle.short,
                label="Role name",
                placeholder="Input Role name",
                min_length=1,
                max_length=30,
                required=True,
            )
        )
        self.add_item(
            InputText(
                style=InputTextStyle.short,
                label="Role Color",
                placeholder="ff0101",
                min_length=6,
                max_length=6,
                required=False,
            )
        )

    async def callback(self, interaction: Interaction):
        role_name = self.children[0].value
        role_color = Colour.random()
        if len(self.children[1].value) != 0:
            role_color = int(f"0x{self.children[1].value}", 16)
        new_role = await interaction.guild.create_role(name=role_name, color=role_color)
        insert_role(interaction.guild_id, new_role.id)
        await interaction.response.send_message(
            content=f"Adding role! **{new_role.name}**\n*Main Menu*",
            view=AdminMainView(interaction.guild_id),
            ephemeral=True
        )
