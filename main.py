import random
from bokeh.plotting import figure, show
from bokeh.io import export_png
from bokeh.models import ColumnDataSource, Legend
from bokeh.transform import dodge

# Klassen für Helden und Gegner
class Held:
    def __init__(self, name, staerke, willenspunkte):
        self.name = name
        self.staerke = staerke
        self.willenspunkte = willenspunkte

    def kaempfen(self, gegner):
        wuerfel_ergebnisse = [random.randint(1, 6) for _ in range(self.willenspunkte)]
        gesamt_staerke = self.staerke + sum(wuerfel_ergebnisse)
        return gesamt_staerke >= gegner.staerke

class Gegner:
    def __init__(self, name, staerke):
        self.name = name
        self.staerke = staerke

# Helden erstellen
chada = Held('Chada', 5, 3)  # Bogenschützin
thorn = Held('Thorn', 7, 2)  # Krieger
kram = Held('Kram', 6, 2)    # Zwerg
eara = Held('Eara', 4, 4)    # Zauberin

# Gegner erstellen
ork = Gegner('Ork', 8)
troll = Gegner('Troll', 12)

# Kampfsimulation
def kampf_simulation(held, gegner, simulations=1000):
    wins = 0
    for _ in range(simulations):
        if held.kaempfen(gegner):
            wins += 1
    return wins / simulations

# Entscheidungshilfe
def entscheidungshilfe(gegner):
    helden = [chada, thorn, kram, eara]
    ergebnisse = {held.name: held.kaempfen(gegner) for held in helden}
    bester_held = max(ergebnisse, key=ergebnisse.get)
    print(f"In der aktuellen Situation sollte {bester_held} gegen {gegner.name} antreten.")

# Plotting Funktion mit Bokeh
def plot_kampfergebnisse(helden, gegner, simulations=1000):
    ergebnisse = {gegner.name: {held.name: kampf_simulation(held, gegner, simulations) for held in helden} for gegner in gegner_list}
    
    held_namen = [held.name for held in helden]
    data = {'Helden': held_namen}
    
    for gegner_name, held_ergebnisse in ergebnisse.items():
        data[gegner_name] = list(held_ergebnisse.values())

    source = ColumnDataSource(data=data)
    
    p = figure(x_range=held_namen, height=400, title="Siegrate gegen Gegner",
               toolbar_location=None, tools="")
    legend_it = []
    colors = ["#c9d9d3", "#718dbf"]
    width = 0.25

    for i, gegner_name in enumerate(gegner_list):
        p.vbar(x=dodge('Helden', width * i, range=p.x_range), top=gegner_name.name, width=width, source=source,
               color=colors[i])
        legend_it.append((gegner_name.name, [p.renderers[i]]))
    
    legend = Legend(items=legend_it, location=(0, 0))
    p.x_range.range_padding = 0.1
    p.xgrid.grid_line_color = None
    p.y_range.start = 0
    p.y_range.end = 1
    p.xaxis.axis_label = "Helden"
    p.yaxis.axis_label = "Siegrate"
    p.add_layout(legend, 'right')
    
    show(p)
    export_png(p, filename="kampfergebnisse.png")

# Helden- und Gegnerlisten
helden = [chada, thorn, kram, eara]
gegner_list = [ork, troll]

# Kampfergebnisse plotten
plot_kampfergebnisse(helden, gegner_list)
