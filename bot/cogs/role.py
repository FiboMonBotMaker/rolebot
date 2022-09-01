from views.adminview import AdminMainView
from views.memberview import MemberMainView, RoleListEmbed
from discord.commands import SlashCommandGroup
from discord.ext import commands
from discord import ApplicationContext, Embed, Color
from lib.locale import get_command_description, get_default_command_description, get_lang


class LanaNealsen(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    role = SlashCommandGroup(name="role", description="Manage roles")

    admin = role.create_subgroup(
        name="admin",
        description="Admin commands",
        checks=[commands.has_permissions(administrator=True).predicate]
    )

    @role.command(
        name="check",
        description=get_default_command_description("check"),
        description_localizations=get_command_description("check")
    )
    async def check(self, ctx: ApplicationContext):
        lang = get_lang(ctx.locale)
        view = MemberMainView(
            lang=lang,
            guild_id=str(ctx.guild_id),
        )
        embed = RoleListEmbed(
            lang=lang,
            name=ctx.author.name,
            icon_url=ctx.user.avatar.url if ctx.user.avatar != None else "",
            roles=view.roles,
            member_roles=ctx.author.roles,
            guild_roles=ctx.guild.roles,
            guild_id=ctx.guild_id
        )
        await ctx.respond(embed=embed, view=view, ephemeral=True)

    @admin.command(
        name="control",
        description=get_default_command_description("control"),
        description_localizations=get_command_description("control"),
    )
    async def control(self, ctx: ApplicationContext):
        lang = get_lang(ctx.locale)
        view = AdminMainView(
            lang=lang,
            guild_id=str(ctx.guild_id),
        )
        await ctx.respond(embed=Embed(color=Color.green(), title=lang['admin']['main']['title']), view=view, ephemeral=True)

    # @admin.command(
    #     name="set_panel",
    #     description=get_default_command_description("set_panel"),
    #     description_localizations=get_command_description("set_panel"),
    # )
    # async def set_panel(self, ctx: ApplicationContext):
    #     lang = get_lang(ctx.locale)
    #     ctx.respond("test")


def setup(bot: commands.Bot):
    bot.add_cog(LanaNealsen(bot))
