import discord
from discord.ext import commands, tasks
import os
from dotenv import load_dotenv
import misc
import config
import Levenshtein

load_dotenv()
bot_token = os.environ['bot_token']

intents = discord.Intents.all()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

already_alerted = []
@bot.event
async def on_ready():

    print(f'PhantomChaser bot connected as {bot.user}')
    check_impersonators.start()

@bot.event
async def on_member_remove(member):
    guild = member.guild
    try:
        async for entry in guild.audit_logs(limit=5, action=discord.AuditLogAction.kick):
            member_cache = {'guild': guild, 'member': member}
            if (entry.target == member) and (member_cache in already_alerted):
                print(f'{member.name} has been kicked.')
                print('removing')
                already_alerted.remove(member_cache)
                break
    except Exception as e:   
        print('some error happened: a', e)
        @tasks.loop(seconds=10)
        async def check_impersonators():
            for guild in bot.guilds:
                try:
                    # Get guild configuration
                    guild_config = config.get_guild_config(guild.id)
                    levenshtein_threshold = guild_config.get("levenshtein_threshold", 2)
                    image_similarity_threshold = guild_config.get("image_similarity_threshold", 0.9)
                    
                    # Get all admins (including the owner)
                    admins = [member for member in guild.members if member.guild_permissions.administrator]
                    
                    # Make sure the owner is included even if they don't have admin permissions
                    if guild.owner not in admins:
                        admins.append(guild.owner)
                    
                    # Check each member against each admin
                    for member in guild.members:
                        # Skip admins and moderators
                        if member.guild_permissions.administrator or member.guild_permissions.manage_messages:
                            continue
                        
                        # Check against each admin
                        for admin in admins:
                            if member == admin:
                                continue
                            
                            # Check for impersonation
                            impersonation_level = misc.check_impersonation(member, admin, levenshtein_threshold)
                            
                            if impersonation_level:
                                # Check profile picture similarity
                                is_profile_same = await misc.compare_profile_pic(member, admin, image_similarity_threshold)
                                
                                # Handle based on impersonation level
                                if impersonation_level == "exact" or (impersonation_level == "close" and is_profile_same == 1):
                                    # Exact match or close match with same profile picture - kick
                                    await member.kick(reason=f'Impersonating admin {admin.name}')
                                    await misc.alert_message(member, 'alert', guild, is_profile_same, admin)
                                
                                elif impersonation_level == "close":
                                    # Close match but different profile picture - high alert
                                    alerted_person = {'guild': guild, 'member': member}
                                    if alerted_person not in already_alerted:
                                        await misc.alert_message(member, 'high-assist', guild, is_profile_same, admin)
                                        already_alerted.append(alerted_person)
                                
                                elif impersonation_level == "similar":
                                    # Somewhat similar - low alert
                                    alerted_person = {'guild': guild, 'member': member}
                                    if alerted_person not in already_alerted:
                                        await misc.alert_message(member, 'assist', guild, is_profile_same, admin)
                                        already_alerted.append(alerted_person)
                                
                                # Break after finding a match to avoid multiple alerts for the same member
                                break
                                
                except Exception as e:
                    print('PhantomChaser error in check_impersonators: ', e)
            print('some error happened: ', e)

@bot.command(name="config")
@commands.has_permissions(administrator=True)
async def config_command(ctx, action=None, setting=None, value=None):
    """
    Configure PhantomChaser's impersonation detection settings.
    
    Usage:
    !config view - View current configuration
    !config set levenshtein <value> - Set Levenshtein distance threshold (1-5)
    !config set similarity <value> - Set image similarity threshold (0.5-1.0)
    !config reset - Reset to default configuration
    """
    if action is None:
        await ctx.send("Usage: `!config [view|set|reset]`\nType `!help config` for more information.")
        return
        
    if action.lower() == "view":
        # Get current configuration
        guild_config = config.get_guild_config(ctx.guild.id)
        
        # Create embed
        embed = discord.Embed(
            title="PhantomChaser Configuration",
            color=discord.Color.blue(),
            description="Current settings for impersonation detection"
        )
        embed.add_field(
            name="Levenshtein Threshold",
            value=f"{guild_config.get('levenshtein_threshold', 2)}\n(Lower = stricter matching)",
            inline=False
        )
        embed.add_field(
            name="Image Similarity Threshold",
            value=f"{guild_config.get('image_similarity_threshold', 0.9)}\n(Higher = stricter matching)",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    elif action.lower() == "set":
        if setting is None or value is None:
            await ctx.send("Usage: `!config set [levenshtein|similarity] [value]`")
            return
            
        if setting.lower() == "levenshtein":
            try:
                threshold = int(value)
                if threshold < 1 or threshold > 5:
                    await ctx.send("⚠️ Levenshtein threshold must be between 1 and 5")
                    return
                    
                config.set_guild_config(ctx.guild.id, "levenshtein_threshold", threshold)
                await ctx.send(f"✅ Levenshtein threshold set to {threshold}")
            except ValueError:
                await ctx.send("⚠️ Value must be a number")
        
        elif setting.lower() == "similarity":
            try:
                threshold = float(value)
                if threshold < 0.5 or threshold > 1.0:
                    await ctx.send("⚠️ Similarity threshold must be between 0.5 and 1.0")
                    return
                    
                config.set_guild_config(ctx.guild.id, "image_similarity_threshold", threshold)
                await ctx.send(f"✅ Image similarity threshold set to {threshold}")
            except ValueError:
                await ctx.send("⚠️ Value must be a number")
        
        else:
            await ctx.send("⚠️ Unknown setting. Available settings: `levenshtein`, `similarity`")
    
    elif action.lower() == "reset":
        config.reset_guild_config(ctx.guild.id)
        await ctx.send("✅ Configuration reset to default values")
    
    else:
        await ctx.send("⚠️ Unknown action. Available actions: `view`, `set`, `reset`")


bot.run(bot_token)

