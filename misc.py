import discord
import re
import requests
import imagehash
from io import BytesIO
from PIL import Image
import Levenshtein


def generate_regex_pattern(name):
    pattern = '^[-_ *]?' + ''.join(f'{c}[-_ *]?' for c in name.lower()) + '[-_ *]?$'
    return pattern


async def compare_profile_pic(member, admin, threshold=None):
    """
    Compare the profile pictures of a member and an admin.
    
    Args:
        member: The member to check
        admin: The admin to compare against
        threshold: Optional custom similarity threshold (0.0 to 1.0)
        
    Returns:
        1 if the profile pictures are similar, 0 otherwise
    """
    # Use default threshold if none provided
    if threshold is None:
        threshold = 0.9
    
    admin_avatar_url = admin.avatar.url
    member_avatar_url = member.avatar.url
    admin_avatar_response = requests.get(admin_avatar_url)
    member_avatar_response = requests.get(member_avatar_url)

    admin_avatar_image = Image.open(BytesIO(admin_avatar_response.content))
    member_avatar_image = Image.open(BytesIO(member_avatar_response.content))

    admin_avatar_hash = imagehash.phash(admin_avatar_image)
    member_avatar_hash = imagehash.phash(member_avatar_image)

    distance = Levenshtein.hamming(str(admin_avatar_hash), str(member_avatar_hash))
    similarity = 1.0 - (distance / len(str(admin_avatar_hash)))

    if similarity >= threshold:
        return 1
    else:
        return 0


async def alert_message(member, type, guild, is_profile_same, admin=None):
    """
    Send an alert message about a potential impersonator.
    
    Args:
        member: The member who might be impersonating
        type: The type of alert ('alert', 'assist', or 'high-assist')
        guild: The guild where the impersonation is happening
        is_profile_same: Whether the profile pictures are similar
        admin: The admin being impersonated (optional, defaults to guild owner)
    """
    if is_profile_same == 0:
        profile_matches = "NO"
    else:
        profile_matches = "YES"
    
    # If no admin is specified, use the guild owner
    if admin is None:
        admin = guild.owner
        admin_info = "Server Owner"
    else:
        admin_info = f"Admin: {admin.name}#{admin.discriminator}"

    if type=='alert':
        channel_name = "impersonation-alerts"
        message = f"Impersonator kicked:\nUsername: {member}\nTag: {member.discriminator}\nNickname: {member.display_name}\nID= {member.id}\nPhoto matches? {profile_matches}\nImpersonating: {admin_info}"
    elif type =='assist':
        channel_name = "impersonation-assist"
        message = f"(LOW ALERT) I think this person might be impersonating. Please check if you need to kick this person? :\nUsername: {member}\nTag: {member.discriminator}\nNickname: {member.display_name}\nID = {member.id}\nPhoto matches? {profile_matches}\nPossibly impersonating: {admin_info}"
    elif type =='high-assist':
        channel_name = "impersonation-assist"
        message = f"(HIGH ALERT) I think this person might be impersonating. Please check if you need to kick this person? :\nUsername: {member}\nTag: {member.discriminator}\nNickname: {member.display_name}\nID = {member.id}\nPhoto matches? {profile_matches}\nPossibly impersonating: {admin_info}"
    
    channel = discord.utils.get(guild.channels, name=channel_name)

    print(message)
    if not channel:
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            guild.me: discord.PermissionOverwrite(read_messages=True),
            guild.owner: discord.PermissionOverwrite(read_messages=True),
            guild.roles[0]: discord.PermissionOverwrite(read_messages=False)
        }
        new_channel = await guild.create_text_channel(channel_name, overwrites=overwrites)

        await new_channel.send(message)
    else:
        await channel.send(message)


def owner_regex_patterns(owner):
    owner_name = owner.name.lower()
    owner_nick = owner.display_name.lower()
    
    owner_name_format = generate_regex_pattern(owner_name)
    owner_nick_format = generate_regex_pattern(owner_nick)

    owner_name_regex = re.compile(owner_name_format, re.IGNORECASE)
    owner_nick_regex = re.compile(owner_nick_format, re.IGNORECASE)

    return owner_name_regex, owner_nick_regex, owner_name, owner_nick


def check_impersonation(member, admin, levenshtein_threshold=2):
    """
    Check if a member is impersonating an admin.
    
    Args:
        member: The member to check
        admin: The admin to compare against
        levenshtein_threshold: The maximum Levenshtein distance to consider as impersonation
        
    Returns:
        "exact" if exact match, "close" if close match, "similar" if somewhat similar, None otherwise
    """
    # Get member and admin names
    member_name = member.name.lower()
    member_nick = member.display_name.lower()
    admin_name = admin.name.lower()
    admin_nick = admin.display_name.lower()
    
    # Create regex patterns for the admin
    admin_name_regex, admin_nick_regex, _, _ = owner_regex_patterns(admin)
    
    # Check for exact matches
    if (str(member) == str(admin) or
        admin_name_regex.search(member_name) or
        admin_nick_regex.search(member_name) or
        admin_name_regex.search(member_nick) or
        admin_nick_regex.search(member_nick)):
        return "exact"
    
    # Check for close matches (Levenshtein distance <= threshold)
    elif ((Levenshtein.distance(member_name, admin_name) <= levenshtein_threshold) or
          (Levenshtein.distance(member_name, admin_nick) <= levenshtein_threshold) or
          (Levenshtein.distance(member_nick, admin_name) <= levenshtein_threshold) or
          (Levenshtein.distance(member_nick, admin_nick) <= levenshtein_threshold)):
        return "close"
    
    # Check for somewhat similar names (Levenshtein distance <= threshold + 1)
    elif ((Levenshtein.distance(member_name, admin_name) <= levenshtein_threshold + 1) or
          (Levenshtein.distance(member_name, admin_nick) <= levenshtein_threshold + 1) or
          (Levenshtein.distance(member_nick, admin_name) <= levenshtein_threshold + 1) or
          (Levenshtein.distance(member_nick, admin_nick) <= levenshtein_threshold + 1)):
        return "similar"
    
    # Not impersonating
    return None
