# Functions for brawlhalla duel
from random import randint
from .Brawler import Brawler


def do_move(p_mv, o_mv, p, o):
    # moves = ["attack", "dodge", "jump"]
    if p_mv == 'attack' and o_mv == 'attack':
        msg = attack_attack(p, o)
    elif p_mv == 'attack' and o_mv == 'dodge':
        msg = attack_dodge(p, o)
    elif p_mv == 'attack' and o_mv == 'jump':
        msg = attack_jump(p, o)
    elif p_mv == 'dodge' and o_mv == 'attack':
        msg = attack_dodge(o, p)
    elif p_mv == 'dodge' and o_mv == 'dodge':
        msg = dodge_dodge(p, o)
    elif p_mv == 'dodge' and o_mv == 'jump':
        msg = dodge_jump(p, o)
    elif p_mv == 'jump' and o_mv == 'attack':
        msg = attack_jump(o, p)
    elif p_mv == 'jump' and o_mv == 'dodge':
        msg = dodge_jump(o, p)
    elif p_mv == 'jump' and o_mv == 'jump':
        msg = jump_jump(p, o)
    return msg


def attack_attack(p, o):
    p_chance = ((p.spd + p.dex) / (p.spd + p.dex + o.spd + o.dex)) * 100
    o_chance = ((o.spd + o.dex) / (o.spd + o.dex + p.spd + p.dex)) * 100
    p_rand = randint(1, 100)
    o_rand = randint(1, 100)
    if p_rand <= p_chance and o_rand <= o_chance:
        p_dmg = p.clash(o)
        o_dmg = o.clash(p)
        return f"CLASH!\n"\
               f"{p.username} hit {o.username} for **{p_dmg}** damage!\n"\
               f"{o.username} hit {p.username} for **{o_dmg}** damage!"
    elif p_rand <= p_chance:
        dmg = p.attack(o)
        return f"{p.username} hit {o.username} for **{dmg}** damage! "\
               f"{o.username} missed!"
    elif o_rand <= o_chance:
        dmg = o.attack(p)
        return f"{p.username} missed! "\
               f"{o.username} hit {p.username} for **{dmg}** damage!"
    else:
        return f"Both players missed their attack!"


def attack_dodge(p, o):
    o.add_dodge_cooldown()
    return f"{o.username} dodged {p.username}'s ground attack!"


def attack_jump(p, o):
    o.add_jump_count()
    if o.jump(p):
        return f"{o.username} jumped over {p.username}'s ground attack!"
    else:
        dmg = p.attack(o)
        return f"{p.username}'s light attack caught "\
               f"{o.username}'s jump for **{dmg}** damage!"


def dodge_dodge(p, o):
    p.add_dodge_cooldown()
    o.add_dodge_cooldown()
    return f"Both players dodged... nothing!"


def dodge_jump(p, o):
    p.add_dodge_cooldown()
    o.add_jump_count()
    return f"{p.username} dodged and {o.username} jumped."


def jump_jump(p, o):
    p.add_jump_count()
    o.add_jump_count()
    return f"Both players jumped."
