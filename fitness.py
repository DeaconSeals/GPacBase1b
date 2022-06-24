import time
from collections import deque
import gpac
import random
import statistics
import staticAgents

def manhattan_distance(location0, location1):
	'''calculate the Manhattan distance between two input points'''
	return sum([abs(coord[0]-coord[1]) for coord in zip(list(location0),list(location1))]) # overkill

def translate_gene(genotype, height, width):
	'''translate the input 1 dimensional genotype into a 2 dimensional map'''
	assert len(genotype) == height*width, f'ERROR: EXPECTED GENOTYPE OF LENGTH {height*width} BUT GOT {len(genotype)}'
	maze = [[0 for __ in range(height)] for _ in range(width)]
	for i in range(len(genotype)):
		x, y = i%width, i//width
		maze[x][y] = genotype[i]
	return maze

def reachable_cells(maze, start):
	'''Form a set of all reachable cells from a starting location using breadth-first graph search.

	   Returns a set of reachable locations from the starting location.'''
	directions = ((0,-1), (1,0), (0,1), (-1,0))
	visited = {start}
	frontier = deque()
	frontier.append(start)
	while frontier:
		x_base, y_base = frontier.popleft()
		for x_shift, y_shift in directions:
			x, y = x_base+x_shift, y_base+y_shift
			if 0 <= x < len(maze) and 0 <= y < len(maze[x]) and maze[x][y]==0 and (x,y) not in visited:
				frontier.append((x,y))
				visited.add((x,y))
	return visited

def repair_unreachable_cells(maze, start):
	'''Make all unreachable cells walls so pills and fruit aren't erroneously spawned.

	   Returns a modified map and the number of repairs performed.'''
	repairs = 0
	reachable = reachable_cells(maze, start)
	for x in range(len(maze)):
		for y in range(len(maze[x])):
			if (x,y) not in reachable and maze[x][y] == 0:
				maze[x][y] = 1
				repairs += 1
	return maze, repairs

def repair_map(maze):
	'''Repair map by connecting player spawn locations and filling in unreachable cells.
	   
	   Returns a modified map and the number of repair operations performed.'''
	pac_spawn = (0, len(maze[0])-1)
	ghost_spawn = (len(maze)-1, 0)
	repairs = 0
	# repair if walls are in spawn locations
	if maze[pac_spawn[0]][pac_spawn[1]] == 1:
		maze[pac_spawn[0]][pac_spawn[1]] = 0
		repairs += 1
	if maze[ghost_spawn[0]][ghost_spawn[1]] == 1:
		maze[ghost_spawn[0]][ghost_spawn[1]] = 0
		repairs += 1
	
	# identify if ghost spawn is reachable from pac-man spawn
	pac_reachable = reachable_cells(maze, pac_spawn)
	if ghost_spawn not in pac_reachable:
		# calculate nearest points reachable from both pac-man and ghost spawns
		ghost_reachable = reachable_cells(maze, ghost_spawn)
		nearest_points = (pac_spawn, ghost_spawn)
		shortest_distance = manhattan_distance(*nearest_points)
		for pac_point in list(pac_reachable):
			for ghost_point in list(ghost_reachable):
				distance = manhattan_distance(pac_point, ghost_point)
				if distance < shortest_distance:
					nearest_points = (pac_point, ghost_point)
		point0, point1 = nearest_points
		x0, y0 = point0
		x1, y1 = point1
		# remove walls to form a rectangular tunnel between two nearest reachable points
		for x in range(min(x0, x1), max(x0, x1)+1):
			if maze[x][y0] == 1:
				maze[x][y0] = 0
				repairs += 1
			if maze[x][y1] == 1:
				maze[x][y1] = 0
				repairs += 1
		for y in range(min(y0, y1), max(y0, y1)+1):
			if maze[x0][y] == 1:
				maze[x0][y] = 0
				repairs += 1
			if maze[x1][y] == 1:
				maze[x1][y] = 0
				repairs += 1
	# repair unreachable cells (given existing modifications)
	maze, access_repairs = repair_unreachable_cells(maze, pac_spawn)
	repairs += access_repairs
	return maze, repairs

def repair_and_test_map(genotype, height, width, return_repair_count = False, agent_type='pill', ghost_type='wander', samples=5, **kwargs):
	'''Fitness function that takes a linear map description, translates it into 2D, repairs the map, and plays
	   and plays a configurable number of games with a static agent strategy. 

	   Returns negative average pac-man score, the log of the game with the score nearest the mean, and 
	   (optionally) the number of repairs made.'''
	game_map = translate_gene(genotype, height, width)
	game_map, num_repairs = repair_map(game_map)
	game = gpac.GPacGame(game_map, **kwargs)
	scores = list()
	logs = list()
	# select agent strategy
	if agent_type == 'pill':
		agent_class = staticAgents.shortestPathPillAgent
	elif agent_type == 'fruit':
		agent_class = staticAgents.shortestPathFruitAgent
	elif agent_type == 'avoid':
		agent_class = staticAgents.AvoidingPacmanAgent
	else:
		raise ValueError(f"{agent_type} is not a known type of Pac-man agent.")
	# select ghost strategy
	if ghost_type == 'wander':
		ghost_class = staticAgents.RandomGhostAgent
	elif ghost_type == 'chase':
		ghost_class = staticAgents.ChasingGhostAgent
	else:
		raise ValueError(f"{ghost_type} is not a known type of ghost agent.")
	# play multiple games against agent
	for i in range(samples):
		agent = agent_class()
		ghosts = {player: ghost_class() for player in game.players if 'm' not in player}
		if i > 0:
			game.reset()
		
		while not game.gameover:
			# select pac-man action using provided strategy
			game.register_action(agent.select_action(game))
			# select ghost actions using provided strategy
			for player in game.players:
				if player != 'm':
					game.register_action(ghosts[player].select_action(game, player), player)
			game.step()
		scores.append(game.score)
		logs.append(game.log)
	average_score = statistics.mean(scores)
	
	# calculate deviation from mean for all games
	score_variances = [abs(average_score-score) for score in scores]
	representative_score = min(score_variances)
	representative_log = None
	for sample in range(len(logs)):
		# get log of game with score nearest the mean
		if score_variances[sample] == representative_score:
			representative_log = logs[sample]
	# optionally return number of repairs
	if return_repair_count:
		return -average_score, representative_log, num_repairs
	else:
		return -average_score, representative_log
