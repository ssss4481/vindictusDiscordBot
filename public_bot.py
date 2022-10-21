# encoding: utf-8
########################################
# Author: Andrew Chen (github: ssss4481)
# Date: 2022/10/21
# Contact: ssss4480@gmail.com
########################################

import random
import time
import datetime

import discord
from discord.commands import option

import vindictus_helper as vt


random.seed(int(time.time()))


bot = discord.Bot()

events = vt.events()
polls = vt.polls()


#print(data_base.data)
async def except_handler(ctx):
    await ctx.respond(f"發生錯誤 請聯絡水豚俠")

@bot.event
async def on_ready():
    print(f"{datetime.datetime.now()}:{bot.user} is ready and online!")


@bot.slash_command(name = "抽一個", description = "args:選項1 選項2 選項3...(記得用空格分開選項)")
async def random_choice(ctx, args):
    try:
        choice = args.strip().split()
        await ctx.respond(f"選項:{args}\n被抽到的是:{choice[random.randint(0, len(choice)-1)]}")
    except:
        await except_handler(ctx)

@bot.slash_command(name = "附魔模擬器", description = "輸入成功機率%數(整數 後面不要加百分比符號 例如30%就輸入30)")
async def capy_hater(ctx, probability):
    threshold = int(probability)
    num = random.randint(1, 100)
    if(num <= threshold):
        await ctx.respond(f"成功機率{threshold}%，成功")
    else:
        await ctx.respond(f"成功機率{threshold}%，失敗")

@bot.slash_command(name="資料初始化", description= "初次使用資料紀錄功能前請執行此指令，再次執行不會重置資料")
async def data_init(ctx):
    global events
    global polls
    try:
        events.guild_init(ctx.guild_id)
        polls.guild_init(ctx.guild_id)
        await ctx.respond("初始化完成")
    except:
        print(f"{datetime.datetime.now()}team_builder with: {ctx.guild_id}")
        await except_handler(ctx)


team_build_usage = "隊伍數量 - 隊長池 - 隊員池1 - 隊員池2 - 隊員池3 -... - 隊員池n\n各池的隊員請用半形空白分格\n隊長池中未獲選為隊長者\n目前預設放入第1池。"
@bot.slash_command(name = "分隊", description = team_build_usage)
async def team_build(ctx, args):
    try:
        team_num, member_list = vt.partyBuilder.build_list(args)
        leader_list = vt.partyBuilder.leader_fix(team_num, member_list)
        if(leader_list == None):
            await ctx.respond(f"發生錯誤，請檢查設定的隊伍數量是不是比提供的隊長還多，或者聯絡水豚俠。\n 使用方法:{team_build_usage}")
            return
        team_composition = vt.partyBuilder.distribute(leader_list, member_list)
        output = vt.partyBuilder.out_string(team_composition)
        await ctx.respond(output)
    except:
        await except_handler(ctx)

###############################################
#####################event#####################
async def get_all_events_options(ctx: discord.AutocompleteContext):
    global events
    return sorted(list(events.get_events_set(ctx.interaction.guild_id)))

async def get_deletable_events_options(ctx: discord.AutocompleteContext):
    global events
    sets = events.get_events_set(ctx.interaction.guild_id)
    for fixed_event in events.fixed_events:
        sets.remove(fixed_event)
    return sorted(list(sets))

@bot.slash_command(name="新增活動")
async def new_event(ctx, event_name):
    global events
    try:
        ret = events.new_event(ctx.guild_id, event_name)
        if(ret == 0):
            await ctx.respond(f"活動\"{event_name}\"新增成功。")
        elif(ret == -1):
            await ctx.respond(f"活動\"{event_name}\"新增失敗，可能是存在同名活動，請確認後再次新增。")
    except:
        await except_handler(ctx)
    return

@bot.slash_command(name="刪除活動")
@option("event_name", description="選擇欲刪除的活動", autocomplete=get_deletable_events_options)
async def del_event(ctx: discord.AutocompleteContext,
                    event_name):
    global events
    try:
        ret = events.del_event(ctx.guild_id, event_name)
        if(ret == 0):
            await ctx.respond(f"活動\"{event_name}\"刪除成功。")
        elif(ret == -1):
            await ctx.respond(f"活動\"{event_name}\"並不存在，無法刪除。")
    except:
        await except_handler(ctx)
    return

@bot.slash_command(name="重置活動")
@option("event_name", description="選擇欲重置的活動", autocomplete=get_all_events_options)
async def reset_event(ctx: discord.AutocompleteContext,
                    event_name):
    global events
    try:
        ret = events.reset_event(ctx.guild_id, event_name)
        if(ret == 0):
            await ctx.respond(f"活動\"{event_name}\"重置成功。")
        elif(ret == -1):
            await ctx.respond(f"活動\"{event_name}\"並不存在，無法重置。")
    except:
        await except_handler(ctx)
    return

@bot.slash_command(name="查詢活動報名資料")
@option("event_name", description="選擇欲查詢的活動", autocomplete=get_all_events_options)
async def event_register_info(ctx: discord.AutocompleteContext,
                            event_name: str):
    global events
    try:
        name_list = list(events.get_event_registered_dict(ctx.guild_id, event_name).keys())
        if(len(name_list) == 0):
            await ctx.respond(f"\"{event_name}\"目前還沒有人報名喔")
        else:
            name_output = "\n".join(name_list)
            output = f"\"{event_name}\"報名資料如下:\n{name_output}\n共計{len(name_list)}人。"
            await ctx.respond(output)
    except:
        await except_handler(ctx)
    return


@bot.slash_command(name="報名活動")
@option("event_name", description="選擇欲報名的活動", autocomplete=get_all_events_options)
@option("user_name", description="暱稱，可留白，預設使用DC暱稱，也可以自行輸入喜歡的ID", required=False, default=None)
async def register(ctx: discord.AutocompleteContext,
                    event_name:str,
                    user_name:str):
    global events
    try:
        if(user_name == None):
            user_name = ctx.author.name
        ret = events.register(ctx.guild_id, event_name, user_name)
        if(ret == 0):
            await ctx.respond(f"<@{ctx.author.id}>於\"{event_name}\"報名成功(登記ID為{user_name})。")
        elif(ret == -1):
            await ctx.respond(f"\"{user_name}\"已經報名\"{event_name}\"，請確認是否重複報名。")
    except:
        await except_handler(ctx)
    return

@bot.slash_command(name="取消報名活動")
@option("event_name", description="選擇欲取消報名的活動", autocomplete=get_all_events_options)
@option("user_name", description="暱稱，可不填，預設使用DC暱稱，也可自行輸入喜歡的ID", required=False, default=None)
async def unregister(ctx: discord.AutocompleteContext,
                    event_name:str,
                    user_name:str):
    global events
    try:
        if(user_name == None):
            user_name = ctx.author.name
        ret = events.unregister(ctx.guild_id, event_name, user_name)
        if(ret == 0):
            await ctx.respond(f"<@{ctx.author.id}>取消報名\"{event_name}\"，取消報名之ID為\"{user_name}\"。")
        elif(ret == -1):
            await ctx.respond(f"\"{user_name}\"並未報名\"{event_name}\"。")

    except:
        await except_handler(ctx)
    return
#####################event#####################
###############################################


##############################################
#####################poll#####################

async def get_all_polls(ctx: discord.AutocompleteContext):
    global polls
    return sorted(list(polls.get_polls_set(ctx.interaction.guild_id)))

async def get_poll_options(ctx: discord.AutocompleteContext):
    global polls
    return sorted(list(polls.get_poll_options(ctx.interaction.guild_id, ctx.options["poll_name"])))


@bot.slash_command(name="新增投票")
@option("poll_name", description="輸入投票名稱")
@option("options", description="輸入選項，各選項之間請用空格區分")
async def new_poll(ctx, poll_name, options):
    global polls
    try:
        ret = polls.new_poll(ctx.guild_id, poll_name, options.split())
        if(ret == 0):
            options = "\n".join(options.split())
            await ctx.respond(f"投票\"{poll_name}\"新增成功。\n選項為:\n{options}")
        elif(ret == -1):
            await ctx.respond(f"投票\"{poll_name}\"新增失敗，可能已存在同名投票。")
    except:
        await except_handler(ctx)


@bot.slash_command(name="刪除投票")
@option("poll_name", description="選擇投票名稱", autocomplete=get_all_polls)
async def del_poll(ctx: discord.AutocompleteContext,
                    poll_name:str):
    global polls
    try:
        ret = polls.del_poll(ctx.guild_id, poll_name)
        if(ret == 0):
            await ctx.respond(f"投票\"{poll_name}\"刪除成功。\n")
        elif(ret == -1):
            await ctx.respond(f"投票\"{poll_name}\"刪除失敗，可能不存在這項投票。")
    except:
        await except_handler(ctx)


@bot.slash_command(name="投票")
@option("poll_name", description="選擇投票名稱", autocomplete=get_all_polls)
@option("choice", description="選擇投票選項", autocomplete=get_poll_options)
async def vote(ctx: discord.AutocompleteContext,
                    poll_name:str,
                    choice:str):
    global polls
    try:
        user_name = str(ctx.author.id)
        ret = polls.vote(ctx.guild_id, poll_name, user_name, choice)
        if(ret == 0):
            await ctx.respond(f"<@{user_name}>於\"{poll_name}\"投票成功。投給了\"{choice}\"。\n")
        elif(ret == -1):
            await ctx.respond(f"投票\"{poll_name}\"失敗，可能不存在這項投票或選項。")
        elif(ret == -2):
            await ctx.respond(f"投票\"{poll_name}\"失敗，投票目前上鎖中。")
    except:
        await except_handler(ctx)


@bot.slash_command(name="開票")
@option("poll_name", description="選擇投票名稱", autocomplete=get_all_polls)
async def result_of_poll(ctx: discord.AutocompleteContext,
                    poll_name:str):
    global polls
    try:
        ret = polls.get_result_dict(ctx.guild_id, poll_name)
        if(ret == None):
            await ctx.respond(f"名為\"{poll_name}\"之投票可能不存在。請確認後再次選擇。")
        else:
            ret = dict(sorted(ret.items(), key=lambda item: item[1], reverse=True))
            output = f"{poll_name}當前投票結果為:\n"
            output += "\n".join(["{0:<10}:{1:>2}票".format(key, value) for key, value in ret.items()])
            output += f"共計{len(ret)}人投票。"
            await ctx.respond(output)
    except:
        await except_handler(ctx)


@bot.slash_command(name="亮票")
@option("poll_name", description="選擇投票名稱", autocomplete=get_all_polls)
async def state_of_vote(ctx: discord.AutocompleteContext,
                    poll_name:str):
    global polls
    try:
        ret = polls.get_poll_vote_record(ctx.guild_id, poll_name)
        if(ret == None):
            await ctx.respond(f"名為\"{poll_name}\"之投票可能不存在。請確認後再次選擇。")
        elif(ret == {}):
            await ctx.respond(f"\"{poll_name}\"當前尚無人投票")
        else:
            output = f"{poll_name}當前各人投票狀況為:\n"
            output += "\n".join([f"<@{key}>投了{value}" for key, value in ret.items()])
            await ctx.respond(output)
    except:
        await except_handler(ctx)


@bot.slash_command(name="鎖定投票")
@option("poll_name", description="選擇投票名稱", autocomplete=get_all_polls)
async def lock_poll(ctx: discord.AutocompleteContext,
                    poll_name:str):
    global polls
    try:
        print(ctx.guild_id, poll_name)
        ret = polls.lock_poll(ctx.guild_id, poll_name)
        print("after ret")
        if(ret == 0):
            await ctx.respond(f"\"{poll_name}\"投票上鎖成功。")
        elif(ret == -1):
            await ctx.respond(f"名為\"{poll_name}\"之投票可能不存在。請確認後再次選擇。")
    except:
        await except_handler(ctx)


@bot.slash_command(name="解鎖投票")
@option("poll_name", description="選擇投票名稱", autocomplete=get_all_polls)
async def unlock_poll(ctx: discord.AutocompleteContext,
                    poll_name:str):
    global polls
    try:
        ret = polls.unlock_poll(ctx.guild_id, poll_name)
        if(ret == 0):
            await ctx.respond(f"\"{poll_name}\"投票解鎖成功。")
        elif(ret == -1):
            await ctx.respond(f"名為\"{poll_name}\"之投票可能不存在。請確認後再次選擇。")
    except:
        await except_handler(ctx)

#####################poll#####################
##############################################

if __name__ == "__main__":
    bot.run("Your bot TOKEN")