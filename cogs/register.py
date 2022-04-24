from discord import PermissionOverwrite
from discord.ext import commands
from discord_components import DiscordComponents, SelectOption, Select
from connect_to_db import connect_to_db
from discord.utils import get


class register(commands.Cog):
    def __init__(self, client):
        self.client = client
        DiscordComponents(client)
        # connect to mongo db
        print("Register connecting to mongoDB....")
        self.db = connect_to_db()
        print("Register connected to database!")

    async def guild_null(self, ctx):
        if ctx.guild is None:
            await ctx.send("This command does not work in direct messages!")
            return True
        return False

    @commands.command(name='register')
    async def register(self, ctx):
        # check if command is not in direct messages
        if await self.guild_null(ctx):
            return
        # get user discord id
        discord_id = str(ctx.author)
        guild_id = str(ctx.guild.id)

        # check if discord user is already in the database
        if self.db.check_active(discord_id, guild_id):
            await ctx.send("You are already in this database.")
            return

        # open a dm channel with user
        dm = await ctx.author.create_dm()

        # helper function that checks if a message is in the authors dm channel
        def check(msg):
            return msg.author == ctx.author and msg.channel == dm

        # get first name
        await dm.send("First Name?")
        fn = await self.client.wait_for("message", check=check)
        first_name = fn.content

        # get last name
        await dm.send("Last Name?")
        ln = await self.client.wait_for("message", check=check)
        last_name = ln.content

        # get timezone
        await dm.send("What is your timezone?", components=[
            Select(
                placeholder="Timezone",
                options=[
                          SelectOption(label="MIT	Midway Islands Time	GMT-11:00", value='Pacific/Midway'),
                          SelectOption(label="HST	Hawaii Standard Time GMT-10:00", value='US/Hawaii'),
                          SelectOption(label="AST Alaska Standard Time GMT-9:00", value='US/Alaska'),
                          SelectOption(label="PST	Pacific Standard Time	GMT-8:00", value='US/Pacific'),
                          SelectOption(label="MST	Mountain Standard Time GMT-7:00", value='US/Mountain'),
                          SelectOption(label="CST	Central Standard Time	GMT-6:00", value='US/Central'),
                          SelectOption(label="EST	Eastern Standard Time	GMT-5:00", value='US/Eastern'),
                          SelectOption(
                              label="PRT	Puerto Rico and US Virgin Islands Time GMT-4:00",
                              value='America/Puerto_Rico'),
                          SelectOption(label="AGT	Argentina Standard Time	GMT-3:00", value='America/Argentina/Ushuaia'),
                          SelectOption(label="UTC	Universal Coordinated Time GMT+0:00", value='UTC'),
                          SelectOption(label="ECT	European Central Time	GMT+1:00", value='Europe/Rome'),
                          SelectOption(label="EET	Eastern European Time	GMT+2:00", value='Europe/Kiev'),
                          SelectOption(label="EAT	Eastern African Time GMT+3:00", value='Africa/Nairobi'),
                          SelectOption(label="NET	Near East Time GMT+4:00", value='Asia/Dubai'),
                          SelectOption(label="PLT	Pakistan Lahore Time GMT+5:00", value='Asia/Oral'),
                          SelectOption(label="BST	Bangladesh Standard Time GMT+6:00", value='Asia/Bishkek'),
                          SelectOption(label="VST	Vietnam Standard Time	GMT+7:00", value='Asia/Bangkok'),
                          SelectOption(label="CTT	China Taiwan Time	GMT+8:00", value='Asia/Hong_Kong'),
                          SelectOption(label="JST	Japan Standard Time	GMT+9:00", value='Asia/Tokyo'),
                          SelectOption(label="AET	Australia Eastern Time GMT+10:00", value='Australia/Brisbane'),
                          SelectOption(label="SST	Solomon Standard Time	GMT+11:00", value='Australia/Sydney'),
                          SelectOption(label="NST	New Zealand Standard Time	GMT+12:00", value='Pacific/Fiji')
                ],
                custom_id='timezone'
            )
        ])
        timezone_interaction = await self.client.wait_for(
            "select_option", check=lambda i: i.custom_id == "timezone" and i.user == ctx.author)
        timezone = timezone_interaction.values[0]
        await self.clear_last_msg(dm)
        member_id = ctx.author.id
        self.db.add_user(discord_id, first_name, last_name, timezone, guild_id, member_id)

        # post verfication in discord channel
        await ctx.send(first_name + " " + last_name + " created in the database.")

    @commands.command(name='promote')
    async def promote(self, ctx):
        if await self.guild_null(ctx):
            return
        # get user discord id
        discord_id = str(ctx.author)
        guild_id = str(ctx.guild.id)
        dm = await ctx.author.create_dm()
        if discord_id == ctx.guild.owner.id or self.db.check_manager(discord_id, guild_id):
            records = self.db.get_employee_records(guild_id)
            ops = []

            for emp in records.find({'manager': False}):
                label = str(emp['name_first'] + " " + str(emp['name_last']))
                ops.append(SelectOption(label=label, value=str(emp['discord_id'])))

            ops.append(SelectOption(label='Cancel', value='end'))

            await dm.send("Who would you like to promote?", components=[
                Select(
                  placeholder="Select a new manager",
                  options=ops,
                  custom_id='promote'
                  )
            ])

            promote_interaction = await self.client.wait_for(
                "select_option", check=lambda i: i.custom_id == "promote" and i.user == ctx.author)
            promote = str(promote_interaction.values[0])

            await self.clear_last_msg(dm)

            if promote == "end":
                await dm.send("Promotion canceled.")

            else:
                self.db.promote_manager(promote, guild_id)
                await dm.send("Promotion complete!")
                slice = records.find_one({'discord_id': promote})
                member_id = slice['member_id']
                user = get(ctx.guild.members, id=member_id)
                manager_check = False

                for role in ctx.guild.roles:
                    if role.name == "Manager":
                        manager_check = True
                        manager_role = role

                if not manager_check:
                    manager_role = await ctx.guild.create_role(name="Manager")

                if user:
                    await user.add_roles(manager_role, atomic=True)
                    channel_check = False
                    for channel in await ctx.guild.fetch_channels():
                        if channel.name == "timeclock-manager-log":
                            channel_check = True

                    if not channel_check:
                        default = ctx.guild.default_role

                        overwrites = {
                            default: PermissionOverwrite(read_messages=False),
                            manager_role: PermissionOverwrite(read_messages=True)
                        }
                        channel = await ctx.guild.create_text_channel(
                            name='timeclock-manager-log', overwrites=overwrites)

        else:
            await dm.send("You do not have permission to access this command. (peasant)")

    @commands.command(name='demote')
    async def demote(self, ctx):
        if await self.guild_null(ctx):
            return
        # get user discord id
        discord_id = str(ctx.author)
        guild_id = str(ctx.guild.id)
        dm = await ctx.author.create_dm()
        if discord_id == ctx.guild.owner.id or self.db.check_manager(discord_id, guild_id):
            records = self.db.get_employee_records(guild_id)
            ops = []

            for emp in records.find({'manager': True}):
                if emp['discord_id'] == discord_id:
                    continue
                label = str(emp['name_first'] + " " + str(emp['name_last']))
                ops.append(SelectOption(label=label, value=str(emp['discord_id'])))

            ops.append(SelectOption(label='Cancel', value='end'))
            await dm.send("Who would you like to demote?", components=[
                Select(
                    placeholder="Select a manager for demotion",
                    options=ops,
                    custom_id='demote'
                )
            ])

            demote_interaction = await self.client.wait_for(
                "select_option", check=lambda i: i.custom_id == "demote" and i.user == ctx.author)
            demote = str(demote_interaction.values[0])
            await self.clear_last_msg(dm)
            if demote == "end":
                await dm.send("Demotion canceled.")

            else:
                self.db.demote_manager(demote, guild_id)
                manager_role = get(ctx.guild.roles, name="Manager")
                slice = records.find_one({'discord_id': demote})
                member_id = slice['member_id']
                user = get(ctx.guild.members, id=member_id)
                await user.remove_roles(manager_role, atomic=True)
                await dm.send("Demotion complete.")

        else:
            await dm.send("You do not have permission to access this command. (peasant)")

    @commands.command(name='edit')
    async def edit(self, ctx):
        # check if command is not in direct messages
        if await self.guild_null(ctx):
            return
        # get user discord id
        discord_id = str(ctx.author)
        guild_id = str(ctx.guild.id)
        # get mongoDB table
        records = self.db.get_employee_records(guild_id)
        # check if discord user is already in the database
        if not self.db.check_active(discord_id, guild_id):
            return

        # open a dm channel with user
        dm = await ctx.author.create_dm()
        # ######## v ################ v REMOVE EVENTUALLY ##################### v
        self.db.update_all_manager_values(guild_id)
        # ######### ^ ################## REMOVE EVENTUALLY ####################### ^
        # helper function that checks if a message is in the authors dm channel

        def check(msg):
            return msg.author == ctx.author and msg.channel == dm

        old = records.find_one({'discord_id': discord_id})
        old_first = old['name_first']
        old_last = old['name_last']

        # get first name
        await dm.send("Current: " + old_first + "\nFirst Name?")
        fn = await self.client.wait_for("message", check=check)
        first_name = fn.content

        # get last name
        await dm.send("Current: " + old_last + "\nLast Name?")
        ln = await self.client.wait_for("message", check=check)
        last_name = ln.content

        # get timezone
        await dm.send("What is your timezone?", components=[
            Select(
                placeholder="Timezone",
                options=[
                          SelectOption(label="MIT	Midway Islands Time	GMT-11:00", value='Pacific/Midway'),
                          SelectOption(label="HST	Hawaii Standard Time	GMT-10:00", value='US/Hawaii'),
                          SelectOption(label="AST Alaska Standard Time - GMT-9:00", value='US/Alaska'),
                          SelectOption(label="PST	Pacific Standard Time	GMT-8:00", value='US/Pacific'),
                          SelectOption(label="MST	Mountain Standard Time	GMT-7:00", value='US/Mountain'),
                          SelectOption(label="CST	Central Standard Time	GMT-6:00", value='US/Central'),
                          SelectOption(label="EST	Eastern Standard Time	GMT-5:00", value='US/Eastern'),
                          SelectOption(
                              label="PRT	Puerto Rico and US Virgin Islands Time	GMT-4:00",
                              value='America/Puerto_Rico'
                          ),
                          SelectOption(label="AGT	Argentina Standard Time	GMT-3:00", value='America/Argentina/Ushuaia'),
                          SelectOption(label="UTC	Universal Coordinated Time	GMT+0:00", value='UTC'),
                          SelectOption(label="ECT	European Central Time	GMT+1:00", value='Europe/Rome'),
                          SelectOption(label="EET	Eastern European Time	GMT+2:00", value='Europe/Kiev'),
                          SelectOption(label="EAT	Eastern African Time	GMT+3:00", value='Africa/Nairobi'),
                          SelectOption(label="NET	Near East Time	GMT+4:00", value='Asia/Dubai'),
                          SelectOption(label="PLT	Pakistan Lahore Time	GMT+5:00", value='Asia/Oral'),
                          SelectOption(label="BST	Bangladesh Standard Time	GMT+6:00", value='Asia/Bishkek'),
                          SelectOption(label="VST	Vietnam Standard Time	GMT+7:00", value='Asia/Bangkok'),
                          SelectOption(label="CTT	China Taiwan Time	GMT+8:00", value='Asia/Hong_Kong'),
                          SelectOption(label="JST	Japan Standard Time	GMT+9:00", value='Asia/Tokyo'),
                          SelectOption(label="AET	Australia Eastern Time	GMT+10:00", value='Australia/Brisbane'),
                          SelectOption(label="SST	Solomon Standard Time	GMT+11:00", value='Australia/Sydney'),
                          SelectOption(label="NST	New Zealand Standard Time	GMT+12:00", value='Pacific/Fiji')
                ],
                custom_id='timezone'
                )
        ])
        timezone_interaction = await self.client.wait_for(
            "select_option", check=lambda i: i.custom_id == "timezone" and i.user == ctx.author)
        timezone = timezone_interaction.values[0]
        await self.clear_last_msg(dm)

        # store employee in the database
        records.update_one(
            {'discord_id': discord_id},
            {"$set":
                {
                    'member_id': ctx.author.id,
                    'name_first': first_name,
                    'name_last': last_name,
                    'timezone': timezone
                }}
        )

        # post verfication in discord channel
        await dm.send("You have updated your information.")

    async def create_mng_log(self, ctx):
        channel_check = False
        manager_check = False

        for role in ctx.guild.roles:
            if role.name == "Manager":
                manager_check = True
                manager_role = role

        if not manager_check:
            manager_role = await ctx.guild.create_role(name="Manager")

        for channel in await ctx.guild.fetch_channels():
            if channel.name == "timeclock-manager-log":
                channel_check = True

        if not channel_check:
            default = ctx.guild.default_role

            overwrites = {
              default: PermissionOverwrite(read_messages=False),
              manager_role: PermissionOverwrite(read_messages=True)
            }
            channel = await ctx.guild.create_text_channel(name='timeclock-manager-log', overwrites=overwrites)

    async def clear_last_msg(self, channel):
        async for x in channel.history(limit=1):
            await x.delete()


def setup(client):
    client.add_cog(register(client))