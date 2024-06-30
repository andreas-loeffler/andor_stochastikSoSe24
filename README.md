# Andor simulation

The [simulation.py](./simulation.py) script simulates battles between heroes and enemies of the Andor board game. The simulation is based on the rules of the game and the probabilities of the dice rolls.

## Requirements
- Python 3.10.12
- numpy
- tabulate
- bokeh

## Constraints
* Each hero and enemy start a fight with their initial willpower and strength
* A hero can only fight alone and not in a group with other heroes
* Each battle starts at the beginning of the day (maximum of 7 rounds)
* A battle ends when the hero or the enemy has no more willpower left

## Simulation
Each battle between a hero and an enemy is simulated 10000 times. 
