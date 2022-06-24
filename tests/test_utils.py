import pytest, random, os, sys, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
from binaryGenotype import binaryGenotype

def random_pop(n, boardsize):
	return binaryGenotype.initialization(n, length=boardsize)
	
def random_fitness(pop, minimum=-1000, maximum=1000):
	for i in range(len(pop)):
		pop[i].fitness = random.uniform(minimum, maximum)
	
def standard_fitness(pop, minimum=-1000, maximum=1000):
	fitness = random.uniform(minimum, maximum)
	for i in range(len(pop)):
		pop[i].fitness = fitness

def all_ones(boardsize):
	ret = binaryGenotype()
	ret.gene = [1 for _ in range(boardsize)]
	return ret

def all_zeroes(boardsize):
	ret = binaryGenotype()
	ret.gene = [0 for _ in range(boardsize)]
	return ret

def get_cross_points(gene):
	crosses = []
	run = gene[0]
	for i in range(1, len(gene)):
		if gene[i] != run:
			run = gene[i]
			crosses.append(i)
	return crosses

def same_object(obj1, obj2):
	if dir(obj1) != dir(obj2):
		return False
	dir1 = obj1.__dict__
	dir2 = obj2.__dict__
	for attr in dir1:
		if dir1[attr] != dir2[attr]:
			return False
	return True

def distance(genes1, genes2):
	assert len(genes1) == len(genes2)
	diff = 0
	for i in range(len(genes1)):
		if genes1[i] != genes2[i]:
			diff += 1
	return diff