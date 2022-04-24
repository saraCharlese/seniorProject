from datetime import datetime
import pymongo
import pytz


class connect_to_db():
    def __init__(self):
        # connect to mongoDB
        self.client = pymongo.MongoClient(
            "mongodb+srv://Danny:qwert123@cluster0.tx7kv.mongodb.net/Cluster0?retryWrites=true&w=majority")

    def get_employee_records(self, guild_id):
        return self.client.get_database(str(guild_id)).employee_records

    def get_active_shifts(self, guild_id):
        return self.client.get_database(str(guild_id)).active_shifts

    def get_complete_shifts(self, guild_id):
        return self.client.get_database(str(guild_id)).complete_shifts

    def get_oldest_shift(self, guild_id):
        shifts = self.get_complete_shifts(guild_id)
        slice = shifts.find_one(sort=[("in_time", 1)])
        return slice

    def get_afk(self, guild_id):
        return self.client.get_database(str(guild_id)).afk

    def add_user(self, discord_id, first_name, last_name, timezone, guild_id, member_id):
        # create employee dict
        if not self.check_active(discord_id, guild_id):
            new_employee = {
                'discord_id': discord_id,
                'member_id': member_id,
                'name_first': first_name,
                'name_last': last_name,
                'timezone': timezone,
                'manager': False
            }
            records = self.client.get_database(str(guild_id)).employee_records
            records.insert_one(new_employee)

    def check_timestamp_collision_change(self, utc_timestamp, in_time, out_time, discord_id, guild_id):
        records = self.get_complete_shifts(guild_id)
        user_records = records.find({'discord_id': discord_id})
        utc_timestamp = utc_timestamp.replace(tzinfo=None)
        for record in user_records:
            if record['in_time'].strftime('%m:%d:%Y-%H:%M:%S:%f') == in_time.strftime('%m:%d:%Y-%H:%M:%S:%f') and \
                    record['out_time'].strftime('%m:%d:%Y-%H:%M:%S:%f') == out_time.strftime('%m:%d:%Y-%H:%M:%S:%f'):
                continue
            if utc_timestamp >= record['in_time'] and utc_timestamp <= record['out_time']:
                return True

        ins = self.get_active_shifts(guild_id)
        user_ins = ins.find({'discord_id': discord_id})
        for record in user_ins:
            if utc_timestamp >= record['in_time']:
                return True

        return False

    
    def check_timestamp_collision(self, utc_timestamp, discord_id, guild_id):
        records = self.get_complete_shifts(guild_id)
        user_records = records.find({'discord_id': discord_id})
        utc_timestamp = utc_timestamp.replace(tzinfo=None)
        for record in user_records:
            if utc_timestamp >= record['in_time'] and utc_timestamp <= record['out_time']:
                return True

        ins = self.get_active_shifts(guild_id)
        user_ins = ins.find({'discord_id': discord_id})
        for record in user_ins:
            if utc_timestamp >= record['in_time']:
                return True

        return False

    def delete_user(self, discord_id, guild_id):
        records = self.client.get_database(str(guild_id)).employee_records
        records.delete_one({'discord_id': discord_id})

    def check_in(self, user_id, guild_id):
        # checks if author of ctx is clocked in
        # get user discord id
        discord_id = str(user_id)
        records = self.client.get_database(str(guild_id)).active_shifts

        # check if discord user is already in the database
        slice = len(list(records.find({'discord_id': discord_id})))

        if slice > 0:
            return True

        return False

    def check_manager(self, user_id, guild_id):
        records = self.client.get_database(str(guild_id)).employee_records
        emp = records.find_one({'discord_id': user_id})
        val = emp['manager']
        return val

    def promote_manager(self, user_id, guild_id):
        records = self.client.get_database(str(guild_id)).employee_records
        records.update_one({'discord_id': user_id}, {"$set": {'manager': True}})

    def demote_manager(self, user_id, guild_id):
        records = self.client.get_database(str(guild_id)).employee_records
        records.update_one({'discord_id': user_id}, {"$set": {'manager': False}})

    def update_all_manager_values(self, guild_id):
        records = self.client.get_database(str(guild_id)).employee_records
        tars = records.find({'manager': {'$exists': False}})
        for employee in tars:
            records.update_one({'discord_id': employee['discord_id']}, {"$set": {'manager': False}})

    def clock_user_in(self, user_id, guild_id):
        if self.check_active(user_id, guild_id):
            if not self.check_in(user_id, guild_id):
                records = self.get_active_shifts(guild_id)
                in_time = datetime.now(tz=pytz.timezone('UTC'))
                new_entry = {
                    'discord_id': user_id,
                    'in_time': in_time
                }
                # store employee in the database
                records.insert_one(new_entry)
                return True
        return False

    def clock_user_out(self, user_id, guild_id):
        if self.check_in(user_id, guild_id):
            actives = self.get_active_shifts(guild_id)
            records = self.get_complete_shifts(guild_id)
            slice = actives.find_one({'discord_id': user_id})
            tz = pytz.timezone('UTC')
            in_time = tz.localize(slice['in_time'])
            out_time = datetime.now(tz=tz)
            total = out_time - in_time
            seconds = total.seconds

            data = {
                'discord_id': user_id,
                'in_time': in_time,
                'out_time': out_time,
                'seconds_worked': seconds,
                'comment': "",
                'paid': False
            }

            actives.delete_one({'discord_id': user_id})
            records.insert_one(data)
            return True
        return False

    def get_managers(self, guild_id):
        records = self.client.get_database(str(guild_id)).employee_records
        managers = records.find({'manager': True})
        return managers

    def check_active(self, user_id, guild_id):
        # checks if author of ctx is a registered user in this servers system
        # get user discord id
        discord_id = str(user_id)
        records = self.client.get_database(str(guild_id)).employee_records

        # check if discord user is already in the database
        slice = len(list(records.find({'discord_id': discord_id})))

        if slice > 0:
            return True

        return False

    def check_complete(self, user_id, guild_id):
        # checks if author of ctx has any completed shifts
        # get user discord id
        discord_id = str(user_id)
        records = self.client.get_database(str(guild_id)).complete_shifts

        # check if discord user is already in the database
        slice = list(records.find({'discord_id': discord_id}))

        if len(slice) > 0:
            return True

        return False

    def check_afk(self, guild_id, id):
        # checks if id has an afk message set in the guild of ctx
        afk = self.client.get_database(str(guild_id)).afk
        slice = list(afk.find({'discord_id': id}))

        if len(slice) > 0:
            return True

        return False