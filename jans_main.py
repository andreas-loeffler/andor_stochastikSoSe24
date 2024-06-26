from typing import Dict, List
import numpy as np
from bokeh.plotting import figure, show, output_notebook, output_file, save
from bokeh.layouts import gridplot
from bokeh.io.export import export_png
from tabulate import tabulate
from enum import Enum


class DiceColor(Enum):
    RED = [1, 2, 3, 4, 5, 6]
    BLACK = [6, 6, 8, 10, 10, 12]


class Objects(Enum):
    WITCH_POTION = "Witch Potion"
    HELMET = "Helmet"


class HeroName(Enum):
    WARRIOR = "Warrior"
    ARCHER = "Archer"
    WIZARD = "Wizard"
    DWARF = "Dwarf"


class EnemyName(Enum):
    GOR = "Gor"
    SKRAL = "Skral"
    WARDRAK = "Wardrak"
    TROLL = "Troll"


class Figure:
    def __init__(
        self,
        name: HeroName | EnemyName,
        strength: int,
        willpower: int,
        no_dices_by_willpower: Dict[int, int],
        dice_color: DiceColor,
    ):
        self.name = name
        self.strength = strength
        self.willpower = willpower
        self.no_dices_by_willpower = no_dices_by_willpower
        self.dice_color = dice_color

    def dice_count(self):
        for wp_threshold in sorted(self.no_dices_by_willpower.keys()):
            if self.willpower <= wp_threshold:
                return self.no_dices_by_willpower[wp_threshold]
        raise ValueError("No dice count found for willpower")


class Hero(Figure):
    def __init__(
        self,
        name: HeroName,
        strength: int,
        willpower: int,
        no_dices_by_willpower: Dict[int, int],
        list_of_objects: list[Objects] | None = None,
    ):
        super().__init__(
            name, strength, willpower, no_dices_by_willpower, DiceColor.RED
        )
        list_of_objects = list_of_objects if list_of_objects is not None else []
        self.has_helmet = Objects.HELMET in list_of_objects
        self.num_witch_potions = 2 if Objects.WITCH_POTION in list_of_objects else 0


class Enemy(Figure):
    def __init__(
        self,
        name: EnemyName,
        strength: int,
        willpower: int,
        no_dices_by_willpower: Dict[int, int],
        dice_color: DiceColor,
    ):
        super().__init__(name, strength, willpower, no_dices_by_willpower, dice_color)


def roll_dice(dice_array, num_dice) -> List[int]:
    return [np.random.choice(dice_array) for _ in range(num_dice)]


class Battle:
    def __init__(self, hero: Hero, enemy: Enemy, days_left: int = 7):
        self.hero = hero
        self.enemy = enemy
        self.days_left = days_left

    def use_object(self, hero_dice: List[int]) -> Objects | None:
        enemy_dice_cnt = self.enemy.dice_count()
        enemy_dice_color = self.enemy.dice_color.value
        avg_single_roll = sum(enemy_dice_color) / len(enemy_dice_color)

        if enemy_dice_cnt == 1:
            avg_enemy_roll = avg_single_roll
        elif enemy_dice_cnt == 2:
            prob2_same_dices = (
                1 / 6 if enemy_dice_color == DiceColor.RED.value else 10 / 36
            )  # 2x6, 1x8, 2x10, 1x12 -> (2/6)²+ (1/6)² + (2/6)² + (1/6)² = 10/36
            avg_enemy_roll = avg_single_roll + prob2_same_dices * avg_single_roll
        elif enemy_dice_cnt == 3:
            prob2_same_dices = (
                1 / 6 if enemy_dice_color == DiceColor.RED.value else 10 / 36
            )
            prob3_same_dices = (
                1 / 36 if enemy_dice_color == DiceColor.RED.value else 18 / 216
            )  # 2x6, 1x8, 2x10, 1x12 -> (2/6)³ + (1/6)³ + (2/6)³ + (1/6)³ = 18/216
            avg_enemy_roll = (
                avg_single_roll
                + prob2_same_dices * avg_single_roll
                + prob3_same_dices * avg_single_roll
            )
        else:
            raise ValueError("Unexpected number of enemy dices")

        if (  # Use witch potion if it increases the chance of winning
            self.hero.num_witch_potions > 0
            and max(hero_dice) + self.hero.strength > avg_enemy_roll
            and 2 * max(hero_dice) + self.hero.strength > avg_enemy_roll
        ):
            self.hero.num_witch_potions -= 1
            return Objects.WITCH_POTION

        if (
            self.hero.has_helmet
            and self.hero.name
            != HeroName.WIZARD  # Wizard and archer has no advantage from helmet
            and self.hero.name != HeroName.ARCHER
        ):
            return Objects.HELMET

        return None

    def simulate_round(self):
        hero_dice = roll_dice(self.hero.dice_color.value, self.hero.dice_count())
        use_object = self.use_object(hero_dice)
        if use_object == Objects.WITCH_POTION:
            hero_roll_sum = 2 * max(hero_dice) + self.hero.strength
        elif use_object == Objects.HELMET:
            count, value = max((hero_dice.count(i), i) for i in set(hero_dice))
            if (count * value) > max(hero_dice):
                hero_roll_sum = count * value + self.hero.strength
            else:
                hero_roll_sum = max(hero_dice) + self.hero.strength
        else:
            hero_roll_sum = max(hero_dice) + self.hero.strength

        enemy_dice = roll_dice(self.enemy.dice_color.value, self.enemy.dice_count())
        no_max = enemy_dice.count(max(enemy_dice))
        enemy_roll_sum = no_max * max(enemy_dice) + self.enemy.strength

        if hero_roll_sum > enemy_roll_sum:
            damage = hero_roll_sum - enemy_roll_sum
            self.enemy.willpower -= damage
        elif enemy_roll_sum > hero_roll_sum:
            damage = enemy_roll_sum - hero_roll_sum
            self.hero.willpower -= damage

    def run_simulation(self) -> HeroName | EnemyName | None:
        while (
            self.days_left > 0 and self.hero.willpower > 0 and self.enemy.willpower > 0
        ):
            self.simulate_round()
            self.days_left -= 1

        if self.hero.willpower > 0 and self.enemy.willpower <= 0:
            return self.hero.name
        elif self.enemy.willpower > 0 and self.hero.willpower <= 0:
            return self.enemy.name
        else:
            return None


def generate_hero(name: HeroName, objects: List[object] | None = None):
    if name == HeroName.WARRIOR:
        return Hero(HeroName.WARRIOR, 6, 14, {6: 2, 13: 3, 14: 4}, objects)
    elif name == HeroName.ARCHER:
        return Hero(HeroName.ARCHER, 5, 14, {6: 3, 13: 4, 14: 5}, objects)
    elif name == HeroName.WIZARD:
        return Hero(HeroName.WIZARD, 4, 14, {6: 1, 13: 1, 14: 1}, objects)
    elif name == HeroName.DWARF:
        return Hero(HeroName.DWARF, 7, 14, {6: 1, 13: 2, 14: 3}, objects)
    else:
        raise ValueError("Unexpected figure")


def generate_enemy(name: EnemyName):
    if name == EnemyName.GOR:
        return Enemy(EnemyName.GOR, 2, 4, {4: 2}, DiceColor.RED)
    elif name == EnemyName.SKRAL:
        return Enemy(EnemyName.SKRAL, 6, 6, {6: 2}, DiceColor.RED)
    elif name == EnemyName.WARDRAK:
        return Enemy(EnemyName.WARDRAK, 10, 7, {6: 1, 7: 2}, DiceColor.BLACK)
    elif name == EnemyName.TROLL:
        return Enemy(EnemyName.TROLL, 14, 12, {2: 1, 12: 3}, DiceColor.RED)
    else:
        raise ValueError("Unexpected figure")


def run_simulation(simulations: int = 10000, objects: List[Objects] | None = None):
    heroes = [
        HeroName.WARRIOR,
        HeroName.ARCHER,
        HeroName.WIZARD,
        HeroName.DWARF,
    ]

    enemies = [
        EnemyName.GOR,
        EnemyName.SKRAL,
        EnemyName.WARDRAK,
        EnemyName.TROLL,
    ]

    # generate a dictionary to store the results in the form of hero: {enemy: (hero_win_probabiliry, no_winner_probability, enemy_wins_probability)}

    results = {
        hero.value: {
            enemy.value: {
                "hero_wins": None,  # Initialize hero_wins with None
                "enemy_wins": None,  # Initialize enemy_wins with None
                "no_winner": None,  # Initialize no_winner with None
            }
            for enemy in enemies  # Loop through each enemy for the current hero
        }
        for hero in heroes  # Loop through each hero
    }

    for hero in heroes:
        for enemy in enemies:
            hero_wins = 0
            no_winner = 0
            enemy_wins = 0

            for _ in range(simulations):
                battle = Battle(generate_hero(hero, objects), generate_enemy(enemy))
                winner = battle.run_simulation()

                if winner is None:
                    no_winner += 1
                elif winner == hero:
                    hero_wins += 1
                elif winner == enemy:
                    enemy_wins += 1
                else:
                    raise ValueError("Unexpected outcome")

            results[hero.value][enemy.value]["hero_wins"] = hero_wins / simulations
            results[hero.value][enemy.value]["no_winner"] = no_winner / simulations
            results[hero.value][enemy.value]["enemy_wins"] = enemy_wins / simulations

    return results


# Funktion zur Simulation eines Kampfes mit nur einer Person
# Geht davon aus, dass der Kampf nicht über den Verlust eines SP hinaus geführt wird
# Er beginnt immer am Anfang eines Tages (d.h. max 7 Runden)
# Zudem gibt es keine zusätlichen Gegenstände (z.B. Helm)
if __name__ == "__main__":
    simulation_results = {}

    for objects in [None, [Objects.HELMET], [Objects.WITCH_POTION]]:
        used_objects = (
            "None" if objects is None else ", ".join([obj.value for obj in objects])
        )
        simulation_results[used_objects] = run_simulation(objects=objects)

    for objects, results in simulation_results.items():
        for hero, hero_results in results.items():
            print(f"Results for {hero} - used objects: {objects}:")
            table = []
            for enemy, enemy_results in hero_results.items():
                table.append(
                    [
                        enemy,
                        f"{enemy_results['hero_wins']:.2%}",
                        f"{enemy_results['no_winner']:.2%}",
                        f"{enemy_results['enemy_wins']:.2%}",
                    ]
                )

            headers = ["Enemy", "Hero Wins", "No Winner", "Enemy Wins"]
            print(tabulate(table, headers=headers, tablefmt="grid"))
            print()

"""
# Bokeh Plots generieren
plots = []
for hero_name, hero_results in results.items():
    x = list(hero_results.keys())
    y = list(hero_results.values())
    y = [i["win"] for i in y]
    p = figure(
        x_range=x, title=f"Siegchancen für {hero_name}", toolbar_location=None, tools=""
    )
    p.vbar(x=x, top=y, width=0.9)
    p.xgrid.grid_line_color = None
    p.y_range.start = 0
    p.y_range.end = 1
    p.xaxis.major_label_orientation = 1
    p.yaxis.axis_label = "Siegchance"
    plots.append(p)

grid = gridplot(plots, ncols=2)
show(grid)

# Speichern als HTML-Datei
output_file("andor_simulation_results.html")
save(grid)

# Exportiere das Grid als PNG-Datei
export_png(grid, filename="andor_simulation_results.png")
"""
