import numpy as np
from bokeh.plotting import figure, show, output_notebook, output_file, save
from bokeh.layouts import gridplot
from bokeh.io.export import export_png

output_notebook()

# Funktion zur Simulation einer Kampfrunde
def simulate_round(hero_strength, hero_dice, hero_wp, enemy_strength, enemy_dice, enemy_wp):
    hero_roll = sum(np.random.randint(1, 7) for _ in range(hero_dice)) + hero_strength
    enemy_roll = sum(np.random.randint(1, 7) for _ in range(enemy_dice)) + enemy_strength

    if hero_roll > enemy_roll:
        damage = hero_roll - enemy_roll
        enemy_wp -= damage
    elif enemy_roll > hero_roll:
        damage = enemy_roll - hero_roll
        hero_wp -= damage

    return hero_wp, enemy_wp

# Funktion zur Simulation eines Kampfes
def simulate_battle(hero_strength, hero_initial_wp, hero_dice, enemy_strength, enemy_initial_wp, enemy_dice, simulations=10000):
    hero_wins = 0

    for _ in range(simulations):
        hero_wp = hero_initial_wp
        enemy_wp = enemy_initial_wp

        while hero_wp > 0 and enemy_wp > 0:
            hero_wp, enemy_wp = simulate_round(hero_strength, hero_dice, hero_wp, enemy_strength, enemy_dice, enemy_wp)

        if hero_wp > 0:
            hero_wins += 1

    win_probability = hero_wins / simulations
    return win_probability

# Helden und ihre Attribute
heroes = {
    "Krieger:in": {"strength": 6, "willpower": [7, 14, 20], "dice": [2, 3, 4]},
    "Bogenschütz:in": {"strength": 5, "willpower": [6, 13, 18], "dice": [2, 3, 4]},
    "Zauber:in": {"strength": 4, "willpower": [5, 10, 15], "dice": [2, 3, 4]},
    "Zwerg:in": {"strength": 7, "willpower": [8, 16, 21], "dice": [2, 3, 4]},
}

# Gegner und ihre Attribute
enemies = {
    "Gor": {"strength": 6, "willpower": 5, "dice": 1},
    "Skral": {"strength": 8, "willpower": 10, "dice": 2},
    "Troll": {"strength": 10, "willpower": 15, "dice": 3},
}

# Simulationsergebnisse speichern
results = {}

# Simulation für jede Held:in gegen jeden Gegner
for hero_name, hero_attr in heroes.items():
    results[hero_name] = {}
    for enemy_name, enemy_attr in enemies.items():
        for i, wp in enumerate(hero_attr["willpower"]):
            hero_dice = hero_attr["dice"][i]
            win_prob = simulate_battle(
                hero_attr["strength"], wp, hero_dice,
                enemy_attr["strength"], enemy_attr["willpower"], enemy_attr["dice"]
            )
            results[hero_name][f"{enemy_name} (WP: {wp})"] = win_prob

# Ergebnisse anzeigen
for hero_name, hero_results in results.items():
    print(f"Ergebnisse für {hero_name}:")
    for enemy_info, win_prob in hero_results.items():
        print(f"  Gegen {enemy_info}: Siegchance = {win_prob:.2%}")
    print()

# Bokeh Plots generieren
plots = []
for hero_name, hero_results in results.items():
    x = list(hero_results.keys())
    y = list(hero_results.values())
    p = figure(x_range=x, title=f"Siegchancen für {hero_name}",
               toolbar_location=None, tools="")
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
