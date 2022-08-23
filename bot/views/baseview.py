from lib.dbutil import select
from discord import Interaction, ButtonStyle
from discord.ui import Button, View, button


def get_roles(guild_id: str) -> list[int]:
    rows = select(table_name="roles", columns=["role_id"],
                  where=f"guild_id = {guild_id}")
    roles = []
    for v in rows:
        roles.append(v[0])
    return roles


class BaseView(View):
    def __init__(self, guild_id):
        super().__init__(timeout=300)
        self.roles = get_roles(guild_id=guild_id)

    @button(label="Exit", row=4, style=ButtonStyle.red)
    async def exit_menu(self, _: Button, interaction: Interaction):
        await interaction.response.edit_message(content="Bye", embed=None, view=None)
