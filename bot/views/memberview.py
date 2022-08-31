from discord import Interaction, Role, ButtonStyle, Colour, ApplicationCommandError, Embed, EmbedField, SelectOption, Color, errors
from discord.ui import Button,  Select
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
        del_roles = ",".join([str(v) for v in del_role_list])
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
    def __init__(self, lang: dict, name: str, icon_url: str, roles: list[int], member_roles: list[Role], guild_roles: list[Role], guild_id: int):
        super().__init__(
            name=name,
            icon_url=icon_url,
            color=Colour.brand_green(),
            title=lang["member"]["embed"]["title"])
        self._set_embed_fields(
            lang=lang["member"]["embed"],
            member_roles=member_roles,
            roles=roles,
            guild_roles=guild_roles,
            guild_id=guild_id
        )

    def _set_embed_fields(self, lang: dict, roles: list[int], member_roles: list[Role], guild_roles: list[Role], guild_id: int):
        guild_role_dict = get_role_dict(guild_roles=guild_roles)
        del_role_list = []
        for r in roles:
            try:
                n = [v for v in member_roles if v.id == r]
                if len(n) != 0:
                    self.append_field(EmbedField(
                        name=f":white_check_mark: {guild_role_dict[r]}", value=lang["field"]["enable"], inline=False))
                else:
                    self.append_field(EmbedField(
                        name=f":octagonal_sign: {guild_role_dict[r]}", value=lang["field"]["disable"], inline=False))
            except KeyError:
                del_role_list.append(r)
        if len(del_role_list) != 0:
            del_roles = ",".join([str(v) for v in del_role_list])
            delete(table_name="roles",
                   where=f"guild_id = {guild_id} AND role_id IN({del_roles})")


class MemberReturnBaseView(BaseView):
    def __init__(self, lang: dict, guild_id: int):
        super().__init__(guild_id=guild_id, lang=lang)
        self.add_item(self.MainMenuButton(lang=lang))

    class MainMenuButton(Button):
        def __init__(self, lang):
            self.lang = lang
            super().__init__(
                style=ButtonStyle.green,
                label=self.lang["member"]["base"]["button"],
                row=3
            )

        async def callback(self, interaction: Interaction):
            view = MemberMainView(
                lang=self.lang,
                guild_id=interaction.guild_id,
            )
            embed = RoleListEmbed(
                lang=self.lang,
                name=interaction.user.name,
                icon_url=interaction.user.avatar.url if interaction.user.avatar != None else "",
                roles=view.roles,
                member_roles=interaction.user.roles,
                guild_roles=interaction.guild.roles,
                guild_id=interaction.guild_id
            )
            await interaction.response.edit_message(view=view, embed=embed)


class MemberMainView(BaseView):
    def __init__(self, lang: dict, guild_id: int):
        super().__init__(guild_id=guild_id, lang=lang)
        self.add_item(self.MainMenuButton(lang=lang))

    class MainMenuButton(Button):
        def __init__(self, lang):
            self.lang = lang
            super().__init__(
                style=ButtonStyle.blurple,
                label=self.lang["member"]["main"]["button"],
                row=3
            )

        async def callback(self, interaction: Interaction):
            try:
                view = EditRoleView(
                    lang=self.lang,
                    guild_id=interaction.guild_id,
                    guild_roles=interaction.guild.roles,
                    member_roles=interaction.user.roles
                )
                await interaction.response.edit_message(
                    embed=Embed(
                        color=Color.orange(),
                        title=self.lang["member"]["edit"]["title"]
                    ),
                    view=view
                )
            except ApplicationCommandError:
                await interaction.response.edit_message(
                    embed=None,
                    view=None,
                    content=self.lang["error"]["zerolength"]
                )


class EditRoleSelect(Select):
    def __init__(self, lang: dict, placeholder: str, options: list[SelectOption]):
        self.lang = lang
        super().__init__(placeholder=placeholder, options=options)

    async def callback(self, interaction: Interaction):
        try:
            edit_role_id = int(self.values[0])
            role = interaction.guild.get_role(abs(edit_role_id))
            userroles = interaction.user.roles
            message = None
            if edit_role_id > 0:
                await interaction.user.remove_roles(role)
                userroles = [v for v in filter(lambda v: v != role, userroles)]
                message: str = self.lang["member"]["edit"]["select"]["disable"]
            else:
                await interaction.user.add_roles(role)
                userroles.append(role)
                message: str = self.lang["member"]["edit"]["select"]["enable"]
            view = EditRoleView(
                lang=self.lang,
                guild_id=interaction.guild_id,
                guild_roles=interaction.guild.roles,
                member_roles=userroles
            )
            await interaction.response.edit_message(embed=Embed(color=Color.green(), title=message.format(role.name)), view=view)
        except errors.Forbidden:
            await interaction.response.edit_message(embed=None, view=None, content=self.lang["error"]["permisson"])

    def get_instance(lang: dict, roles: list[int], guild_roles: list[Role], guild_id: int, member_roles: list[Role]):
        options = get_select_options(
            roles=roles, guild_roles=guild_roles, guild_id=guild_id, member_roles=member_roles)
        return EditRoleSelect(lang=lang, placeholder=lang["member"]["edit"]["select"]["placeholder"], options=options)


class EditRoleView(MemberReturnBaseView):
    def __init__(self, lang: dict, guild_id: int, guild_roles: list[Role], member_roles: list[Role]):
        super().__init__(guild_id=guild_id, lang=lang)
        self.add_item(
            EditRoleSelect.get_instance(
                lang=lang,
                roles=self.roles,
                guild_roles=guild_roles,
                guild_id=guild_id,
                member_roles=member_roles
            )
        )
