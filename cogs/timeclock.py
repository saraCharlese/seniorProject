from datetime import datetime, timedelta
from discord import PermissionOverwrite, File, Embed
from discord_components import DiscordComponents, Button, SelectOption, Select
from discord.ext import commands
from connect_to_db import connect_to_db
import pytz
import asyncio
import csv
from dateutil.relativedelta import relativedelta
import os


class timeclock(commands.Cog):
    def __init__(self, client):
        self.client = client
        DiscordComponents(client)
        # connect to mongo db
        print("Timeclock connecting to mongoDB....")
        self.db = connect_to_db()
        print("Timeclock connected to database!")

    async def guild_null(self, ctx):
        if ctx.guild is None:
            await ctx.send("This command does not work in direct messages!")
            return True
        return False

    @commands.command(name='in')
    async def clock_in(self, ctx):
        # check if command is not in direct messages
        if await self.guild_null(ctx):
            return

        # get user discord id
        discord_id = str(ctx.author)
        guild_id = str(ctx.guild.id)
        # open direct message channel with author
        dm = await ctx.author.create_dm()

        # check if discord user is in the database
        if not self.db.check_active(discord_id, guild_id):
            embed = Embed(title=" ", color=0x000FF)
            embed.add_field(name="You are not registered with this discord server.", value=str("Please use the 'register' command to sign up before clocking in"))
            await dm.send(embed=embed)
            return

        # check if user is already clocked in
        if self.db.check_in(discord_id, guild_id):
            embed = Embed(title="You are already clocked in!", color=0x000FF)
            await dm.send(embed=embed)
            return

        # verify user has set their timezone
        users = self.db.get_employee_records(guild_id)
        userdata = list(users.find({'discord_id': discord_id, "timezone": {"$exists": False}}))
        if len(userdata) > 0:
            embed = Embed(title="Please use the 'edit' command to update your timezone before clocking in.", color=0x000FF)
            await dm.send(embed=embed)
            return

        userdata = users.find_one({'discord_id': discord_id})
        timezone = userdata['timezone']
        timezone_pytz = pytz.timezone(timezone)
        in_time = datetime.now(tz=pytz.timezone('UTC'))

        if self.db.clock_user_in(discord_id, guild_id):
            # post verfication in discord channel
            embed = Embed(title="You have clocked in.")
            embed.add_field(name="In time:", value=str(in_time.astimezone(timezone_pytz).strftime('%I:%M:%S %p')))
            await dm.send(embed=embed)
            embed = Embed(title=userdata["name_first"] + " " + userdata["name_last"] + " has clocked in.")
            embed.add_field(name="In time:", value=str(in_time.astimezone(timezone_pytz).strftime('%I:%M:%S %p')))
            await self.post_mng_log_embed(ctx, embed)
            # start 10 hour timer
            await self.ten_hour_check(ctx)
        else:
            embed = Embed(title="There has been an error in your clock in.", color=0x000FF)
            await dm.send(embed=embed)

    @commands.command(name='out')
    async def clock_out(self, ctx):
        # check if command is not in direct messages
        if await self.guild_null(ctx):
            return
        # get user discord id
        discord_id = str(ctx.author)
        guild_id = str(ctx.guild.id)
        # create direct message channel with author
        dm = await ctx.author.create_dm()

        # check if discord user is clocked in
        if not self.db.check_in(discord_id, guild_id):
            embed = Embed(title="You are not clocked in.", color=0x000FF)
            await dm.send(embed=embed)
            return

        # verify user has set their timezone
        users = self.db.get_employee_records(guild_id)
        userdata = list(users.find({'timezone': {'$exists': False}, 'discord_id': discord_id}))

        if len(userdata) > 0:
            embed = Embed(title="Please use the 'edit' command to update your timezone before clocking out.", color=0x000FF)
            await dm.send(embed=embed)
            return

        records = self.db.get_active_shifts(guild_id)
        shift_data = records.find_one({'discord_id': discord_id})

        userdata = users.find_one({'discord_id': discord_id})
        timezone = userdata['timezone']
        timezone_pytz = pytz.timezone(timezone)
        in_time_data = shift_data["in_time"]
        out_time = datetime.now().astimezone(pytz.timezone('UTC'))
        tz = pytz.timezone("UTC")
        in_time = tz.localize(in_time_data)
        total = out_time - in_time

        if self.db.clock_user_out(discord_id, guild_id):
            embed = Embed(title="You have been clocked out.")
            embed.add_field(name="In time:", value=str(in_time.astimezone(timezone_pytz).strftime('%I:%M:%S %p')))
            embed.add_field(name="Out time:", value=str(out_time.astimezone(timezone_pytz).strftime('%I:%M:%S %p')))
            embed.add_field(name="Time Worked:", value=str(str(total).split(".")[0]))
            await dm.send(embed=embed)
            embed = Embed(title=userdata["name_first"] + " " + userdata["name_last"] + " has clocked out.")
            embed.add_field(name="In time:", value=str(in_time.astimezone(timezone_pytz).strftime('%I:%M:%S %p')))
            embed.add_field(name="Out time:", value=str(out_time.astimezone(timezone_pytz).strftime('%I:%M:%S %p')))
            embed.add_field(name="Time Worked:", value=str(str(total).split(".")[0]))
            await self.post_mng_log_embed(ctx, embed)

        else:
            embed = Embed(title="There has been an error in your clock out.", color=0x000FF)
            await dm.send(embed=embed)

    @commands.command(name='fix')
    async def fix(self, ctx):
        # check if command is not in direct messages
        if await self.guild_null(ctx):
            return
        # helper function that checks if a message is in the authors dm channel

        # get user discord id
        discord_id = str(ctx.author)
        guild_id = str(ctx.guild.id)
        # create direct message channel with author
        dm = await ctx.author.create_dm()

        # verify user has set their timezone
        users = self.db.get_employee_records(guild_id)
        userdata = list(users.find({'timezone': {'$exists': False}, 'discord_id': discord_id}))
        if len(userdata) > 0:
            embed = Embed(title="Please use the 'edit' command to update your timezone first.", color=0x000FF)
            await dm.send(embed=embed)
            return

        if self.db.check_manager(discord_id, guild_id):
            ops = []
            records = self.db.get_employee_records(guild_id)
            for employee in records.find():
                name = employee['name_first'] + " " + employee['name_last']
                ops.append(SelectOption(label=name, value=employee['discord_id']))
            embed = Embed(title="Who would you like to edit?", color=0x000FF)
            await dm.send("", embed=embed, components=[
                Select(
                    placeholder='Select a user',
                    options=ops,
                    custom_id='user'
                )
            ])

            user_choice = await self.client.wait_for(
                "select_option", check=lambda i: i.custom_id == "user" and i.user == ctx.author)
            discord_id = user_choice.values[0]
            await self.clear_last_msg(dm)
            await self.clear_last_msg(dm)

        # check if discord user has completed shifts to edit
        if not self.db.check_complete(discord_id, guild_id) and not self.db.check_manager(discord_id, guild_id):
            embed = Embed(title="You do not have any completed shifts to edit.", color=0x000FF)
            await dm.send(embed=embed)
            return

        # get timezone
        userdata = users.find_one({'discord_id': discord_id})
        timezone = userdata['timezone']
        tzp = pytz.timezone(timezone)

        # get 14 most recent completed shifts table associated with ctx author
        records = self.db.get_complete_shifts(guild_id)
        shifts = records.find({'discord_id': discord_id})
        shift_data = []
        for shift in shifts:
            # format shift data, create SelectOption,
            # append to list of options (key based on seconds from epoch of in_time)
            intime = shift["in_time"]
            outtime = shift["out_time"]
            tz = pytz.timezone("UTC")
            utcin = tz.localize(intime)
            utcout = tz.localize(outtime)
            instr = utcin.astimezone(tzp).strftime("%I:%M %p")
            outstr = utcout.astimezone(tzp).strftime("%I:%M %p on %A %B %d")
            shift_data.append(SelectOption(label=instr + ' to ' + outstr, value=str(shift["in_time"].timestamp())))

        recent_14 = shift_data[-14:]
        # build a Select to choose a shift for user to edit and send in dms
        embed = Embed(title="Which shift would you like to edit?", color=0x000FF)
        await dm.send("", embed=embed, components=[
            Select(
                placeholder="Shifts",
                options=recent_14,
                custom_id='shift'
            )
        ])
        # await response
        shiftans = await self.client.wait_for(
            "select_option", check=lambda i: i.custom_id == "shift" and i.user == ctx.author)

        # use seconds from epoch of chosen option, convert back to date time, use this to search for associated out time
        in_time_raw = datetime.fromtimestamp(float(shiftans.values[0]))
        out_data = records.find_one({"in_time": in_time_raw, 'discord_id': discord_id})
        out_time_raw = out_data["out_time"]
        tz = pytz.timezone("UTC")
        in_time = tz.localize(in_time_raw)
        out_time = tz.localize(out_time_raw)

        # clear spent Select
        await self.clear_last_msg(dm)

        # build a Select to chose to edit the in time or the out time of the chosen shift
        embed = Embed(title="Which would you like to edit?", color=0x000FF)
        await dm.send("", embed=embed, components=[
            Select(
                placeholder="In or Out",
                options=[
                    SelectOption(
                        label="In: " + str(in_time.astimezone(tzp).strftime('%I:%M %p on %A %B %d')),
                        value="in"
                    ),
                    SelectOption(
                        label="Out: " + str(out_time.astimezone(tzp).strftime('%I:%M %p on %A %B %d')),
                        value="out"
                    )
                ],
                custom_id='inout'
            )
        ])
        # await response
        choice1 = await self.client.wait_for(
          "select_option", check=lambda i: i.custom_id == "inout" and i.user == ctx.author)

        # clear spent Select
        await self.clear_last_msg(dm)

        # display the datetime selected for editing
        if choice1.values[0] == "in":
            dt_change = in_time
            embed = Embed(title="You are editing the in time (" +
                str(in_time.astimezone(tzp).strftime('%I:%M:%S %p on %A %B %d')) + ")", color=0x000FF)
            await dm.send(embed=embed)
        else:
            dt_change = out_time
            embed = Embed(title="You are editing the out time (" +
                str(out_time.astimezone(tzp).strftime('%I:%M:%S %p on %A %B %d')) + ")", color=0x000FF)
            await dm.send(embed=embed)

        # begin while loop that allows for user verification and re-trial before final submittion
        try_again = True
        while try_again:
            # build SelectOptions for 24 hours of values starting from the in or out associated with the 
            # selected entry 
            ops = []

            if choice1.values[0] == "in":
                for x in range(24):
                    val = out_time - timedelta(hours=x)
                    out = val.astimezone(tzp).strftime('%I %p')
                    if not out_time.astimezone(tzp).strftime('%d') == val.astimezone(tzp).strftime('%d'):
                        out = out + " (previous day)"
                    ops.append(SelectOption(label=out, value=str(x)))
            else:
                for x in range(24):
                    val = in_time + timedelta(hours=x)
                    in_val = val.astimezone(tzp).strftime('%I %p')
                    if not in_time.astimezone(tzp).strftime('%d') == val.astimezone(tzp).strftime('%d'):
                        in_val = in_val + " (next day)"
                    ops.append(SelectOption(label=in_val, value=str(x)))

            # build and send hours Select
            embed = Embed(title="Select an hour for this time entry.", color=0x000FF)
            await dm.send("", embed=embed, components=[
                Select(
                    placeholder="Hours",
                    options=ops,
                    custom_id='hours'
                )
            ])
            # await response
            hours_interaction = await self.client.wait_for(
              "select_option", check=lambda i: i.custom_id == "hours" and i.user == ctx.author)
            hoursint = int(hours_interaction.values[0])
            if choice1.values[0] == "in":
                hourstr = (out_time.astimezone(tzp) - timedelta(hours=hoursint)).strftime('%I')
            else:
                hourstr = (in_time.astimezone(tzp) + timedelta(hours=hoursint)).strftime('%I')

            # clear spend Select
            await self.clear_last_msg(dm)

            # Build and send minutes Select with hours from previous answer displayed for clarity
            embed = Embed(title="Select a minute value for this time entry.", color=0x000FF)
            await dm.send("", embed=embed, components=[
                Select(
                    placeholder="Minutes",
                    options=[
                        SelectOption(label=hourstr + ":00", value=0),
                        SelectOption(label=hourstr + ":15", value=15),
                        SelectOption(label=hourstr + ":30", value=30),
                        SelectOption(label=hourstr + ":45", value=45)
                    ],
                    custom_id='minutes'
                )
            ])

            minutes_interaction = await self.client.wait_for(
              "select_option", check=lambda i: i.custom_id == "minutes" and i.user == ctx.author)
            # create new datetime value with users responses
            hours = int(hours_interaction.values[0])
            minutes = int(minutes_interaction.values[0])
            if choice1.values[0] == "in":
                new_dt = out_time - timedelta(hours=hours)
                new_dt = new_dt.replace(minute=minutes, second=0, microsecond=0)
            else:
                new_dt = in_time + timedelta(hours=hours)
                new_dt = new_dt.replace(minute=minutes, second=0, microsecond=0)

            # clear spend Select
            await self.clear_last_msg(dm)
            # verify new datetime is correct
            title = new_dt.astimezone(tzp).strftime('%I:%M:%S %p') + "\nIs this correct?"
            embed = Embed(title=title, color=0x000FF)
            await dm.send("", embed=embed, components=[
                Button(label="Yes", style="3", custom_id="send"),
                Button(label="No", style="4", custom_id="again"),
                Button(label="Cancel", style="2", custom_id="exit")
            ])

            # await response
            choice = await self.client.wait_for(
              "button_click", check=lambda i: i.custom_id == "send" or "again" or "exit")
            # clear spent Buttons
            await self.clear_last_msg(dm)
            await self.clear_last_msg(dm)

            # break loop if user confirms verification
            if choice.component.custom_id == "exit":
                embed = Embed(title="Timeclock edit canceled.", color=0x000FF)
                await dm.send(embed)
                return

            elif choice.component.custom_id == "send":
                if self.db.check_timestamp_collision_change(new_dt, in_time, out_time, discord_id, guild_id):
                    embed = Embed(title="This new time would collide with a previous entry in your timesheet", color=0x000FF)
                    await dm.send(embed)
                    continue

                try_again = False

                # select in or out
                if choice1.values[0] == "in":
                    # verify replacement does not cause in_time to come after out_time resulting in negative hours
                    if new_dt.astimezone(tzp) > out_time.astimezone(tzp):
                        embed = Embed(title="This would result in your in time coming after your out time. \
                            Please try again with a valid in time.", color=0x000FF)
                        await dm.send(embed)
                        # restart loop
                        try_again = True
                        continue

                    # if manager bypass verification
                    if self.db.check_manager(str(ctx.author), guild_id):
                        total = out_time.astimezone(tzp) - new_dt.astimezone(tzp)
                        seconds = total.seconds
                        new_val = {"$set": {'in_time': new_dt, 'seconds_worked': seconds}}
                        records.update_one({'discord_id': discord_id, 'out_time': out_time}, new_val)
                        embed = Embed(title="You have updated this entry!", color=0x000FF)
                        await dm.send(embed)

                    else:
                        # open dm with boss for verification
                        emp_name = self.db.get_employee_records(guild_id).find_one({"discord_id": discord_id})
                        name = emp_name["name_first"] + " " + emp_name["name_last"]
                        boss_dm = await ctx.guild.owner.create_dm()
                        await boss_dm.send(name + " would like to change a shift on " + new_dt.strftime('%A %B %d'))
                        await boss_dm.send(
                          "Old shift: " +
                          str(
                              dt_change.astimezone(tzp).strftime('%I:%M:%S %p')
                              + " to " +
                              out_time.astimezone(tzp).strftime('%I:%M:%S %p')
                          )
                        )
                        await boss_dm.send(
                          "New shift: " +
                          str(
                              new_dt.astimezone(tzp).strftime('%I:%M:%S %p') +
                              " to " +
                              out_time.astimezone(tzp).strftime('%I:%M:%S %p')
                          )
                        )
                        await boss_dm.send("Would you like to allow this?", components=[
                            Button(label="Yes", style="3", custom_id="yes"),
                            Button(label="No", style="4", custom_id="no")
                        ])
                        # await response
                        await dm.send("Please wait while we aprove this with your boss.")
                        boss_choice = await self.client.wait_for(
                          "button_click", check=lambda i: i.custom_id == "yes" or "no")
                        # clear spent Buttons
                        await self.clear_last_msg(boss_dm)
                        if boss_choice.component.custom_id == "yes":
                            await boss_dm.send("Thank you, I will let " + name + " know their shift has been changed!")
                            await self.post_mng_log(
                                ctx,
                                ctx.guild.owner.name +
                                " has aproved a time clock change for " +
                                name)
                            await self.post_mng_log(
                                ctx,
                                "Old shift: " +
                                str(
                                    dt_change.astimezone(tzp).strftime('%I:%M:%S %p') +
                                    " to " +
                                    out_time.astimezone(tzp).strftime('%I:%M:%S %p'))
                                )
                            await self.post_mng_log(
                                ctx,
                                "New shift: " +
                                str(
                                    new_dt.astimezone(tzp).strftime('%I:%M:%S %p') +
                                    " to " +
                                    out_time.astimezone(tzp).strftime('%I:%M:%S %p')
                                )
                            )
                        else:
                            await boss_dm.send("Thank you, I will let " + name + " know their shift has not \
                                  been changed and to contact you if they have any questions as to why.")
                            await dm.send("Your boss has declined your timeclock change. Please contact them \
                                  if you have any concerns as to why.")
                            return

                        # update record with new in_time datetime and total seconds of the shift
                        total = out_time.astimezone(tzp) - new_dt.astimezone(tzp)
                        seconds = total.seconds
                        new_val = {"$set": {'in_time': new_dt, 'seconds_worked': seconds}}
                        records.update_one({'discord_id': discord_id, 'out_time': out_time}, new_val)
                        # post verfication in dm
                        await dm.send(
                            "Your boss has confirmed your timeclock change on " +
                            str(new_dt.strftime('%A %B %d'))
                        )
                        await dm.send(
                            "Old shift: " +
                            str(
                                dt_change.astimezone(tzp).strftime('%I:%M:%S %p') +
                                " to " +
                                out_time.astimezone(tzp).strftime('%I:%M:%S %p')
                            )
                        )
                        await dm.send(
                            "New shift: " +
                            str(
                                new_dt.astimezone(tzp).strftime('%I:%M:%S %p') +
                                " to " +
                                out_time.astimezone(tzp).strftime('%I:%M:%S %p')
                            )
                        )

                elif choice1.values[0] == "out":
                    if in_time.astimezone(tzp) > new_dt.astimezone(tzp):
                        embed = Embed(title="This would result in your in time coming after your out time. \
                        Please try again with a valid in time.", color=0x000FF)
                        await dm.send(embed)
                        # restart loop
                        try_again = True
                        continue
                    # if manager bypass verification
                    if self.db.check_manager(str(ctx.author), guild_id):
                        total = new_dt - in_time
                        seconds = total.seconds
                        new_val = {"$set": {'out_time': new_dt, 'seconds_worked': seconds}}
                        records.update_one({'discord_id': discord_id, 'in_time': in_time}, new_val)
                        embed = Embed(title="You have updated this entry!", color=0x000FF)
                        await dm.send(embed)

                    else:
                        # open dm with boss for verification
                        emp_name = self.db.get_employee_records(guild_id).find_one({"discord_id": discord_id})
                        name = emp_name["name_first"] + " " + emp_name["name_last"]
                        boss_dm = await ctx.guild.owner.create_dm()
                        await boss_dm.send(name + " would like to change a shift on " + new_dt.strftime('%A %B %d'))
                        await boss_dm.send(
                            "Old shift: " + in_time.astimezone(tzp).strftime('%I:%M:%S %p') +
                            " to " + dt_change.astimezone(tzp).strftime('%I:%M:%S %p'))
                        await boss_dm.send(
                            "New shift: " + in_time.astimezone(tzp).strftime('%I:%M:%S %p') +
                            " to " + new_dt.astimezone(tzp).strftime('%I:%M:%S %p'))
                        await boss_dm.send("Would you like to allow this?", components=[
                            Button(label="Yes", style="3", custom_id="yes"),
                            Button(label="No", style="4", custom_id="no")
                        ])
                        # await response
                        await dm.send("Please wait while we aprove this with your boss.")
                        boss_choice = await self.client.wait_for(
                          "button_click", check=lambda i: i.custom_id == "yes" or "no")
                        # clear spent Buttons
                        await self.clear_last_msg(boss_dm)
                        if boss_choice.component.custom_id == "yes":
                            await boss_dm.send("Thank you, I will let " + name + " know their shift has been changed!")
                        else:
                            await boss_dm.send(
                                "Thank you, I will let " + name + " know their shift has not \
                                been changed and to contact you if they have any questions as to why.")
                            await dm.send(
                                "Your boss has declined your timeclock change. Please contact them \
                                if you have any concerns as to why.")
                            return

                        # update record with new out_time datetime and total seconds of the shift
                        total = new_dt - in_time
                        seconds = total.seconds
                        new_val = {"$set": {'out_time': new_dt, 'seconds_worked': seconds}}
                        records.update_one({'discord_id': discord_id, 'in_time': in_time}, new_val)
                        # post verfication in dm
                        await dm.send(
                            "You have edited your out time on " +
                            str(new_dt.astimezone(tzp).strftime('%A %B %d')))
                        await dm.send(
                            "Old shift: " + in_time.astimezone(tzp).strftime('%I:%M:%S %p') +
                            " to " + str(dt_change.astimezone(tzp).strftime('%I:%M:%S %p')))
                        await dm.send(
                            "New shift: " + in_time.astimezone(tzp).strftime('%I:%M:%S %p') +
                            " to " + str(new_dt.astimezone(tzp).strftime('%I:%M:%S %p')))
                        await self.post_mng_log(
                            ctx, ctx.guild.owner.name + " has aproved a time clock change for " + name)
                        await self.post_mng_log(
                            ctx, "Old shift: " + in_time.astimezone(tzp).strftime('%I:%M:%S %p') +
                            " to " + str(dt_change.astimezone(tzp).strftime('%I:%M:%S %p')))
                        await self.post_mng_log(
                            ctx, "New shift: " + in_time.astimezone(tzp).strftime('%I:%M:%S %p') +
                            " to " + str(new_dt.astimezone(tzp).strftime('%I:%M:%S %p')))

    @commands.command(name='time')
    async def printtime(self, ctx):
        # allows user to see all of their time data. well eventually be depricated to data command
        # check if command is not in direct messages
        if await self.guild_null(ctx):
            return
        # open dm channel
        dm = await ctx.author.create_dm()
        # get guild id
        guild_id = str(ctx.guild.id)
        # get completed shifts table
        records = self.db.get_complete_shifts(guild_id)
        # get timezone
        discord_id = str(ctx.author)
        users = self.db.get_employee_records(guild_id)
        userdata = users.find_one({'discord_id': discord_id})
        timezone = userdata['timezone']
        tzp = pytz.timezone(timezone)
        utc = pytz.timezone('UTC')
        # get shifts associated with author of ctx
        shifts = records.find({'discord_id': discord_id})
        total = 0
        shift_data = []
        for shift in shifts:
            # localize times to utc, convert to user timezone, format
            in_time = utc.localize(shift["in_time"])
            out_time = utc.localize(shift["out_time"])
            instr = in_time.astimezone(tzp).strftime('%A %m-%d-%Y from %I:%M %p')
            outstr = out_time.astimezone(tzp).strftime("%I:%M %p on %A %m-%d")
            # get total seconds, minutes, hours in shift
            s = int(shift["seconds_worked"])
            hours, remainder = divmod(s, 3600)
            minutes, seconds = divmod(remainder, 60)
            # add seconds to running total
            total += s
            # format shift data
            data = '{:02}:{:02}:{:02}'.format(int(hours), int(minutes), int(seconds))
            # append shift data
            shift_data.append(str(data + ' on ' + instr + ' to ' + outstr))

        # send shift information in dm
        for shift in shift_data:
            await dm.send(shift)

        # calculate and send total time based on running total of seconds.
        hours, remainder = divmod(total, 3600)
        minutes, seconds = divmod(remainder, 60)
        total_time = '{:02}:{:02}:{:02}'.format(int(hours), int(minutes), int(seconds))
        await dm.send("Total time: " + total_time)

    @commands.command(name='clean')
    async def clean(self, ctx):
        # development command that has the bot delete its messages in ctx authors dm's
        dm = await ctx.author.create_dm()
        async for x in dm.history(limit=1000):
            if x.author == self.client.user:
                await x.delete()

    @commands.command(name='data')
    async def data(self, ctx):
        # command that sends a manager a CSV file of all timeclock data between two chosen dates
        guild_id = ctx.guild.id
        user_id = str(ctx.author)

        # manager only command
        if not self.db.check_manager(user_id, guild_id):
            return
        dm = await ctx.author.create_dm()
        option_start = self.db.get_oldest_shift(guild_id)
        option_in = option_start["in_time"].replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        option_end = datetime.now().replace()

        # get starting month
        ops = []
        while option_in < option_end:
            lbl = option_in.strftime("%B, %Y")
            val = option_in.strftime("%m %Y")
            ops.append(SelectOption(label=lbl, value=val))
            option_in = option_in + relativedelta(months=+1)
        await dm.send("Select a starting month", components=[
            Select(
                placeholder="Month",
                options=ops,
                custom_id='Month'
            )
        ])
        start_interaction = await self.client.wait_for(
          "select_option", check=lambda i: i.custom_id == "Month" and i.user == ctx.author)
        await self.clear_last_msg(dm)
        ppstart = start_interaction.values[0]
        start_split = ppstart.split(" ")
        start_month = start_split[0]
        start_year = start_split[1]
        start = datetime(
            year=int(start_year), month=int(start_month),
            day=1, hour=0, minute=0, second=0, microsecond=0)

        # get starting day
        ops = []

        while int(start.strftime("%d")) < 20:
            lbl = start.strftime("%A the %d")
            val = start.strftime("%d")
            ops.append(SelectOption(label=lbl, value=val))
            start = start + relativedelta(days=+1)
        ops.append(SelectOption(label="More", value="More"))
        await dm.send("Select a starting day", components=[
            Select(
                placeholder="Day",
                options=ops,
                custom_id='Day'
            )
        ])
        start_day_interaction = await self.client.wait_for(
          "select_option", check=lambda i: i.custom_id == "Day" and i.user == ctx.author)
        await self.clear_last_msg(dm)
        day = start_day_interaction.values[0]
        if day == "More":
            ops = []
            while start.strftime("%m") == start_month:
                lbl = start.strftime("%A the %d")
                val = start.strftime("%d")
                ops.append(SelectOption(label=lbl, value=val))
                start = start + relativedelta(days=+1)
            await dm.send("Select a starting day", components=[
                Select(
                    placeholder="Day",
                    options=ops,
                    custom_id='Day'
                )
            ])
            start_day_interaction = await self.client.wait_for(
              "select_option", check=lambda i: i.custom_id == "Day" and i.user == ctx.author)
            await self.clear_last_msg(dm)
            day = start_day_interaction.values[0]

        ppstart = datetime(
            year=int(start_year), month=int(start_month),
            day=int(day), hour=0, minute=0, second=0, microsecond=0)
        start = datetime(
            year=int(start_year), month=int(start_month),
            day=1, hour=0, minute=0, second=0, microsecond=0)
        ops = []
        while start < option_end:
            lbl = start.strftime("%B, %Y")
            val = start.strftime("%m %Y")
            ops.append(SelectOption(label=lbl, value=val))
            start = start + relativedelta(months=1)

        await dm.send("Select an ending month", components=[
            Select(
              placeholder="Month",
              options=ops,
              custom_id='Month'
              )
          ])
        end_interaction = await self.client.wait_for(
            "select_option", check=lambda i: i.custom_id == "Month" and i.user == ctx.author)
        await self.clear_last_msg(dm)

        ppend = end_interaction.values[0]
        end_split = ppend.split(" ")
        end_month = end_split[0]
        end_year = end_split[1]
        start = datetime(
            year=int(end_year), month=int(end_month),
            day=1, hour=0, minute=0, second=0, microsecond=0)
        if end_month == start_month:
            start = start.replace(day=int(day))

        # get ending day
        ops = []
        while len(ops) < 20 and start.strftime("%m") == end_month:
            lbl = start.strftime("%A the %d")
            val = start.strftime("%d")
            ops.append(SelectOption(label=lbl, value=val))
            start = start + relativedelta(days=+1)
        if start.strftime("%m") == end_month:
            ops.append(SelectOption(label="More", value="More"))
        await dm.send("Select an ending day", components=[
            Select(
                placeholder="Day",
                options=ops,
                custom_id='Day'
            )
        ])
        end_day_interaction = await self.client.wait_for(
            "select_option", check=lambda i: i.custom_id == "Day" and i.user == ctx.author)
        await self.clear_last_msg(dm)
        day = end_day_interaction.values[0]
        if day == "More":
            ops = []
            while start.strftime("%m") == end_month:
                lbl = start.strftime("%A the %d")
                val = start.strftime("%d")
                ops.append(SelectOption(label=lbl, value=val))
                start = start + relativedelta(days=+1)
            await dm.send("Select an ending day", components=[
                Select(
                    placeholder="Day",
                    options=ops,
                    custom_id='Day'
                )
            ])
            end_day_interaction = await self.client.wait_for(
                "select_option", check=lambda i: i.custom_id == "Day" and i.user == ctx.author)
            await self.clear_last_msg(dm)
            day = end_day_interaction.values[0]

        ppend = datetime(
            year=int(end_year), month=int(end_month),
            day=int(day), hour=23, minute=59, second=59, microsecond=0)
        records = self.db.get_employee_records(guild_id)
        shifts = self.db.get_complete_shifts(guild_id)
        slice = shifts.find({"in_time": {"$gt": ppstart}, "in_time": {"$lt": ppend}})
        data = {}
        for entry in slice:
            user = records.find_one({'discord_id': entry["discord_id"]})
            name = user["name_last"] + ", " + user["name_first"]
            if name not in data.keys():
                data[name] = 0
            data[name] = data[name] + entry["seconds_worked"]

        # open the file in the write mode
        title = 'csv/' + ppstart.strftime('%m-%dto') + ppend.strftime('%m-%d-%Y') + '.csv'
        with open(title, 'w') as file:
            # create the csv writer
            writer = csv.writer(file)
            ppst = ['Pay Period Start:', ppstart.strftime('%A %B %d %Y')]
            ppnd = ['Pay Period End:', ppend.strftime('%A %B %d %Y')]
            blank = ['', '']
            header = ['Employee Name', 'Hours Worked']
            rows = [ppst, ppnd, blank, header]
            # write a row to the csv file
            writer.writerows(rows)
            for name, seconds in sorted(data.items()):
                minutes = float(seconds) / 60
                hours = round(float(minutes) / 60, 4)
                row = [str(name), hours]
                writer.writerow(row)
        await dm.send("Creating and Sending timeclock file.")
        await dm.send(file=File(title))
        os.remove(title)

    async def clear_last_msg(self, channel):
        # clears the last message the bot sent in channel
        async for x in channel.history(limit=1):
            await x.delete()

    async def ten_hour_check(self, ctx):
        # helper function that attempts to clock out user 10 hours after they clock in. Then every 2 hours after that
        sleep_time = 36000
        second_sleep_time = 7200
        discord_id = str(ctx.author)
        guild_id = str(ctx.guild.id)
        while True:
            await asyncio.sleep(sleep_time)

            if not self.db.check_in(discord_id, guild_id):
                return

            dm = await ctx.author.create_dm()
            await dm.send("You have been clocked in for a long time. Is this intentional?", components=[
                  Button(label="No", style="4", custom_id="out"),
                  Button(label="Yes", style="3", custom_id="remain")
            ])

            # await response
            try:
                ans = await self.client.wait_for(
                    "button_click", timeout=300, check=lambda i: i.custom_id == "out" or "remain")
                await self.clear_last_msg(dm)
                if ans.component.custom_id == "remain":
                    sleep_time = second_sleep_time
                    continue
                else:
                    break
            except asyncio.TimeoutError:
                await self.clear_last_msg(dm)
                break

        self.db.clock_user_out(discord_id, guild_id)
        await dm.send(
            "You were clocked out due to the bot suspecting you forgot to clock out. \
             \nPlease edit this shift to correct your time sheet.")

    async def get_mng_log(self, ctx):
        # get channel object for manager log
        await self.create_mng_log(ctx)
        for channel in await ctx.guild.fetch_channels():
            if channel.name == "timeclock-manager-log":
                return channel

    async def post_mng_log(self, ctx, msg):
        # post to the manager log
        mng_log = await self.get_mng_log(ctx)
        await mng_log.send(msg)

    async def post_mng_log_embed(self, ctx, embed):
        # post an embed to the manager log
        mng_log = await self.get_mng_log(ctx)
        await mng_log.send(embed=embed)

    async def create_mng_log(self, ctx):
        # attempt to create manager log
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


def setup(client):
    client.add_cog(timeclock(client))