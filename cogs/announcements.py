import asyncio
import datetime

import discord
from discord.ext import commands
from discord.ext.commands import has_permissions


class Announcements(commands.Cog):
    def __init__(self, client):
        """

        Format of Multi-dim Array: ann_list[[ID, title, description, imageURL, thumbnail, channel,
        inlineList, target], . . .]

        Format of inlineList = [[title, description], . . .]
        TODO:
            - Add textfile storage.
        """
        self.client = client
        self.ann_list = []

    async def prompted_input(self, ctx, prompt):
        prompt_str = await ctx.send(prompt)
        user_input = await self.client.wait_for("message", check=lambda m: m.author == ctx.author)

        await prompt_str.delete()
        return user_input.content

    async def assign_inarray(self, ctx, outer_index, inner_index, value):
        try:
            self.ann_list[outer_index][inner_index] = value
        except IndexError:
            await ctx.send("Event ID does not exist.")
            return None

    @commands.command()
    @has_permissions(manage_roles=True)
    async def create_announcement(self, ctx, arg1=None):
        # Arg1 = Title
        try:
            arg1 = str(arg1)

            ann_new = [None] * 8
            ann_id = len(self.ann_list)
            ann_new[0], ann_new[1] = ann_id, arg1

            self.ann_list.append(ann_new)
            await ctx.send(f"Created Event - Title: {arg1} ID: {ann_id}")
        except:
            await ctx.send("Incorrect usage of command: !create_announcement [title]")

    @commands.command()
    @has_permissions(manage_roles=True)
    async def mod_anntitle(self, ctx, arg1=None, arg2=None):
        try:
            if arg1 is None:
                arg1 = len(self.ann_list) - 1
            arg1 = int(arg1)
            title = self.prompted_input(ctx, "Please enter the new title of the event: ")
            await self.assign_inarray(ctx, arg1, 1, title)
        except:
            await ctx.send("Incorrect usage of command: !mod_anntitle [eventID] [Title]")

    @commands.command()
    @has_permissions(manage_roles=True)
    async def mod_anndesc(self, ctx, arg1=None):
        try:
            if arg1 is None:
                arg1 = len(self.ann_list) - 1
            arg1 = int(arg1)
            desc = self.prompted_input(ctx, "Please enter the new description of the event: ")
            await self.assign_inarray(ctx, arg1, 2, desc)
        except:
            await ctx.send("Incorrect usage of command: !mod_anndesc [eventID] [description]")

    @commands.command()
    @has_permissions(manage_roles=True)
    async def mod_annimage(self, ctx, arg1=None, arg2=None):
        try:
            if arg1 is None:
                arg1 = len(self.ann_list) - 1
            arg1 = int(arg1)
            await self.assign_inarray(ctx, arg1, 3, arg2)
        except:
            await ctx.send("Incorrect usage of command: !mod_annimage [eventID] [image URL]")

    @commands.command()
    @has_permissions(manage_roles=True)
    async def mod_annthumbnail(self, ctx, arg1=None, arg2=None):
        try:
            if arg1 is None:
                arg1 = len(self.ann_list) - 1
            arg1 = int(arg1)
            await self.assign_inarray(ctx, arg1, 4, arg2)
        except:
            await ctx.send("Incorrect usage of command: !mod_annthumbnail [eventID] [image URL]")

    @commands.command()
    @has_permissions(manage_roles=True)
    async def add_anninline(self, ctx, arg1=None):
        try:
            if arg1 is None:
                arg1 = len(self.ann_list) - 1

            arg1 = int(arg1)

            num_inline = int(await self.prompted_input(ctx, "How many inlines would you like?"))

            inline_appendage = []
            for i in range(num_inline):
                field_title = await self.prompted_input(ctx, f"State title of field name: {str(i + 1)}")
                field_description = await self.prompted_input(ctx, "State the description: ")

                field = [field_title, field_description]
                inline_appendage.append(field)

            self.ann_list[arg1][6] = inline_appendage
        except IndexError:
            await ctx.send("Event ID does not exist.")
        else:
            await ctx.send("Incorrect usage of the command: !add_anninline [eventID]")

    @commands.command()
    @has_permissions(manage_roles=True)
    async def add_anntarget(self, ctx, arg1=None, arg2="everyone"):
        try:
            if arg1 is None:
                arg1 = len(self.ann_list) - 1
            arg1 = int(arg1)

            target_role = discord.utils.get(ctx.guild.roles, name=str(arg2))
            self.ann_list[arg1][7] = target_role
        except:
            await ctx.send("Incorrect usage of the command: !add_anntarget [eventID] [target role]")

    @commands.command()
    @has_permissions(manage_roles=True)
    async def add_channeltarget(self, ctx, arg1=None, arg2="announcements"):
        try:
            if arg1 is None:
                arg1 = len(self.ann_list) - 1
            arg1 = int(arg1)

            self.ann_list[arg1][5] = arg2
        except:
            await ctx.send("Incorrect usage of the command: !add_anntarget [eventID] [target role]")

    @commands.command()
    @has_permissions(manage_roles=True)
    async def submit_announcement(self, ctx, arg1=None, arg2=None):
        # Arg1=EventID
        # Arg2=Time?

        if arg1 is None:
            arg1 = len(self.ann_list) - 1
        # Scheduler
        if arg2 is not None:
            arg2 = arg2.split(':')
            cur_time = datetime.datetime.now()
            delta = datetime.timedelta(hours=int(arg2[0]), minutes=int(arg2[1]),
                                       seconds=int(arg2[2])) - datetime.timedelta(hours=cur_time.hour,
                                                                                  minutes=cur_time.minute,
                                                                                  seconds=cur_time.second)
            delta_seconds = delta.total_seconds()

        arg1 = int(arg1)

        cur_pos = self.ann_list[arg1]

        embed = discord.Embed()

        embed.title = str(cur_pos[1])
        embed.description = str(cur_pos[2])

        if cur_pos[3] is not None: embed.set_image(url=cur_pos[3])
        if cur_pos[4] is not None: embed.set_thumbnail(url=cur_pos[4])
        if cur_pos[7] is not None: await ctx.send(cur_pos[7].mention)

        #
        if cur_pos[6] is not None:
            for field in cur_pos[6]:
                embed.add_field(name=field[0], value=field[1], inline=True)

        # Sleep until announcement time.
        if arg2 is not None: await asyncio.sleep(delta_seconds)

        # Out the embed
        if cur_pos[5] is None:
            await ctx.send(embed=embed)
        else:
            channel = discord.utils.get(ctx.guild.text_channels, name=cur_pos[5])
            await channel.send(embed=embed)


def setup(client):
    client.add_cog(Announcements(client))
