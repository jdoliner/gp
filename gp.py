#Module to use genetic programming to learn functions

import agents
import math
import lisp
import os
import popen2

initial_file = "composition.lisp"

def bell_payment(x, y):
	difference = x-y
	return 2 ** (- (difference ** 2))
max_payment = 1

class GP():
	project_name = None
	source_folder = None
	fifo = 'pyfifo'
	generation = 0
	population = []
	parallelizer = None
	evaluator = None
	grader = None
	breeder = None
	coder = None
	source = None
	bytecode = None
	population_size = 100
	generation_cap = 1000 #the number of generations we will run for
	
	#datasets should be a tuple of answers and data
	def __init__(self, project_name, initial, dataset):
		self.project_name = project_name
		self.source_folder = project_name + '_dir'
		os.system("mkdir " + self.source_folder)
		os.system("fifo " + self.fifo)
		
		self.population = initial
		self.required = "composition.lisp"
		data = dataset[0]
		answers = dataset[1]
		self.parallelizer = agents.Parallelizer(['pyscreen0', 'pyscreen1', 'pyscreen2', 'pyscreen3'], self.population, self.fifo)
		self.evaluator = agents.Evaluator(self.population, data, self.required, self.source_folder, self.parallelizer)
		self.grader = agents.Grader(self.population, answers, bell_payment, max_payment)
		self.breeder = agents.Breeder(self.population, self.population_size)
		self.coder = agents.Coder(self.population, self.required, self.source_folder)
		for agent in self.population:
			self.grader.pay(agent,1)
		self.breeder.refresh()
		self.update_population( self.breeder.breed() )
		
	def increment_generation(self):
		self.generation += 1
		self.evaluator.generation += 1
		self.grader.generation += 1
		self.breeder.generation += 1
		self.coder.generation += 1
		
	def update_population(self, new_population):
		self.population += new_population
		self.evaluator.population = new_population
		self.grader.population = new_population
		self.breeder.population += new_population
		self.coder.population = new_population
		
	def update_source(self, new_source):
		sourcecode = new_source[0]
		bytecode = new_source[1]
		self.source = sourcecode
		self.bytecode = bytecode
		self.evaluator.required = sourcecode
		self.coder.required = sourcecode
		
	def cycle(self):
		self.update_source( the_big_one.coder.code() )
		self.evaluator.evaluate()
		self.grader.grade()
		self.increment_generation()
		self.update_population( the_big_one.breeder.breed() )
		
	def run(self):
		while self.grader.final_answers == [] and self.generation < self.generation_cap:
			print "Generation: ", self.generation, "..." 
			self.cycle()
			print "MVP: ", self.grader.mvp
			
		print "Final answer: ", self.grader.final_answers

data = []
answers = []
for i in range(-10, 10):
	for j in range(-10, 10):
		data.append([i,j])
		answers.append( math.sqrt( i*i + j*j) )

plus = lisp.Function('plus', ['x','y'], 'built-in')
minus = lisp.Function('minus', ['x','y'], 'built-in')
mult = lisp.Function('mult', ['x','y'], 'built-in')
div = lisp.Function('div' , ['x','y'], 'built-in')
one = lisp.Function('one', [], 'built-in')

Plus = agents.Agent(plus)
Minus = agents.Agent(minus)
Times = agents.Agent(mult)
Div = agents.Agent(div)
One = agents.Agent(one)

initial_population = [Plus, Minus, Times, Div, One]
the_big_one = GP('the_big_one', initial_population, [data,answers])

the_big_one.run()
