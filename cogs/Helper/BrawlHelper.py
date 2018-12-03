# Functions for brawlhalla duel
from random import randint
from .Brawler import Brawler


def do_move(p_mv, o_mv, p, o):
    # moves = ["ground attack", "anti-air attack", "signature attack", "dodge", "jump", "charge"]
    if p_mv == 'ground attack' and o_mv == 'ground attack':
        msg = gAttack_gAttack(p, o)
    elif p_mv == 'ground attack' and o_mv == 'anti-air attack':
        msg = gAttack_aAttack(p, o)
    elif p_mv == 'ground attack' and o_mv == 'signature attack':
        msg = gAttack_sAttack(p, o)
    elif p_mv == 'ground attack' and o_mv == 'dodge':
        msg = gAttack_dodge(p, o)
    elif p_mv == 'ground attack' and o_mv == 'jump':
        msg = gAttack_jump(p, o)
    elif p_mv == 'ground attack' and o_mv == 'charge':
        msg = gAttack_charge(p, o)

    elif p_mv == 'anti-air attack' and o_mv == 'ground attack':
        msg = gAttack_aAttack(o, p)
    elif p_mv == 'anti-air attack' and o_mv == 'anti-air attack':
        msg = aAttack_aAttack(p, o)
    elif p_mv == 'anti-air attack' and o_mv == 'signature attack':
        msg = aAttack_sAttack(p, o)
    elif p_mv == 'anti-air attack' and o_mv == 'dodge':
        msg = aAttack_dodge(p, o)
    elif p_mv == 'anti-air attack' and o_mv == 'jump':
        msg = aAttack_jump(p, o)
    elif p_mv == 'anti-air attack' and o_mv == 'charge':
        msg = aAttack_charge(p, o)

    elif p_mv == 'signature attack' and o_mv == 'ground attack':
        msg = gAttack_sAttack(o, p)
    elif p_mv == 'signature attack' and o_mv == 'anti-air attack':
        msg = aAttack_sAttack(o, p)
    elif p_mv == 'signature attack' and o_mv == 'signature attack':
        msg = sAttack_sAttack(p, o)
    elif p_mv == 'signature attack' and o_mv == 'dodge':
        msg = sAttack_dodge(p, o)
    elif p_mv == 'signature attack' and o_mv == 'jump':
        msg = sAttack_jump(p, o)
    elif p_mv == 'signature attack' and o_mv == 'charge':
        msg = sAttack_charge(p, o)

    elif p_mv == 'dodge' and o_mv == 'ground attack':
        msg = gAttack_dodge(o, p)
    elif p_mv == 'dodge' and o_mv == 'anti-air attack':
        msg = aAttack_dodge(o, p)
    elif p_mv == 'dodge' and o_mv == 'signature attack':
        msg = sAttack_dodge(o, p)
    elif p_mv == 'dodge' and o_mv == 'dodge':
        msg = dodge_dodge(p, o)
    elif p_mv == 'dodge' and o_mv == 'jump':
        msg = dodge_jump(p, o)
    elif p_mv == 'dodge' and o_mv == 'charge':
        msg = dodge_charge(p, o)

    elif p_mv == 'jump' and o_mv == 'ground attack':
        msg = gAttack_jump(o, p)
    elif p_mv == 'jump' and o_mv == 'anti-air attack':
        msg = aAttack_jump(o, p)
    elif p_mv == 'jump' and o_mv == 'signature attack':
        msg = sAttack_jump(o, p)
    elif p_mv == 'jump' and o_mv == 'dodge':
        msg = dodge_jump(o, p)
    elif p_mv == 'jump' and o_mv == 'jump':
        msg = jump_jump(p, o)
    elif p_mv == 'jump' and o_mv == 'charge':
        msg = jump_charge(p, o)

    elif p_mv == 'charge' and o_mv == 'ground attack':
        msg = gAttack_charge(o, p)
    elif p_mv == 'charge' and o_mv == 'anti-air attack':
        msg = aAttack_charge(o, p)
    elif p_mv == 'charge' and o_mv == 'signature attack':
        msg = sAttack_charge(o, p)
    elif p_mv == 'charge' and o_mv == 'dodge':
        msg = dodge_charge(o, p)
    elif p_mv == 'charge' and o_mv == 'jump':
        msg = jump_charge(o, p)
    elif p_mv == 'charge' and o_mv == 'charge':
        msg = charge_charge(o, p)

    return msg


def gAttack_gAttack(p, o):
    p_chance = 75 + (p.dex + p.spd - 10) * 2
    o_chance = 75 + (o.dex + o.spd - 10) * 2
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
        return f"Both players missed their ground attack!"


def gAttack_aAttack(p, o):
    dmg = p.attack(o)
    return f"{p.username} hit {o.username} for **{dmg}** damage!"


def gAttack_sAttack(p, o):
    dmg = o.signature_attack(p)
    return f"{o.username}'s signature attack hit {p.username} for **{dmg}** damage!"


def gAttack_dodge(p, o):
    o.add_dodge_cooldown()
    punish_chance = ((o.dex + o.spd) / (p.dex + p.spd + o.dex + o.spd)) * 100 * 1.2
    rand = randint(1, 100)
    if rand <= punish_chance:
        dmg = o.attack(p)
        return f"{o.username} dodged {p.username}'s ground attack "\
               f"and punished it for **{dmg}** damage!"
    else:
        return f"{o.username} dodged {p.username}'s ground attack "\
               f"but failed to punish the attack."


def gAttack_jump(p, o):
    punish_chance = ((o.dex + o.spd) / (p.dex + p.spd + o.dex + o.spd)) * 100 * 0.7
    rand = randint(1, 100)
    if rand <= punish_chance:
        dmg = o.attack(p)
        return f"{o.username} jumped over {p.username}'s ground attack "\
               f"and punished it for **{dmg}** damage!"
    else:
        return f"{o.username} jumped over {p.username}'s ground attack "\
               f"but failed to punish the attack."


def gAttack_charge(p, o):
    dmg = p.attack(o)
    return f"{p.username} hit {o.username} for **{dmg}** damage! "\
           f"{o.username} gained 0 charge."


def aAttack_aAttack(p, o):
    return f"Both players missed their anti-air attack!"


def aAttack_sAttack(p, o):
    dmg = o.signature_attack(p)
    return f"{o.username}'s signature attack hit {p.username} for **{dmg}** damage!"


def aAttack_dodge(p, o):
    o.add_dodge_cooldown()
    punish_chance = ((o.dex + o.spd) / (p.dex + p.spd + o.dex + o.spd)) * 100 * 1.2
    rand = randint(1, 100)
    if rand <= punish_chance:
        dmg = o.attack(p)
        return f"{o.username} dodged {p.username}'s anti-air attack "\
               f"and punished it for **{dmg}** damage!"
    else:
        return f"{o.username} dodged {p.username}'s anti-air attack "\
               f"but failed to punish the attack."


def aAttack_jump(p, o):
    dmg = p.attack(o)
    return f"{p.username}'s anti-air attack caught {o.username}'s jump for **{dmg}** damage!"


def aAttack_charge(p, o):
    dmg = p.attack(o)
    return f"{p.username} hit {o.username} for **{dmg}** damage! "\
           f"{o.username} gained 0 charge."


def sAttack_sAttack(p, o):
    p_dmg = p.signature_attack(o)
    o_dmg = o.signature_attack(p)
    return f"{p.username}'s signature attack hit {o.username} for **{p_dmg}** damage!\n"\
           f"{o.username}'s signature attack hit {p.username} for **{o_dmg}** damage!"


def sAttack_dodge(p, o):
    o.add_dodge_cooldown()
    punish_chance = ((o.dex + o.spd) / (p.dex + p.spd + o.dex + o.spd)) * 100 * 1.2
    rand = randint(1, 100)
    if rand <= punish_chance:
        dmg = o.attack(p)
        return f"{o.username} dodged {p.username}'s signature attack "\
               f"and punished it for **{dmg}** damage!"
    else:
        return f"{o.username} dodged {p.username}'s signature attack "\
               f"but failed to punish the attack."


def sAttack_jump(p, o):
    dmg = p.signature_attack(o)
    return f"{p.username}'s signature attack caught {o.username}'s jump for **{dmg}** damage!"


def sAttack_charge(p, o):
    dmg = p.signature_attack(o)
    return f"{p.username}'s signature attack hit {o.username} for **{dmg}** damage! "\
           f"{o.username} gained 0 charge."


def dodge_dodge(p, o):
    p.add_dodge_cooldown()
    o.add_dodge_cooldown()
    return f"Both players dodged... nothing!"


def dodge_jump(p, o):
    p.add_dodge_cooldown()
    return f"{p.username} dodged and {o.username} jumped."


def dodge_charge(p, o):
    p.add_dodge_cooldown()
    o.add_charge()
    return f"{o.username} gained 1 charge!"


def jump_jump(p, o):
    return f"Both players jumped."


def jump_charge(p, o):
    o.add_charge()
    return f"{o.username} gained 1 charge!"


def charge_charge(p, o):
    p.add_charge()
    o.add_charge()
    return f"Both players gained 1 charge!"
