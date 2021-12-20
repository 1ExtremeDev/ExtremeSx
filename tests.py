from core.checkers.modules import Apple, EpicGames, Instagram, Spotify, TakeWay
from core.discord.actions import Checker, Leave
from core.discord.spammers import Report, friendRequest, privateSpam, serverSpam
from lib.values import *

Join(
    token="token", 
    link="link"
)

Leave(
    token="token", 
    link="link"
)

privateSpam(
    token="token", 
    message="message", 
    identifier="identifier"
)

serverSpam(
    token="token", 
    message="message", 
    identifier="identifier"
)

friendRequest(
    token="token", 
    username="username", 
    discriminator="discriminator"
)

Report(
    token="token", 
    messageID="messageID", 
    channelID="channelID", 
    guildID="guildID", 
    reason="reason"
)

Checker(
    token="token"
)

BruteForce(
    identifier="identifier"
)

Instagram(
    line="email@gmail.com:password"
)

Spotify(
    email="email@gmail.com"
)

Apple(
    email="email@gmail.com"
)

EpicGames(
    line="email@gmail.com"
)

TakeWay(
    line="email@gmail.com"
)