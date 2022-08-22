from views.adminmodel import AdminMainView
from discord.commands import SlashCommandGroup
from discord.ext import commands
from discord import ApplicationContext


class LanaNealsen(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    role = SlashCommandGroup(name="role", description="ロール管理")

    # @role.command(name="check_role", description="現在ついているロールの確認を行う事ができます。")
    # async def check(self, ctx: ApplicationContext):
    #     v = MemberMainView(
    #         guild_id=str(ctx.guild_id),
    #         guild_roles=ctx.guild.roles,
    #     )
    #     await ctx.respond(view=v, ephemeral=True)

    @role.command(name="control", description="管理者用コマンドです。ロールの追加や削除などが行なえます。")
    @commands.has_permissions(administrator=True)
    async def control(self, ctx: ApplicationContext):
        ctx.bot.get_guild(ctx.guild_id).roles
        v = AdminMainView(
            guild_id=str(ctx.guild_id),
        )
        await ctx.respond(content="*Main Menu*", view=v, ephemeral=True)


def setup(bot):
    bot.add_cog(LanaNealsen(bot))
