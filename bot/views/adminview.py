from lib.dbutil import delete, insert
from lib.guild_role import get_role_dict
from discord import Interaction, Role, ButtonStyle, InputTextStyle, Colour, ApplicationCommandError, SelectOption
from discord.ui import Button,  Select, InputText, Modal, button
from views.baseview import BaseView


def get_select_options(roles: list[int], guild_roles: list[Role], guild_id: int):
    options = []
    if len(roles) == 0:
        raise ApplicationCommandError("Role data is zero length")

    guild_role_dict = get_role_dict(guild_roles=guild_roles)
    del_role_list = []
    for r in roles:
        try:
            options.append(
                SelectOption(
                    label=guild_role_dict[r],
                    value=str(r),
                )
            )
        except KeyError:
            del_role_list.append(r)
    if len(del_role_list) != 0:
        del_roles = "".join([str(v) for v in del_role_list])
        delete(table_name="roles",
               where=f"guild_id = {guild_id} AND role_id IN({del_roles})")
    return options


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


class AdminReturnBaseView(BaseView):
    def __init__(self, guild_id):
        super().__init__(guild_id=guild_id)

    @button(label="Main menu", row=3, style=ButtonStyle.grey)
    async def main_menu(self, _: Button, interaction: Interaction):
        await interaction.response.edit_message(content="*Main Menu*", view=AdminMainView(interaction.guild_id))


class AdminMainView(BaseView):
    def __init__(self, lang: dict, guild_id: int):
        super().__init__(guild_id=guild_id, lang=lang)

    @button(label="Addition Role", row=0, style=ButtonStyle.blurple)
    async def add_role(self, _: Button, interaction: Interaction):
        m = AddingRoleModal()
        await interaction.response.send_modal(modal=m)

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
    def __init__(self, lang: dict, guild_id: int, guild_roles: list[Role]):
        super().__init__(guild_id=guild_id, lang=lang)
        self.add_item(
            RemoveRoleSelect.get_instance(
                roles=self.roles,
                guild_roles=guild_roles,
                guild_id=guild_id
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

    def get_instance(roles: list[int], guild_roles: list[Role], guild_id: int):
        options = get_select_options(
            roles=roles, guild_roles=guild_roles, guild_id=guild_id)
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
            content=f"Adding role! <@&{new_role.id}>",
            ephemeral=True
        )
