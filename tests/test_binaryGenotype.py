from test_utils import *
import random, pytest, copy

iterations = 250
boardsize = 100

class TestUniformRecombination:
	def test_length(self):
		for _ in range(iterations):
			size = random.randint(2, boardsize * 5)
			parents = random_pop(2, size)
			child = parents[0].recombine(parents[1], 'uniform')
			assert len(child.gene) == size

	#each loci is selected uniform randomly
	def test_is_uniform(self):
		expected_lower_bound = 0.2
		expected_upper_bound = 0.8
		out_of_bounds = 0
		m_iterations = iterations * 100
		ones = all_ones(boardsize)
		zeroes = all_zeroes(boardsize)
		hits = [0 for _ in range(boardsize)]
		for _ in range(m_iterations):
			if random.randint(0, 1) == 0:
				child = ones.recombine(zeroes, 'uniform')
			else:
				child = zeroes.recombine(ones, 'uniform')
			num_ones = 0
			for i in range(len(child.gene)):
				if child.gene[i] == 1:
					num_ones += 1
					hits[i] += 1
			ratio = num_ones / boardsize
			if ratio < expected_lower_bound or ratio > expected_upper_bound:
				out_of_bounds += 1
		assert out_of_bounds < 5
		min_bound = 0.4
		max_bound = 0.6
		for hit in hits:
			ratio = hit / m_iterations
			assert ratio < max_bound
			assert ratio > min_bound

	#parents are not modified at all by recombination
	def test_parents_unmodified(self):
		for _ in range(iterations):
			size = random.randint(2, boardsize * 5)
			parents = random_pop(2, size)
			random_fitness(parents)
			copies = [copy.deepcopy(x) for x in parents]
			child = parents[0].recombine(parents[1], 'uniform')
			assert same_object(copies[0], parents[0])
			assert same_object(copies[1], parents[1])

class Test1PointCrossoverRecombination:
	def test_length(self):
		for _ in range(iterations):
			size = random.randint(2, boardsize * 5)
			parents = random_pop(2, size)
			child = parents[0].recombine(parents[1], '1-point crossover')
			assert len(child.gene) == size

	#the resulting child has one distinct crossover point
	def test_has_1_point(self):
		for _ in range(iterations):
			ones = all_ones(boardsize)
			zeroes = all_zeroes(boardsize)
			if random.randint(0, 1) == 0:
				child = ones.recombine(zeroes, '1-point crossover')
			else:
				child = zeroes.recombine(ones, '1-point crossover')
			assert len(get_cross_points(child.gene)) == 1

	#the crossover point is selected uniformly out of all valid loci
	def test_point_is_uniformly_selected(self):
		hits = {x:0 for x in range(boardsize)}
		m_iterations = iterations * 100
		ones = all_ones(boardsize)
		zeroes = all_zeroes(boardsize)
		for _ in range(m_iterations):
			if random.randint(0, 1) == 0:
				child = ones.recombine(zeroes, '1-point crossover')
			else:
				child = zeroes.recombine(ones, '1-point crossover')
			hits[get_cross_points(child.gene)[0]] += 1
		expected = m_iterations / (boardsize - 1)
		expected_lower_bound = expected - (expected * 0.2)
		expected_upper_bound = expected + (expected * 0.2)
		min_bound = expected - (expected * 0.4)
		max_bound = expected + (expected * 0.4)
		assert hits[0] == 0
		hits[0] = expected
		out_of_bounds = 0
		for hit in hits.values():
			assert hit < max_bound
			assert hit > min_bound
			if hit > expected_upper_bound or hit < expected_lower_bound:
				out_of_bounds += 1
		assert out_of_bounds < boardsize / 20

	#parents are not modified at all by recombination
	def test_parents_unmodified(self):
		for _ in range(iterations):
			size = random.randint(2, boardsize * 5)
			parents = random_pop(2, size)
			random_fitness(parents)
			copies = [copy.deepcopy(x) for x in parents]
			child = parents[0].recombine(parents[1], '1-point crossover')
			assert same_object(copies[0], parents[0])
			assert same_object(copies[1], parents[1])

class TestMutation:
	def test_length(self):
		for _ in range(iterations):
			size = random.randint(2, boardsize * 5)
			parents = random_pop(1, size)
			random_fitness(parents)
			child = parents[0].mutate()
			assert len(child.gene) == size

	#mutation produces changes
	def test_sometimes_changes(self):
		passed = False
		for _ in range(iterations):
			size = random.randint(2, boardsize * 5)
			parents = random_pop(1, size)
			random_fitness(parents)
			child = parents[0].mutate()
			if distance(child.gene, parents[0].gene) > 0:
				passed = True
				break
		assert passed

	# #mutation produces no changes with mutation rate 0
	# def test_no_changes(self):
		# for _ in range(iterations):
			# size = random.randint(2, boardsize * 5)
			# parents = random_pop(1, size)
			# random_fitness(parents)
			# child = parents[0].mutate(**{'mutation_rate':0})
			# assert distance(child.gene, parents[0].gene) == 0

	# #mutation flips every locus with mutation rate 1
	# def test_all_changes(self):
		# for _ in range(iterations):
			# size = random.randint(2, boardsize * 5)
			# parents = random_pop(1, size)
			# random_fitness(parents)
			# child = parents[0].mutate(**{'mutation_rate':1})
			# assert distance(child.gene, parents[0].gene) == size

	#each locus has the same independent chance of mutating
	def test_no_locus_bias(self):
		hits = [0 for _ in range(boardsize)]
		m_iterations = iterations * 100
		for _ in range(m_iterations):
			parents = random_pop(1, boardsize)
			random_fitness(parents)
			child = parents[0].mutate()
			for i in range(boardsize):
				if parents[0].gene[i] != child.gene[i]:
					hits[i] += 1
		average_change = sum(hits) / len(hits)
		expected_lower_bound = average_change - average_change * 0.2
		expected_upper_bound = average_change + average_change * 0.2
		out_of_bounds = 0
		for locus in hits:
			if locus > expected_upper_bound or locus < expected_lower_bound:
				out_of_bounds += 1
		assert out_of_bounds < boardsize / 20

	# #amount of change is proportional to mutation rate
	# def test_accurate_rate(self):
		# rates = [0.1 * x for x in range(0, 11)]
		# for rate in rates:
			# diff = 0
			# for _ in range(iterations):
				# parents = random_pop(1, boardsize)
				# random_fitness(parents)
				# child = parents[0].mutate(**{'mutation_rate':rate})
				# diff += distance(parents[0].gene, child.gene)
			# diff = diff / iterations
			# assert diff / boardsize > rate - 0.05
			# assert diff / boardsize < rate + 0.05