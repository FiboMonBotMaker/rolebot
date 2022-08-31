from lib.dbutil import select
from discord import Interaction, ButtonStyle, Embed, Color
from discord.ui import Button, View


def get_roles(guild_id: int) -> list[int]:
    rows = select(table_name="roles", columns=["role_id"],
                  where=f"guild_id = {guild_id}")
    roles = []
    for v in rows:
        roles.append(v[0])
    return roles


class BaseView(View):
    def __init__(self, lang: dict, guild_id: int):
        super().__init__(timeout=300)
        self.lang = lang
        self.roles = get_roles(guild_id=guild_id)
        self.add_item(self.ExitButton(lang=lang))

    class ExitButton(Button):
        def __init__(self, lang: dict):
            self.lang: dict = lang["base"]
            super().__init__(
                style=ButtonStyle.red,
                label=self.lang["button"],
                row=4)

        async def callback(self, interaction: Interaction):
            await interaction.response.edit_message(content=None, embed=Embed(color=Color.green(), title=self.lang["message"]), view=None)
