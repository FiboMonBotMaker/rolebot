from discord import Role


def get_role_dict(guild_roles: list[Role]):
    return {v.id: v.name for v in guild_roles}
