from lib.dbutil import select
from discord import SelectOption, Role
from discord import ApplicationCommandError


def get_select_options(roles: list[int], guild_roles: list[Role]):
    options = []
    if len(roles) == 0:
        raise ApplicationCommandError("Role data is zero length")
    for gr in guild_roles:
        if gr.id in roles:
            options.append(
                SelectOption(
                    label=gr.name,
                    value=str(gr.id),
                )
            )
    return options


def get_roles(guild_id: str) -> list[int]:
    rows = select(table_name="roles", columns=["role_id"],
                  where=f"guild_id = {guild_id}")
    roles = []
    for v in rows:
        roles.append(v[0])
    return roles
