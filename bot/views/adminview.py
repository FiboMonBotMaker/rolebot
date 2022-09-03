from lib.dbutil import delete, insert
from lib.guild_role import get_role_dict
from discord import Interaction, Role, ButtonStyle, InputTextStyle, Colour, ApplicationCommandError, SelectOption, Embed, Color
from discord.ui import Button,  Select, InputText, Modal, View
from views.baseview import BaseView


def get_select_options(roles: list[int], guild_roles: list[Role], guild_id: int) -> list[SelectOption]:
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
    def __init__(self, lang: dict, guild_id: int):
        super().__init__(guild_id=guild_id, lang=lang)
        self.add_item(self.MainMenuButton(lang=lang))

    class MainMenuButton(Button):
        def __init__(self, lang):
            self.lang = lang
            super().__init__(
                style=ButtonStyle.green,
                label=self.lang["admin"]["base"]["button"],
                row=3
            )

        async def callback(self, interaction: Interaction):
            await interaction.response.edit_message(
                content=None,
                embed=Embed(
                    color=Color.green(),
                    title=self.lang["admin"]["base"]["title"]
                ),
                view=AdminMainView(
                    lang=self.lang,
                    guild_id=interaction.guild_id
                )
            )


class AdminMainView(BaseView):
    def __init__(self, lang: dict, guild_id: int):
        super().__init__(guild_id=guild_id, lang=lang)
        self.add_item(self.AddingRoleButton(lang=lang))
        self.add_item(self.RemoveRoleButton(lang=lang))

    class AddingRoleButton(Button):
        def __init__(self, lang):
            self.lang = lang
            super().__init__(
                style=ButtonStyle.blurple,
                label=self.lang["admin"]["main"]["button"]["adding"],
                row=0
            )

        async def callback(self, interaction: Interaction):
            m = AddingRoleModal(lang=self.lang, interaction=interaction)
            await interaction.response.send_modal(modal=m)

    class RemoveRoleButton(Button):
        def __init__(self, lang):
            self.lang = lang
            super().__init__(
                style=ButtonStyle.blurple,
                label=self.lang["admin"]["main"]["button"]["remove"],
                row=1
            )

        async def callback(self, interaction: Interaction):
            try:
                v = RemoveRoleView(
                    lang=self.lang,
                    guild_id=interaction.guild_id,
                    guild_roles=interaction.guild.roles,
                )
            except ApplicationCommandError as e:
                await interaction.response.edit_message(content=f"**Error!!**\n*{e}*")
                return
            await interaction.response.edit_message(
                content=None,
                embed=Embed(
                    color=Color.orange(),
                    title=self.lang["admin"]["main"]["button"]["remove"]
                ),
                view=v
            )


class AddingRoleModal(Modal):
    def __init__(self, lang: dict, interaction: Interaction):
        self.lang = lang
        self.interaction = interaction
        super().__init__(title=lang["admin"]["adding"]["modal"]["title"])
        self.add_item(
            InputText(
                style=InputTextStyle.short,
                label=lang["admin"]["adding"]["modal"]["rolename"]["title"],
                placeholder=lang["admin"]["adding"]["modal"]["rolename"]["placeholder"],
                min_length=1,
                max_length=30,
                required=True,
            )
        )
        self.add_item(
            InputText(
                style=InputTextStyle.short,
                label=lang["admin"]["adding"]["modal"]["rolecolor"]["title"],
                placeholder=lang["admin"]["adding"]["modal"]["rolecolor"]["placeholder"],
                min_length=6,
                max_length=6,
                required=False,
            )
        )

    class SettingRoleView(View):
        def __init__(self, lang: dict, role_name: str, role_color: Colour):
            super().__init__()
            self.lang = lang
            self.role_name = role_name
            self.role_color = role_color
            self.mentionable = False
            self.add_item(
                self.MentionableButton(
                    lang=lang,
                    mentionable=self.mentionable
                )
            )
            self.add_item(
                self.ExecuteButton(lang=lang)
            )

        def get_status(lang: dict, mentionable: bool) -> tuple[str, ButtonStyle]:
            label = (
                lang['admin']['adding']['modal']['button']['enable']
                if mentionable
                else lang['admin']['adding']['modal']['button']['disable']
            )
            style = ButtonStyle.green if mentionable else ButtonStyle.red
            return label, style

        def toggle_mentionable(self):
            self.mentionable = not self.mentionable
            button: Button = self.children[0]
            label, style = AddingRoleModal.SettingRoleView.get_status(
                self.lang, self.mentionable)
            button.label = label
            button.style = style

        class MentionableButton(Button):
            def __init__(self, lang: dict, mentionable: bool):
                label, style = AddingRoleModal.SettingRoleView.get_status(
                    lang, mentionable)

                super().__init__(
                    style=style,
                    label=label,
                    row=0,
                )

            async def callback(self, interaction: Interaction):
                view: AddingRoleModal.SettingRoleView = self.view
                view.toggle_mentionable()
                await interaction.response.edit_message(view=view)

        class ExecuteButton(Button):
            def __init__(self, lang: dict):
                super().__init__(
                    style=ButtonStyle.success,
                    label=lang['admin']['adding']['modal']['button']['create'],
                    row=0,
                )

            async def callback(self, interaction: Interaction):
                view: AddingRoleModal.SettingRoleView = self.view
                new_role = await interaction.guild.create_role(name=view.role_name, color=view.role_color, mentionable=view.mentionable)
                insert_role(interaction.guild_id, new_role.id)
                await interaction.response.edit_message(
                    embed=Embed(title=view.lang['admin']['adding']['modal']['execute'], description=f"<@&{new_role.id}>"), view=AdminMainView(lang=view.lang, guild_id=interaction.guild_id))

    async def callback(self, interaction: Interaction):
        await interaction.response.defer()
        role_name = self.children[0].value
        role_color = Colour.random()
        try:
            if len(self.children[1].value) != 0:
                role_color = int(f"0x{self.children[1].value}", 16)
        except ValueError:
            ...
        await self.interaction.edit_original_message(
            content=None,
            embed=Embed(title=self.lang['admin']
                        ['adding']['modal']["mention"]),
            view=self.SettingRoleView(lang=self.lang, role_name=role_name, role_color=role_color))


class RemoveRoleView(AdminReturnBaseView):
    def __init__(self, lang: dict, guild_id: int, guild_roles: list[Role]):
        super().__init__(guild_id=guild_id, lang=lang)
        self.add_item(
            RemoveRoleView.RemoveRoleSelect.get_instance(
                lang=lang,
                roles=self.roles,
                guild_roles=guild_roles,
                guild_id=guild_id
            )
        )

    class RemoveRoleSelect(Select["RemoveRoleView"]):
        def __init__(self, lang: dict, options: list[SelectOption]) -> None:
            self.lang = lang
            super().__init__(
                placeholder=lang["admin"]["remove"]["select"]["placeholder"],
                options=options
            )

        async def callback(self, interaction: Interaction):
            remove_role_id = int(self.values[0])
            target_role = interaction.guild.get_role(remove_role_id)
            role_name = target_role.name
            await target_role.delete()
            delete_role(guild_id=interaction.guild_id, role_id=remove_role_id)
            v = AdminMainView(lang=self.lang, guild_id=interaction.guild_id)
            await interaction.response.edit_message(content=f"{self.lang['admin']['remove']['select']['execute']}: **{role_name}**", view=v)

        def get_instance(lang: dict, roles: list[int], guild_roles: list[Role], guild_id: int):
            options = get_select_options(
                roles=roles, guild_roles=guild_roles, guild_id=guild_id)
            return RemoveRoleView.RemoveRoleSelect(lang=lang, options=options)
