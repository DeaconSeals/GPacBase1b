from test_utils import *
import random, pytest, copy, os, sys, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
from snakeeyes import readConfig
from selection import *
import baseEvolution as evo

config = readConfig('./configs/vanilla_config.txt', globalVars=globals(), localVars=locals())
iterations = 25

class TestChildGeneration:
	def test_length(self):
		ea = evo.baseEvolutionPopulation(**config['EA_configs'], **config)
		ea.mutation_rate = 0.5
		ea.parent_selection = uniform_random_selection
		ea.survival_selection = truncation
		for _ in range(iterations):
			ea.population = random_pop(random.randint(2, 500), random.randint(2, 500))
			random_fitness(ea.population)
			ea.mu = len(ea.population)
			ea.num_children = random.randint(1, 500)
			assert len(ea.generate_children()) == ea.num_children
	
	#child generation has no impact on the population
	def test_unmodified_parents(self):
		ea = evo.baseEvolutionPopulation(**config['EA_configs'], **config)
		ea.mutation_rate = 0.5
		ea.parent_selection = uniform_random_selection
		ea.survival_selection = truncation
		for _ in range(iterations):
			ea.population = random_pop(random.randint(2, 500), random.randint(2, 500))
			random_fitness(ea.population)
			ea.mu = len(ea.population)
			ea.num_children = random.randint(1, 500)
			copies = copy.deepcopy(ea.population)
			children = ea.generate_children()
			for i in range(len(copies)):
				assert same_object(ea.population[i], copies[i])