# Class for brawlhalla duel
from random import uniform
from random import randint


class Brawler:
    def __init__(self, username, name, stats, weapons, skin, color, key):
        self.username = username
        self.name = name.capitalize()
        self.str = int(stats[0])
        self.dex = int(stats[1])
        self.defe = int(stats[2])
        self.spd = int(stats[3])
        self.weapons = weapons
        self.skin = skin.capitalize()
        self.color = color.capitalize()
        self.key = key
        self.total_hp = 30
        self.hp = 30
        self.stocks = 3
        self.dodge_cooldown = 0
        self.jump_count = 0
        # self.punish_chance = 0

    def attack(self, opponent):
        universal_dmg = 20
        raw_dmg = universal_dmg + ((self.str - 5) * 0.4)
        raw_dmg *= uniform(0.8, 1.2)
        final_dmg = raw_dmg - ((opponent.defe - 5) * 0.4)
        final_dmg = round(final_dmg, 1)
        opponent.hp -= final_dmg

        # give jump if hit in the air
        if opponent.jump_count != 0:
            opponent.jump_count -= 1

        return final_dmg

    def clash(self, opponent):
        universal_dmg = 10
        raw_dmg = universal_dmg + ((self.str - 5) * 0.2)
        raw_dmg *= uniform(0.9, 1.1)
        final_dmg = raw_dmg - ((opponent.defe - 5) * 0.2)
        final_dmg = round(final_dmg, 1)
        opponent.hp -= final_dmg
        return final_dmg

    def jump(self, opponent):
        universal_dodge_chance = 30
        raw_dodge_chance = universal_dodge_chance + (self.spd * 1.5)
        final_dodge_chance = raw_dodge_chance - (opponent.dex * 1.5)
        rand_num = randint(1, 100)
        if rand_num <= final_dodge_chance:
            return True
        return False

    # def win_priority(self, opponent):
        

    def update_stocks(self):
        if self.hp <= 0:
            self.stocks -= 1
            self.hp = self.total_hp
            return True
        return False

    def update_cooldown(self):
        if self.dodge_cooldown != 0:
            self.dodge_cooldown -= 1
        if self.jump_count == 3:
            self.jump_count = 0

    def add_dodge_cooldown(self):
        if self.jump_count == 0:
            self.dodge_cooldown += 2
            return "grounded"
        elif self.jump_count > 0:
            self.dodge_cooldown += 3
            return "aerial"

    def add_jump_count(self):
        self.jump_count += 1
        jumps_remaining = 3 - self.jump_count
        return jumps_remaining

    # def add_punish_chance(self):
    #     self.punish_chance += 50
