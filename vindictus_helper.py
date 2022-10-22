# encoding: utf-8
import random
import json

class polls:
    def __init__(self):
        self.data = dict()
        self.json = "polls.json"
        with open(self.json) as json_file:
            self.data = json.load(json_file)
        self.options = "options"
        self.vote_record = "voteRecord"
        self.lock = "lock"
        return

    def sync_json(self):
        with open(self.json, 'w') as json_file:
            json.dump(self.data, json_file)
        return

    def guild_init(self, guild_id):
        guild_id = str(guild_id)
        if(guild_id not in self.data):
            self.data[guild_id] = {}
            self.sync_json()
        return

    def poll_exist(self, guild_id, poll_name):
        return poll_name in self.data[guild_id]

    def vote_exist(self, guild_id, poll_name, user_name):
        return user_name in self.get_poll_vote_record(guild_id, poll_name)#####

    def get_polls_set(self, guild_id):
        guild_id = str(guild_id)
        return set(self.data[guild_id].keys())

    def get_poll_options(self, guild_id, poll_name):
        guild_id = str(guild_id)
        return set(self.data[guild_id][poll_name][self.options])

    def get_poll_vote_record(self, guild_id, poll_name):
        guild_id = str(guild_id)
        if(self.poll_exist(guild_id, poll_name)):
            return self.data[guild_id][poll_name][self.vote_record]
        return None

    def new_poll(self, guild_id, poll_name, poll_options):
        guild_id = str(guild_id)
        if(not self.poll_exist(guild_id, poll_name)):
            poll = {}
            poll[self.options] = { i : 0 for i in poll_options}
            poll[self.vote_record] = {}
            poll[self.lock] = False
            self.data[guild_id][poll_name] = poll
            self.sync_json()
            return 0
        return -1

    def del_poll(self, guild_id, poll_name):
        guild_id = str(guild_id)
        if(self.poll_exist(guild_id, poll_name)):
            del self.data[guild_id][poll_name]
            self.sync_json()
            return 0
        return -1

    def reset_poll(self, guild_id, poll_name):
        guild_id = str(guild_id)
        if(self.poll_exist(guild_id, poll_name)):
            poll = self.data[guild_id][poll_name]
            poll[self.options] = dict.fromkeys(poll[self.options], 0)
            poll[self.vote_record] = {}
            poll[self.lock] = False
            self.sync_json()
            return 0
        return -1

    def get_result_dict(self, guild_id, poll_name):
        guild_id = str(guild_id)
        if(self.poll_exist(guild_id, poll_name)):
            return self.data[guild_id][poll_name][self.options]
        return None

    def vote(self, guild_id, poll_name, user_name, choice):
        guild_id = str(guild_id)
        if(not self.poll_exist(guild_id, poll_name)):
            return -1
        poll = self.data[guild_id][poll_name]
        if(poll[self.lock]):
            return -2
        if(self.vote_exist(guild_id, poll_name, user_name)):
            old_choice = poll[self.vote_record][user_name]
            poll[self.options][old_choice] -= 1
        poll[self.vote_record][user_name] = choice
        poll[self.options][choice] += 1
        self.sync_json()
        return 0

    def lock_change(self, guild_id, poll_name, value):
        guild_id = str(guild_id)
        if(not self.poll_exist(guild_id, poll_name)):
            return -1
        poll = self.data[guild_id][poll_name]
        poll[self.lock] = value
        self.sync_json()
        return 0

    def lock_poll(self, guild_id, poll_name):
        return self.lock_change(guild_id, poll_name, True)

    def unlock_poll(self, guild_id, poll_name):
        return self.lock_change(guild_id, poll_name, False)





class events:
    def __init__(self):
        self.data = dict()
        self.json = "events.json"
        with open(self.json) as json_file:
            self.data = json.load(json_file)
        self.fixed_events = set(["絕命戰", "時空扭曲"])
        return

    def sync_json(self):
        with open(self.json, 'w') as json_file:
            json.dump(self.data, json_file)
        return

    def guild_init(self, guild_id):
        guild_id = str(guild_id)
        if(guild_id not in self.data):
            self.data[guild_id] = {}
            for key in self.fixed_events:
                self.data[guild_id][key] = {}
            self.sync_json()
        return

    def event_exist(self, guild_id, event_name):
        return event_name in self.data[guild_id]

    def deletable_event(self, guild_id, event_name):
        return event_name not in self.fixed_events

    def user_exist(self, guild_id, event_name, user_name):
        return user_name in self.get_event_registered_dict(guild_id, event_name)

    def get_events_set(self, guild_id):
        guild_id = str(guild_id)
        return set(self.data[guild_id].keys())

    def new_event(self, guild_id, event_name):
        guild_id = str(guild_id)
        if(not self.event_exist(guild_id, event_name)):
            self.data[guild_id][event_name] = {}
            self.sync_json()
            return 0
        return -1

    def del_event(self, guild_id, event_name):
        guild_id = str(guild_id)
        if(self.deletable_event(guild_id, event_name) and self.event_exist(guild_id, event_name)):
            del self.data[guild_id][event_name]
            self.sync_json()
            return 0
        return -1

    def reset_event(self, guild_id, event_name):
        guild_id = str(guild_id)
        if(self.event_exist(guild_id, event_name)):
            self.data[guild_id][event_name] = {}
            self.sync_json()
            return 0
        return -1

    def get_event_registered_dict(self, guild_id, event_name):
        guild_id = str(guild_id)
        try:
            return self.data[guild_id][event_name]
        except:
            return None

    def register(self, guild_id, event_name, user_name):
        guild_id = str(guild_id)
        event_registered_dict = self.get_event_registered_dict(guild_id, event_name)
        if(not self.user_exist(guild_id, event_name, user_name)):
            event_registered_dict[user_name] = None
            self.sync_json()
            return 0
        return -1

    def unregister(self, guild_id, event_name, user_name):
        guild_id = str(guild_id)
        if(self.user_exist(guild_id, event_name, user_name)):
            event_registered_dict = self.get_event_registered_dict(guild_id, event_name)
            del event_registered_dict[user_name]
            self.sync_json()
            return 0
        return -1





class partyBuilder:

    @staticmethod
    def build_list(args):
        members = args.split("-")
        whole_list = []
        for item in members:
            whole_list.append(item.split())
        team_num = int(whole_list[0][0])
        return team_num, whole_list[1::]

    @staticmethod
    def capybara_adder(member_list):
        for i in range(len(member_list)):
            for j in range(len(member_list[i])):
                if("水豚" not in member_list[i][j]):
                    member_list[i][j] = "水豚" + member_list[i][j]
        return

    @staticmethod
    def leader_fix(team_num, member_list):
        partyBuilder.capybara_adder(member_list)
        leader_choice = member_list[0]
        del member_list[0]
        leader_list = []
        if(team_num > len(leader_choice)):
            return None
        else:
            random.shuffle(leader_choice)
        leader_list = leader_choice[0:team_num]

        member_list[0] = member_list[0] + leader_choice[team_num::]
        return leader_list

    @staticmethod
    def distribute(leader_list, member_list):
        team_num = len(leader_list)
        team_composition = [[leader_list[i]] for i in range(team_num)]
        put_flag = 0

        for i in range(len(member_list)):
            random.shuffle(member_list[i])

        for pool in member_list:
            for member in pool:
                if((put_flag // team_num) % 2 == 0):
                    team_composition[put_flag % team_num].append(member)
                else:
                    team_composition[0 - (put_flag % team_num + 1)].append(member)
                put_flag += 1
        return team_composition

    @staticmethod
    def out_string(team_composition):
        ret = ""
        for team in team_composition:
            ret += (f"隊長: {team[0]}\n隊員: {' '.join(team[1::])}\n\n")
        return ret

