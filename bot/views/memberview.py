from discord import Interaction, Role, ButtonStyle, Colour, ApplicationCommandError, Embed, EmbedField, SelectOption
from discord.ui import Button,  Select,  button
from views.baseview import BaseView
from lib.guild_role import get_role_dict
from lib.dbutil import delete


def get_select_options(roles: list[int], member_roles: list[Role], guild_roles: list[Role], guild_id: int):
    options = []
    if len(roles) == 0:
        raise ApplicationCommandError("Role data is zero length")
    member_role_ids = [v.id for v in member_roles]
    guild_role_dict = get_role_dict(guild_roles=guild_roles)
    del_role_list = []
    for r in roles:
        try:
            if r in member_role_ids:
                label = guild_role_dict[r]
                value = str(r)
                emoji = "🟢"
            else:
                label = guild_role_dict[r]
                value = str(-r)
                emoji = "🔴"
            options.append(
                SelectOption(
                    emoji=emoji,
                    label=label,
                    value=value,
                )
            )
        except KeyError:
            del_role_list.append(r)
    if len(del_role_list) != 0:
        del_roles = "".join([str(v) for v in del_role_list])
        delete(table_name="roles",
               where=f"guild_id = {guild_id} AND role_id IN({del_roles})")
    return options


class BaseEmbed(Embed):
    def __init__(self, name: str, icon_url: str, title: str, color: Colour):
        super().__init__(colour=color, title=title)
        self.set_author(name=name, icon_url=icon_url)
        self.set_footer(
            icon_url="https://avatars.githubusercontent.com/u/66500373?s=50",
            text="Made by nikawamikan"
        )


class RoleListEmbed(BaseEmbed):
    def __init__(self, name: str, icon_url: str, roles: list[int], member_roles: list[Role], guild_roles: list[Role], guild_id: int):
        super().__init__(name, icon_url, color=Colour.brand_green(),
                         title="The Role that belongs to you")
        self._set_embed_fields(
            member_roles=member_roles,
            roles=roles,
            guild_roles=guild_roles,
            guild_id=guild_id
        )

    def _set_embed_fields(self, roles: list[int], member_roles: list[Role], guild_roles: list[Role], guild_id: int):
        guild_role_dict = get_role_dict(guild_roles=guild_roles)
        del_role_list = []
        for r in roles:
            try:
                n = [v for v in member_roles if v.id == r]
                if len(n) != 0:
                    self.append_field(EmbedField(
                        name=f":white_check_mark: {guild_role_dict[r]}", value="enable", inline=False))
                else:
                    self.append_field(EmbedField(
                        name=f":octagonal_sign: {guild_role_dict[r]}", value="disable", inline=False))
            except KeyError:
                del_role_list.append(r)
        if len(del_role_list) != 0:
            del_roles = "".join([str(v) for v in del_role_list])
            delete(table_name="roles",
                   where=f"guild_id = {guild_id} AND role_id IN({del_roles})")


class MemberReturnBaseView(BaseView):
    def __init__(self, guild_id):
        super().__init__(guild_id=guild_id)

    @button(label="Main menu", row=3, style=ButtonStyle.grey)
    async def main_menu(self, _: Button, interaction: Interaction):
        v = MemberMainView(
            guild_id=str(interaction.guild_id),
        )
        embed = RoleListEmbed(
            name=interaction.user.name,
            icon_url=interaction.user.avatar.url,
            roles=v.roles,
            member_roles=interaction.user.roles,
            guild_roles=interaction.guild.roles,
            guild_id=interaction.guild_id
        )
        await interaction.response.edit_message(content="**Main menu**", view=MemberMainView(interaction.guild_id), embed=embed)


class MemberMainView(BaseView):
    def __init__(self, guild_id):
        super().__init__(guild_id=guild_id)

    @button(label="Edit role", row=0, style=ButtonStyle.green)
    async def edit_role(self, _: Button, interaction: Interaction):
        v = EditRoleView(guild_id=interaction.guild_id,
                         guild_roles=interaction.guild.roles,
                         member_roles=interaction.user.roles
                         )
        await interaction.response.edit_message(content="**Edit Menu**", view=v, embed=None)


class EditRoleSelect(Select["EditRoleView"]):
    async def callback(self, interaction: Interaction):
        edit_role_id = int(self.values[0])
        role = interaction.guild.get_role(abs(edit_role_id))
        if edit_role_id > 0:
            await interaction.user.remove_roles(role)
        else:
            await interaction.user.add_roles(role)
        view = EditRoleView(
            guild_id=interaction.guild_id,
            guild_roles=interaction.guild.roles,
            member_roles=interaction.user.roles
        )
        await interaction.response.edit_message(content="Success !", view=view)

    def get_instance(roles: list[int], guild_roles: list[Role], guild_id: int, member_roles: list[Role]):
        options = get_select_options(
            roles=roles, guild_roles=guild_roles, guild_id=guild_id, member_roles=member_roles)
        return EditRoleSelect(placeholder="Select Role", options=options)


class EditRoleView(MemberReturnBaseView):
    def __init__(self, guild_id: int, guild_roles: list[Role], member_roles: list[Role]):
        super().__init__(guild_id=guild_id)
        self.add_item(
            EditRoleSelect.get_instance(
                roles=self.roles,
                guild_roles=guild_roles,
                guild_id=guild_id,
                member_roles=member_roles
            )
        )
