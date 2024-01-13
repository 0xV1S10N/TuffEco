import discord
import requests
import json
import random
from discord.ext.commands import BucketType
from discord.ext.commands import Bot
from discord.utils import get
from discord.ext import commands , tasks
import aiohttp
from datetime import datetime, timedelta
from discord.ext.commands import cooldown
import time
import asyncio


TOKEN = "YOUR_DISCORD_BOT_TOKEN"

#Load the user data from data.json
def load_data():
    with open('data.json', 'r') as file:
        try:
            return json.load(file)
        except:
            return {}

# Save the user data to data.json
def save_data(data):
    with open('data.json', 'w') as file:
        json.dump(data, file, indent=4)

# Check if the user exists in the data
def user_exists(user_id):
    return str(user_id) in data

# Get the user's balance
def get_balance(user_id):
    if user_exists(user_id):
        return data[str(user_id)]['balance']
    else:
        return 0

def get_leaderboard(n):
    leaderboard = sorted(data.items(), key=lambda x: x[1]['balance'], reverse=True)[:n]
    return leaderboard

def update_balance(user_id, amount):
    if user_exists(user_id):
        data[str(user_id)]['balance'] += amount
    else:
        data[str(user_id)] = {'balance': amount}

    if data[str(user_id)]['balance'] < 0:
        data[str(user_id)]['balance'] = 0

    save_data(data)

def update_last_claimed(user_id):
    if user_exists(user_id):
        data[str(user_id)]['last_claimed'] = datetime.now().isoformat()
        save_data(data)

def can_claim_daily(user_id):
    if user_exists(user_id):
        if 'last_claimed' in data[str(user_id)]:
            last_claimed = datetime.fromisoformat(data[str(user_id)]['last_claimed'])
            now = datetime.now()
            return now - last_claimed >= timedelta(days=1)
        else:
            return True
    else:
        return True

def can_claim_work(user_id):
    if user_exists(user_id):
        if 'last_worked' in data[str(user_id)]:
            last_worked = datetime.fromisoformat(data[str(user_id)]['last_worked'])
            now = datetime.now()
            return now - last_worked >= timedelta(minutes=5)
        else:
            return True
    else:
        return True



# Initialize the bot
class MyBot(commands.Bot):

    def __init__(self):

        super().__init__(command_prefix = ">",
                         intents = discord.Intents.all(),
                         case_insensitive=True,
                         application_id =1122601712146985050)
        
        # self.initial_extensions = [
        #     "cogs.music"]
        self.added = False



    async def setup_hook(self):
        self.session = aiohttp.ClientSession()
        # for cogs in self.initial_extensions: 
        #     await self.load_extension(cogs)
        await self.tree.sync()
        print(f"Synced for {self.user}!")

    #closing
    async def close(self):
        await super().close()
        await self.session.close()




    #on_ready message
    async def on_ready(self):
        print(f'{self.user} has connected to Discord!')
        if not self.added:
            self.added = True
        global data
        data = load_data()
        live_status.start()
        voice = await bot.fetch_channel("1093395247817576468")
        await voice.connect(self_deaf=True)

allowed_channel_id = 1065543823381508116
async def restricted_channel(ctx):
    # Check if the command is being invoked in the allowed channel
    return ctx.channel.id == allowed_channel_id


bot = MyBot()
bot.remove_command('help')
channelidbot = 1065543823381508116




@bot.command()
async def help(ctx):
    if ctx.channel.id == channelidbot:
        embed = discord.Embed(title='دستورات بات 🤖', description='لیست کامندهای موجود 🧩:', color=discord.Color.blue())
        # Add commands and their descriptions
        embed.add_field(name='>Help', value='منوی کامند هارا را نشان می دهد ❓', inline=True)
        embed.add_field(name='>Balance', value='حساب شما را نشان می دهد 🪙', inline=True)
        embed.add_field(name='>Daily', value='به شما پاداش روزانه میدهد 💸', inline=True)
        embed.add_field(name='>Work', value='میتوانید کار کنید 👨‍🔧', inline=True)
        embed.add_field(name='>Collect', value='دریافت سکه ها جمع کرده 💰', inline=True)
        embed.add_field(name='>Gamble Number', value='فمار کردن 🎰', inline=True)
        embed.add_field(name='>Rob @mention', value='دزدی کردن از کاربر ها 🥷', inline=True)
        embed.add_field(name='>Pay @mention', value='دادن پول یه یک نفر یا پرداخت 💲', inline=True)     
        embed.add_field(name='>Buy Help', value='منوی کامند های خرید 🛒', inline=True)     
        embed.add_field(name='>Buyeds', value='خرید های شما 🛍️', inline=True)     
        embed.add_field(name='>Leaderboard', value='منوی 10 نفر اول از در تعداد سکه 🏦', inline=True)  
        embed.add_field(name='>Clear', value='پاک کردن پیام ها (ادمین) 🧹', inline=True)   
        embed.add_field(name='>Dev', value='سازنده بات ⚙️', inline=True)                         
        await ctx.channel.send(embed=embed)
    else:
        await ctx.message.delete()
        warn = await ctx.send(f"Aghaaaaaaa {ctx.author.mention} Mage Jende Khonas Boro Gomsho Dakhel <#1065543823381508116> Cmd Hato Use Bede <a:2884gapolice:1096353641146892358>  ")
        await asyncio.sleep(20)
        await warn.delete()
# Process commands
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    user_id = message.author.id
    update_balance(user_id, 1)
    await bot.process_commands(message)


@bot.event
async def on_command_error(ctx,error):
  if isinstance(error, commands.CommandNotFound):
    embed = discord.Embed(title='⚠️ کامند پیدا نشد', description='**❌ کامند نا معتبر**')
    await ctx.send(embed=embed)
  else:
    if isinstance(error,commands.CommandOnCooldown):
      embed = discord.Embed(title='صبر ⌛', description=f'شما در حال کولدان هستید ** {error.retry_after}** ثانیه ⏱️')
      await ctx.send(embed=embed)
    else:
      print(error)


# Command to check balance
@bot.command()
async def balance(ctx):
    if ctx.channel.id == channelidbot:
        
            user_id = ctx.author.id
            balance = get_balance(user_id)
            embed = discord.Embed()
            embed.add_field(name="**حساب شما :**",value=f"{balance} سکه 🪙")
            await ctx.channel.send(embed=embed)
    else:
            warn = await ctx.send("Aghaaaaaaa Mage Jende Khonas Boro Gomsho Dakhel <#1065543823381508116> Cmd Hato Use Bede :2884gapolice: ")
            await asyncio.sleep(20)
            await warn.delete()

# Command to give coins to another user
@bot.command()
async def pay(ctx, member: discord.Member, amount: int):
    if ctx.channel.id == channelidbot:

        if amount <= 0:
            await ctx.send("**مقدار باید بیشتر از 0 باشد**")
            return
        elif not user_exists(ctx.author.id):
            await ctx.send("**شما هنوز بازی را شروع نکرده اید**")
            return
        elif data[str(ctx.author.id)]['balance'] < amount:
            await ctx.send("**شما سکه های کافی برای دادن ندارید**")
            return
        elif not user_exists(member.id):
            data[str(member.id)] = {'balance': amount}
        else:
            data[str(member.id)]['balance'] += amount
            data[str(ctx.author.id)]['balance'] -= amount
            save_data(data)
            embed = discord.Embed(title=f"شما **{amount} سکه به {member.display_name} **دادید 🎁")
            embed.set_footer(text="نصیحت من به شما زیاد سکه جا به جا نکنید دزد ها در کمین هستن ✌🏻🗿")
            await ctx.channel.send(embed=embed)
    else:
        warn = await ctx.send("Aghaaaaaaa Mage Jende Khonas Boro Gomsho Dakhel <#1065543823381508116> Cmd Hato Use Bede <a:2884gapolice:1096353641146892358> ")
        await asyncio.sleep(20)
        await warn.delete()

# Command to gamble coins
@bot.command()
async def gamble(ctx, amount: int):
    if ctx.channel.id == channelidbot:

        if amount < 1:
            await ctx.channel.send('**مبلغ باید مثبت باشد**')
            return

        user_id = ctx.author.id
        balance = get_balance(user_id)
        if balance < amount:
            embed = discord.Embed(title='**❌ بالانس شما ~~ناکافی~~ است**')
            embed.set_footer(text="تو که سکه نداری گوه میخوری میای قمار میکنی 🤨")
            await ctx.channel.send(embed=embed)
            return

        outcome = random.choice(['win', 'lose'])
        if outcome == 'win':
            update_balance(user_id, amount)
            embed = discord.Embed(title="**نتیجه 🎲**")
            embed.add_field(name=f'تبریک میگم شما برنده شدید 🎉', value=f"+{amount} 🪙")
            embed.set_footer(text="کون سفید 🤝🏼")
            await ctx.channel.send(embed=embed)
            

        else:
            update_balance(user_id, -amount)
            embed = discord.Embed(title="**نتیجه 🎲**")
            embed.add_field(name=f'اوه شما باختید ❌', value=f"-{amount} 🪙")
            embed.set_footer(text="خیلی ببخشید ببخشید ولی ریدم تو شانست 🗿")
    else:
        warn = await ctx.send("Aghaaaaaaa Mage Jende Khonas Boro Gomsho Dakhel <#1065543823381508116> Cmd Hato Use Bede <a:2884gapolice:1096353641146892358> ")
        await asyncio.sleep(20)
        await warn.delete()
            



@bot.command()
async def leaderboard(ctx):
    sorted_data = sorted(data.items(), key=lambda x: x[1]['balance'], reverse=True)
    embed = discord.Embed(title="**لیست ده نفر اول در تعداد سکه ها 🏦**", color=0x00ff00)
    if ctx.channel.id == channelidbot:
        for index, (user_id, user_data) in enumerate(sorted_data):
            try:
                member = await ctx.guild.fetch_member(int(user_id))
                name = member.display_name
            except:
                name = "کاربر ناشناس"
                balance = user_data['balance']
                embed.add_field(name=f"{index+1}. {name}", value=f"**سکه** **: {balance} 🪙**", inline=False)
                if index+1 == 10:
                    break
            embed.set_image(url="https://media.discordapp.net/attachments/1122680430626361384/1122727611630632990/istockphoto-1208505233-612x612.jpg?width=765&height=463")
            await ctx.channel.send(embed=embed)
    else:
        warn = await ctx.send("Aghaaaaaaa Mage Jende Khonas Boro Gomsho Dakhel <#1065543823381508116> Cmd Hato Use Bede <a:2884gapolice:1096353641146892358> ")  # Corrected the error message
        await asyncio.sleep(20)
        await warn.delete()
    
@bot.command()
@commands.cooldown(1, 86400, commands.BucketType.user)  # 24 hours cooldown
async def daily(ctx):
    if ctx.channel.id == channelidbot:
        user_id = ctx.author.id
        update_balance(user_id, 500)
        data[str(user_id)]['last_claimed'] = datetime.now().isoformat()
        save_data(data)
        embed = discord.Embed(title='**شما پاداش روزانه 500 🪙 سکه را دریافت کرده اید**')
        await ctx.channel.send(embed=embed)

        return
    else:
        warn = await ctx.send("Aghaaaaaaa Mage Jende Khonas Boro Gomsho Dakhel <#1065543823381508116> Cmd Hato Use Bede <a:2884gapolice:1096353641146892358> ")  # Corrected the error message
        await asyncio.sleep(20)
        await warn.delete()




@bot.command()
@commands.cooldown(1, 1800, commands.BucketType.user)  # 5 minutes cooldown
async def work(ctx):
    user_id = ctx.author.id
    if ctx.channel.id == channelidbot:
        if not can_claim_work(user_id):
            embed = discord.Embed(title='**شما میتوانید هر 5 دقیقه کار کنید 🙅‍♂️**')
            await ctx.channel.send(embed=embed)
            return

        earned = random.randint(10, 200)
        if user_exists(user_id):
            if 'earned' in data[str(user_id)]:
                data[str(user_id)]['earned'].append(earned)
            else:
                data[str(user_id)] = {'balance': 0, 'last_worked': datetime.now().isoformat(), 'earned': [earned]}
        else:
            data[str(user_id)] = {'balance': 0, 'last_worked': datetime.now().isoformat(), 'earned': [earned]}
            save_data(data)
            embed = discord.Embed()
            embed.add_field(name="**⚒️ شما سخت کار کردید و به سکه های کسب شده شما اضافه شده است **",value=f"**{earned} 🪙**")
            embed.set_footer(text="برای گرفتن سکه و اضافه شدن سکه های جم شده به حساب خود از کامند Collect> استفاده کنید ")
            await ctx.channel.send(embed=embed)
    else:
        warn = await ctx.send("Aghaaaaaaa Mage Jende Khonas Boro Gomsho Dakhel <#1065543823381508116> Cmd Hato Use Bede <a:2884gapolice:1096353641146892358> ")  # Corrected the error message
        await asyncio.sleep(20)
        await warn.delete()


@bot.command()
async def collect(ctx):
    user_id = ctx.author.id
    if ctx.channel.id == channelidbot:
        if user_exists(user_id) and data[str(user_id)]['earned']:
            earned_coins = sum(data[str(user_id)]['earned'])
            update_balance(user_id, earned_coins)
            data[str(user_id)]['earned'] = []
            save_data(data)
            await ctx.channel.send(f'شما **{earned_coins} 🪙** سکه جمع کردید')
        else:
            await ctx.channel.send('**شما هیچ سکه ای برای جمع آوری ندارید 🤷‍♂️**')
    else:
        warn = await ctx.send("Aghaaaaaaa Mage Jende Khonas Boro Gomsho Dakhel <#1065543823381508116> Cmd Hato Use Bede <a:2884gapolice:1096353641146892358> ")
        await asyncio.sleep(20)
        await warn.delete()

@bot.command()
@cooldown(1, 300, BucketType.user)
async def rob(ctx, member: discord.Member):
    user_id = ctx.author.id
    victim_id = member.id
    if ctx.channel.id == channelidbot:
        if user_id == victim_id:
            embed = discord.Embed(title=f"**شما نمیتوانید از خود دزدی کنید 😐**")
            embed.set_footer(text="مشروووب خوردی پسسسر 💀")
            await ctx.send(embed=embed)
            return

        if not user_exists(victim_id):
            embed = discord.Embed(title=f"**لطفا از کامند های اولیه استفاده کنید !!!**")
            embed.set_footer(text="داداش یه کاری یه دیلی گیفتی یه قماری بکن بد بیا راب بزن 🙃")
            await ctx.send(embed=embed)
            return

        if 'balance' not in data[str(victim_id)] or data[str(victim_id)]['balance'] <= 0:
            await ctx.send(f"**{member.display_name}** 🤷‍♂️سکه ای برای سرقت ندارد")
            return

        if user_exists(user_id) and data[str(user_id)]['balance'] <= 0:
            await ctx.send("**شما هیچ سکه ای برای سرقت ندارید 🤷‍♂️**")
            return

        if user_exists(user_id) and data[str(user_id)]['balance'] < 85:
            await ctx.send("**🤷‍♂️ برای سرقت از کسی حداقل به 85 سکه نیاز دارید**")
            return

        if user_exists(user_id):
            robbed = round(random.uniform(0.1, 0.15) * data[str(victim_id)]['balance'])
            data[str(victim_id)]['balance'] -= robbed
            data[str(user_id)]['balance'] += robbed
            save_data(data)
            await ctx.send(f"دزدی کردی از **{member.display_name} و از او {robbed}** سکه سرقت کردی")
            embed = discord.Embed(title=f"دزدی کردی از **{member.display_name} و از او {robbed}** سکه سرقت کردی")
            embed.set_footer(text="درو که الان امور ها میان کونت میزارن 😗")
            await ctx.send(embed=embed)
    else:
        warn = await ctx.send("Aghaaaaaaa Mage Jende Khonas Boro Gomsho Dakhel <#1065543823381508116> Cmd Hato Use Bede <a:2884gapolice:1096353641146892358> ")
        await asyncio.sleep(20)
        await warn.delete()


@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    if amount <= 0:
        channel = ctx.channel.name
        restricted_channels = ["kon"]  # Renamed restricted_channel to restricted_channels
        if channel in restricted_channels:
         await ctx.send("**مقدار باید بیشتر از 0 باشد**")
        return
    await ctx.channel.purge(limit=amount+1)
    abas = discord.Embed(f"**{amount}**🧹 پیام پاک شد")
    await ctx.send(embed=abas)
    time.sleep(2)
    abas.delete()
    
    


@bot.command()
async def buy(ctx, item: str):
    if ctx.channel.id == channelidbot:
        if ctx is None:
            embed = discord.Embed(title="**📌 کامند باید در سرور استفاده شود**")
            await ctx.send(embed=embed)
            return
        if ctx.author is None:
            embed = discord.Embed(title="**یوزر نامعتبر ❌**")
            await ctx.send(embed=embed)
            return
        if not user_exists(ctx.author.id):
            embed = discord.Embed("**لطفا اول کامند های اولیه را انجام دهید 😗**")
            await ctx.send(embed=embed)
            return

        if item == "tenacity":
            if data[str(ctx.author.id)].get('balance', 0) < 200000:
                embed = discord.Embed(title="**🛒 شما سکه کافی برای خرید این چیت ندارید**")
                embed.set_footer(text="یکم کار کن یکم فعالیت کن داخل چت پول در میاری ✌🏻")
                await ctx.send(embed=embed)
                return
            if "tenacity" in data[str(ctx.author.id)].get('buyeds', []):
                embed = discord.Embed(title="**🏷️ شما قبلا این چیت را خریداری کردید**")
                embed.set_footer(text="کسخلی ؟")
                await ctx.send(embed=embed)
                return
            data[str(ctx.author.id)]['balance'] -= 200000
            data[str(ctx.author.id)].setdefault('buyeds', []).append("Tenacity Client")
            save_data(data)
            role = discord.utils.get(ctx.guild.roles, name="Cheater")
            await ctx.author.add_roles(role)
            embed = discord.Embed(title="**خرید موفق**", description="**شما چیت تناسیتی را خریداری کرده اید. امید وارم لذت ببرید!🎉**", color=0x00ff00)
            embed = discord.Embed(title="||**https://mega.nz/file/G99QUAja#MvvXURqpDmLRDefGZnXXcLO_ATDJ4b3MatUDMVKBaxw**|| \n اگه از چیت راضی بودید حتما بخش <1095753777870549103#> رضایت بدید ✌🏻")
            embed.set_footer(text="discord.gg/mcclub")
            await ctx.author.send(embed=embed)
    

        elif item == "sigma5":
            if data[str(ctx.author.id)].get('balance', 0) < 200000:
                embed = discord.Embed(title="**🛒 شما سکه کافی برای خرید این چیت ندارید**")
                embed.set_footer(text="یکم کار کن یکم فعالیت کن داخل چت پول در میاری ✌🏻")
                await ctx.send(embed=embed)
                return
            if "sigma5" in data[str(ctx.author.id)].get('buyeds', []):
                embed = discord.Embed(title="**🏷️ شما قبلا این چیت را خریداری کردید**")
                embed.set_footer(text="کسخلی ؟")
                await ctx.send(embed=embed)
                return 
            data[str(ctx.author.id)]['balance'] -= 200000
            data[str(ctx.author.id)].setdefault('buyeds', []).append("Sigma 5")
            save_data(data)
            # role = discord.utils.get(ctx.guild.roles, name="FiveM Cheater")
            # await ctx.author.add_roles(role)
            embed = discord.Embed(title="**خرید موفق**", description="**شما چیت سیگما را خریداری کرده اید. امید وارم لذت ببرید!🎉**", color=0x00ff00)
            await ctx.author.send(embed=embed)
            await ctx.send(embed=embed)

        elif item == "rise":
            if data[str(ctx.author.id)].get('balance', 0) < 200000:
                embed = discord.Embed(title="**🛒 شما سکه کافی برای خرید این چیت ندارید**")
                embed.set_footer(text="یکم کار کن یکم فعالیت کن داخل چت پول در میاری ✌🏻")
                await ctx.send(embed=embed)
                return
            if "rise" in data[str(ctx.author.id)].get('buyeds', []):
                embed = discord.Embed(title="**🏷️ شما قبلا این چیت را خریداری کردید**")
                embed.set_footer(text="کسخلی ؟")
                await ctx.send(embed=embed)
                return
            data[str(ctx.author.id)]['balance'] -= 200000
            data[str(ctx.author.id)].setdefault('buyeds', []).append("Rise Client")
            save_data(data)
            # role = discord.utils.get(ctx.guild.roles, name="Mamane Devil")
            # await ctx.author.add_roles(role)
            embed = discord.Embed(title="**خرید موفق**", description="**شما چیت رایس را خریداری کرده اید. امید وارم لذت ببرید!🎉**", color=0x00ff00)
            # await ctx.author.send(embed=embed)
            await ctx.send(embed=embed)
        elif item == "help":
            embed = discord.Embed(title="**خرید چیت های پرمیوم 💰**")
            embed.add_field(name="**Tenacity Client ²⁰⁰ᵏ**",value="type : ``>buy tenacity``")
            embed.add_field(name="**Sigma 5 ²⁰⁰ᵏ**",value="type : ``>buy sigma5``")
            embed.add_field(name="**Rise Client ²⁰⁰ᵏ**",value="type : ``>buy rise``")
            await ctx.send(embed=embed)

        else:
                embed = discord.Embed(title="**ایتم نامعتبر ❌**")
                await ctx.send(embed=embed)
    else:
        warn = await ctx.send("Aghaaaaaaa Mage Jende Khonas Boro Gomsho Dakhel <#1065543823381508116> Cmd Hato Use Bede <a:2884gapolice:1096353641146892358> ")
        await asyncio.sleep(20)
        await warn.delete()

@bot.command()
async def buyeds(ctx):
    if ctx.channel.id == channelidbot:
        if ctx is None:
            embed = discord.Embed(title="**📌 کامند باید در سرور استفاده شود**")
            await ctx.send(embed=embed)
            return
        if ctx.author is None:
            embed = discord.Embed(title="**یوزر نامعتبر ❌**")
            await ctx.send(embed=embed)
            return
        if not user_exists(ctx.author.id):
            embed = discord.Embed("**لطفا اول کامند های اولیه را انجام دهید 😗**")
            await ctx.send(embed=embed)
            return
        buyeds = data[str(ctx.author.id)].get('buyeds', [])
        if not buyeds:
            await ctx.send("**شما هنوز هیچ ایتمی را خریداری نکرده اید**")
            return
        embed = discord.Embed(title="**ایتم های خریداری شده شما**", color=0x00ff00)
        for item in buyeds:
            embed.add_field(name=item, value="**از خرید خود لذت ببرید!**", inline=False)
            await ctx.send(embed=embed)
    else:
        warn = await ctx.send("Aghaaaaaaa Mage Jende Khonas Boro Gomsho Dakhel <#1065543823381508116> Cmd Hato Use Bede <a:2884gapolice:1096353641146892358> ")
        await asyncio.sleep(20)
        await warn.delete()


@bot.command()
async def dev(ctx):
    embed = discord.Embed(title="The Economy System Developers")
    embed.add_field(name="⚙️ Main Developer",value="<@257635603091292160> | ice.zero ")
    embed.add_field(name="⚙️ Helper Developer",value="<@249383958289186816> | pa9da ")
    embed.set_footer(text="If You want a bot like this , you can buy from us 🤝")
    await ctx.send(embed=embed)

@tasks.loop()
async def live_status(seconds=30):

    activity = discord.Activity(type=discord.ActivityType.watching, name=f".gg/mcclub")
    await bot.change_presence(status=discord.Status.idle,activity=activity)
    await asyncio.sleep(5)

    activity = discord.Activity(type=discord.ActivityType.watching, name=f'>Help')
    await bot.change_presence(status=discord.Status.idle,activity=activity)
    await asyncio.sleep(15)

    activity = discord.Activity(type=discord.ActivityType.watching, name=f'Members {len(bot.users)} ')
    await bot.change_presence(status=discord.Status.idle,activity=activity)
    await asyncio.sleep(15)

bot.run(TOKEN)