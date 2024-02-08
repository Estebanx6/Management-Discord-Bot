import discord
from discord import message
from discord.ext import commands, tasks

import config
from config import *
intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.members = True
intents.guilds = True
bot = commands.Bot(command_prefix=config.prefix, intents=intents)

permissions_ticket = discord.PermissionOverwrite(read_messages=True, add_reactions=True, read_message_history =True, send_messages =True )

@bot.event
async def on_ready():
    print(bot.user, " is started")
    await bot.change_presence(status=discord.Status.online, activity = discord.Game(name=config.discord_status, type=3))




@bot.event
async def on_member_join(member):
    welcome_channel_id = config.welcome_channel_id
    welcome_channel = bot.get_channel(welcome_channel_id)
    name_member = str(member)
    embed = discord.Embed(description=(f"{name_member} Join in the server"), color=0x5CDBF0)
    # embed.set_image(url = image1)
    embed.set_author(name=welcome_channel.guild, icon_url= welcome_channel.guild.icon)
    await welcome_channel.send(embed=embed)
    



@bot.event
async def on_member_update(before, after):
    nick_roles = config.roles
    if after.roles != before.roles:
        for i in nick_roles:  
            member_role = discord.utils.get(after.guild.roles, name=i)
            if member_role in after.roles:
                if i == "@everyone":
                    await after.edit(nick=after.name)    
                    break
                else:   
                    member_role = str(member_role)
                    await after.edit(nick="[" + member_role + "] " + after.name)
                    break
            else:
                pass
    else:
        pass




@bot.event
async def on_reaction_add(reaction, user):
    emoji = str(reaction.emoji)
    if user.id == bot.user.id:
        pass
    else:

        #open ticket 

        if reaction.message.id == message_tickets.id and emoji == "📩":
            channel = discord.utils.get(message_tickets.guild.channels, name=("ticket-{}".format(user)))
            if channel:
                await message_tickets.remove_reaction(emoji, user)
            else:
                new_ticket = await message_tickets.guild.create_text_channel("ticket-{}".format(user), category = message_tickets.channel.category)
                await message_tickets.remove_reaction(emoji, user)
                embed = discord.Embed(description=("""
            :flag_es:
            **Soporte General**
            Espera a recibir soporte del staff

            :flag_us:
            **General Support**
            Wait to get support of staff
            
            """), color=0x5CDBF0, title = "Soporte General | General Support")
                embed.set_thumbnail(url=new_ticket.guild.icon.url)
                embed.set_footer(text = "Click in 🔒 to close ticket | Reacciona a 🔒 para cerrar el ticket")
                new_ticket_message =await new_ticket.send(embed=embed)
                await new_ticket_message.add_reaction('🔒')

                # set permissions

                role_viewer = (discord.utils.get(reaction.message.guild.roles, name=config.ticket_viewer_role))
                role_op = (discord.utils.get(reaction.message.guild.roles, name=config.all_commands_role))

                await new_ticket.set_permissions(user, overwrite = permissions_ticket)
                await new_ticket.set_permissions(role_viewer, overwrite = permissions_ticket)
                await new_ticket.set_permissions(role_op, overwrite = permissions_ticket)



        else:
            await message_tickets.remove_reaction(emoji, user)

        # close tocket 
            
        if reaction.message.channel.category.id == message_tickets.channel.category.id and emoji == "🔒" and reaction.message.channel.id != message_tickets.channel.id:
            await reaction.message.channel.send("Closing ticket...")
            channel = bot.get_channel(config.ticket_logs_channel_id)
            await channel.send(
f"""
Ticket Name: {reaction.message.channel.name}
Closed by: {user}
""")
            await reaction.message.channel.delete()

            


@bot.command()
async def ticketset(ctx):
    role = (discord.utils.get(ctx.author.roles, name=config.all_commands_role))
    if role:
        await ctx.message.delete()
        global message_tickets
        embed = discord.Embed(description=("""
    :flag_es:
    **Soporte General**
    Crea un ticket para resivir soporte de un staff

    :flag_us:
    **General Support**
    Create the ticket to get support of staff
    """), color=0x5CDBF0, title = "Soporte General | General Support")
        embed.set_thumbnail(url=ctx.guild.icon.url)
        message_tickets = await ctx.send(embed=embed)
        await message_tickets.add_reaction('📩')
    else: 
        pass
    




@bot.command()
async def purge(ctx, frag=2):
    role = (discord.utils.get(ctx.author.roles, name=config.all_commands_role))
    if role:
        frag = int(frag)
        await ctx.channel.purge(limit=frag)




@bot.command()
async def strike(ctx, member: discord.Member, reason, number = None):

    role = (discord.utils.get(ctx.author.roles, name=config.all_commands_role))
    if role:

        message_strike =(
f"""
**Staff:** {member.mention}
**Reason:** {reason}
**Strike:** {number}
""")
        channel = bot.get_channel(config.strikes_channel_id)

        if number:

            if config.strike_embed == True:
                strike_embed = discord.Embed(description=message_strike,color= config.strike_embed_color)
                await channel.send(embed = strike_embed)

            else:
                await channel.send(message_strike)

            if config.direct_message_strike == True:
                await member.send(f"You received a **STRIKE** in {ctx.guild.name}, Strike number: {number}")
        else:
            await channel.send(f"The command is: `{config.prefix}strike @user reason number_strike`")


    
bot.run(config.bot_token)