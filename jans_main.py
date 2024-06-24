import numpy as np
from bokeh.plotting import figure, show, output_notebook, output_file, save
from bokeh.layouts import gridplot
from bokeh.io.export import export_png
from tabulate import tabulate

output_notebook()

dice_red = [1, 2, 3, 4, 5, 6]
dice_black = [6, 6, 8, 10, 10, 12]

# Helden und ihre Attribute
heroes = {
    "Krieger:in": {
        "strength": 6,
        "no_dices_by_willpower": {6: 2, 13: 3, 14: 4},
        "willpower_start": 14,
        "dice": dice_red,
    },
    "Bogenschütz:in": {
        "strength": 5,
        "no_dices_by_willpower": {6: 3, 13: 4, 14: 5},
        "willpower_start": 14,
        "dice": dice_red,
    },
    "Zauber:in": {
        "strength": 4,
        "no_dices_by_willpower": {6: 1, 13: 1, 14: 1},
        "willpower_start": 14,
        "dice": dice_red,
    },
    "Zwerg:in": {
        "strength": 7,
        "no_dices_by_willpower": {6: 1, 13: 2, 14: 3},
        "willpower_start": 14,
        "dice": dice_red,
    },
}

# Gegner und ihre Attribute
enemies = {
    "Gor": {
        "strength": 2,
        "willpower_start": 4,
        "no_dices_by_willpower": {4: 2},
        "dice": dice_red,
    },
    "Skral": {
        "strength": 6,
        "willpower_start": 6,
        "no_dices_by_willpower": {6: 2},
        "dice": dice_red,
    },
    "Wardrak": {
        "strength": 10,
        "willpower_start": 7,
        "no_dices_by_willpower": {6: 1, 7: 2},
        "dice": dice_black,
    },
    "Troll": {
        "strength": 14,
        "willpower_start": 12,
        "no_dices_by_willpower": {2: 1, 12: 3},
        "dice": dice_red,
    },
}


def roll_dice(dice_array, num_dice):
    return [np.random.choice(dice_array) for _ in range(num_dice)]


# Funktion zur Simulation einer Kampfrunde
def simulate_round(
    hero_strength,
    hero_dice,
    hero_dice_count,
    hero_wp,
    enemy_strength,
    enemy_dice,
    enemy_dice_count,
    enemy_wp,
):
    hero_dice_rolls = roll_dice(hero_dice, hero_dice_count)
    hero_roll_sum = max(hero_dice_rolls) + hero_strength

    enemy_dice_rolls = roll_dice(enemy_dice, enemy_dice_count)
    no_max = enemy_dice_rolls.count(max(enemy_dice_rolls))
    enemy_roll_sum = no_max * max(enemy_dice_rolls) + enemy_strength

    if hero_roll_sum > enemy_roll_sum:
        damage = hero_roll_sum - enemy_roll_sum
        enemy_wp -= damage
    elif enemy_roll_sum > hero_roll_sum:
        damage = enemy_roll_sum - hero_roll_sum
        hero_wp -= damage

    return hero_wp, enemy_wp


def determine_dice_count(willpower, no_dices_by_willpower):
    for wp_threshold in sorted(no_dices_by_willpower.keys()):
        if willpower <= wp_threshold:
            return no_dices_by_willpower[wp_threshold]
    raise ValueError("No dice count found for willpower")


# Funktion zur Simulation eines Kampfes mit nur einer Person
# Geht davon aus, dass der Kampf nicht über den Verlust eines SP hinaus geführt wird
# Er beginnt immer am Anfang eines Tages (d.h. max 7 Runden)
# Zudem gibt es keine zusätlichen Gegenstände (z.B. Helm)
def simulate_battle(
    hero_strength,
    hero_initial_wp,
    hero_dice,
    hero_dice_count,
    enemy_strength,
    enemy_initial_wp,
    enemy_dice,
    enemy_dice_count,
    simulations=10000,
):
    hero_wins = 0
    no_winner = 0
    enemy_wins = 0

    for _ in range(simulations):
        hero_wp = hero_initial_wp
        enemy_wp = enemy_initial_wp
        left_days = 7

        while hero_wp > 0 and enemy_wp > 0:
            hero_wp, enemy_wp = simulate_round(
                hero_strength,
                hero_dice,
                hero_dice_count,
                hero_wp,
                enemy_strength,
                enemy_dice,
                enemy_dice_count,
                enemy_wp,
            )

            left_days -= 1
            if left_days == 0:
                break

        if hero_wp > 0 and enemy_wp > 0:
            no_winner += 1
        elif hero_wp > 0 and enemy_wp <= 0:
            hero_wins += 1
        elif enemy_wp > 0 and hero_wp <= 0:
            enemy_wins += 1
        else:
            raise ValueError("Unexpected outcome")

    win_probability = hero_wins / simulations
    no_winner_probability = no_winner / simulations
    enemy_wins_probability = enemy_wins / simulations
    return win_probability, no_winner_probability, enemy_wins_probability


# Simulationsergebnisse speichern
results = {}

# Simulation für jede Held:in gegen jeden Gegner
for hero_name, hero_attr in heroes.items():
    results[hero_name] = {}
    for enemy_name, enemy_attr in enemies.items():
        hero_wp = hero_attr["willpower_start"]
        enemy_wp = enemy_attr["willpower_start"]
        hero_dice_count = determine_dice_count(
            hero_wp, hero_attr["no_dices_by_willpower"]
        )
        enemy_dice_count = determine_dice_count(
            enemy_wp, enemy_attr["no_dices_by_willpower"]
        )
        win_prob, no_win_prob, enemy_win_prob = simulate_battle(
            hero_attr["strength"],
            hero_wp,
            hero_attr["dice"],
            hero_dice_count,
            enemy_attr["strength"],
            enemy_wp,
            enemy_attr["dice"],
            enemy_dice_count,
        )
        results[hero_name][
            f"{enemy_name} (SP: {enemy_attr['strength']}, WP: {enemy_attr['willpower_start']})"
        ] = {
            "win": win_prob,
            "no_win": no_win_prob,
            "enemy_win": enemy_win_prob,
        }


# Ergebnisse anzeigen
for hero_name, hero_results in results.items():
    print(
        f"Ergebnisse für {hero_name} (SP: {heroes[hero_name]['strength']}, WP: {heroes[hero_name]['willpower_start']})"
    )
    table = []
    for enemy_info, win_prob in hero_results.items():
        table.append(
            [
                enemy_info,
                f"{win_prob['win']:.2%}",
                f"{win_prob['no_win']:.2%}",
                f"{win_prob['enemy_win']:.2%}",
            ]
        )

    headers = ["Gegner", "Siegchance", "Unentschieden", "Niederlage"]
    print(tabulate(table, headers=headers, tablefmt="grid"))
    print()  # Add a blank line between each hero's results


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
