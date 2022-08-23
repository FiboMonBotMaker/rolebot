from views.adminview import AdminMainView
from views.memberview import MemberMainView, RoleListEmbed
from discord.commands import SlashCommandGroup
from discord.ext import commands
from discord import ApplicationContext, EmbedField, File


class LanaNealsen(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    role = SlashCommandGroup(name="role", description="Manage roles")

    @role.command(name="check_role", description="You can manage the roles attached to you.")
    async def check(self, ctx: ApplicationContext):
        v = MemberMainView(
            guild_id=str(ctx.guild_id),
        )
        embed = RoleListEmbed(
            name=ctx.author.name,
            icon_url=ctx.author.avatar.url,
            roles=v.roles,
            member_roles=ctx.author.roles,
            guild_roles=ctx.guild.roles,
            guild_id=ctx.guild_id
        )
        await ctx.respond(embed=embed, view=v, ephemeral=True)

    @role.command(name="control", description="This command is for administrators. You can add roles, etc.")
    @commands.has_permissions(administrator=True)
    async def control(self, ctx: ApplicationContext):
        ctx.bot.get_guild(ctx.guild_id).roles
        v = AdminMainView(
            guild_id=str(ctx.guild_id),
        )
        await ctx.respond(content="*Main Menu*", view=v, ephemeral=True)


def setup(bot):
    bot.add_cog(LanaNealsen(bot))
