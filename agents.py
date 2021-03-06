import lisp
import datetime
import time
import random
import copy
import os
from math import floor

__all__ = ["Derived", "Agent", "Parallelizer", "Evaluator", "Grader", "Breeder", "Coder"]

as_string = True

#returns the number of uniq elements in a list
def uniq(list):
	dictionary = {}
	for element in list:
		dictionary[element] = True
	return len(dictionary)

class Derived(lisp.Function):
	name = None
	unpinchedname = None #the function is firsted implemented in an unpinched version and given this name
	base_function = None
	complist = [] # a list of functions and None
	pinchlist = [] #defines the pinching of the function
	complistsymbol = 'complist' # the symbol used in the lisp code to represent the composition list
	pinchlistsymbol = 'pinchlist' #ditto for the pinchlist
	argcount = 0
	
	def __init__(self, name, base_function, complist, pinchlist):
		assert len(complist) == base_function.argcount
		self.name = name
		self.unpinchedname = name + '_unpinched'
		self.base_function = base_function
		self.complist = complist
		self.pinchlist = pinchlist
		self.complistsymbol += ( '_' + name )
		self.pinchlistsymbol += ( '_' + name )
		#these initializations are for safety incase someone reinitializes
		self.argcount = 0
		for i in complist:
			if(isinstance(i, lisp.Function)):
				self.argcount += i.argcount
			else:
				assert i == None
				self.argcount += 1
				
			if self.pinchlist != None:
				self.argcount = uniq(self.pinchlist) 
	def __repr__(self):
		string = '<'
		string += 'lisp.function: '
		string += self.name + ': '
		string += self.base_function.name
		string += '('
		for i in self.complist:
			string += str(i)
			string += ' '
		string += ')'
		string += '>'
		return string
		
	#create the lisp code to define the function in lisp
	def defun(self):
		initialize = lisp.setq( self.complistsymbol, lisp.complist(self.complist), as_string)
		initialize += lisp.setq( self.pinchlistsymbol, lisp.pinchlist(self.pinchlist), as_string)
		if self.pinchlist == None:
			compose = lisp.call( 'compose', [self.name, self.base_function.name, self.complistsymbol], as_string)
			return initialize + compose + '\n'
		else:
			compose = lisp.call( 'compose', [self.unpinchedname, self.base_function.name, self.complistsymbol], as_string)
			pinch = lisp.call( 'pinch', [self.name, self.unpinchedname, self.pinchlistsymbol], as_string)
			return initialize + compose + '\n' + pinch + '\n'
		
class Agent():
	name = None
	client = None #the function the the agent represents
	argcount = 0
	money = 0 #the amount of money the client has made
	suppliers = None #a list of agents that represent the functions with which the clients uses in its composition
	suppliercount = 0
	generosity = .5 #the portion of money that the Agent shares with its suppliers, the money is split evenly
	stream = None #a place to store the stream the agents test results are written to
	
	def __init__(self, client):
		self.name = 'The_agent_representing:' + client.name
		self.client = client
		client.agent = self
		self.argcount = client.argcount
		if(isinstance(client, Derived)):
			self.suppliers = [client.base_function.agent]
			self.suplliercount = 1
			for i in client.complist:
				if(isinstance(i, lisp.Function)):
					self.suppliers.append(i.agent)
					self.suppliercount += 1
					
	def __repr__(self):
		repr = '<'
		repr += self.name
		repr += '>'
		return repr
					
	def __pay(self, receiver, amount):
		assert amount <= self.money
		self.money -= amount
		receiver.money += amount
		receiver.receive_payment(amount)
	
	#the receive_payment method is a way of alerting the agent that it has just received money
	def receive_payment(self, amount):
		if(self.suppliercount != 0):
			stipend = amount * self.generosity / self.suppliercount #the amount the agent will pay each supplier
			for i in self.suppliers:
				self.__pay(i, stipend)
	
	#evaluates a single datum of a function
	def evaluate(self, datum):
		lisp.streamprint( lisp.call(self.client, datum, as_string))
		
	def report(self):
		print self.money
		
	#This function is need for parallelization
		#it allows an agent to check if its stream function is being used by another process
	def available(self):
		if self.stream == None:
			return False
		status = os.system("lsof -t " + self.stream + ">available.tmp")
		#pipe is just to keep the function quiet
		
		#this next bit seems like magic we're exploiting the fact that lsof returns 0 iff it finds the file is in use
		if status == 0:
			return False
		else :
			return True

#A class to represent a gnu screen session
class Screen():
	name = None #the name of the session
	
	def __init__(self, name):
		self.name = name
		command = 'screen -dmS ' + name
		os.system(command)
		
	def send_command(self, command):
		screen_command = 'screen -S ' + self.name + ' -X stuff ' + command + '\r'
		print screen_command
		os.system(screen_command)
	
#The parallelizer is in charge of starting the different clisp processes
#and providing access to the different processes
#it does not do any of the work of figuring out how parallize
class Parallelizer():
	num_screen = None #the number of screens
	screens = [] #tuple contain all of the screen session names
	chunks = []
	fifo = None
	
	def __init__(self, screen_names, population, fifo):
		self.num_screen = len(screen_names)
		for name in screen_names:
			self.screens.append(Screen(name))
		self.fifo = fifo
			
		for screen in self.screens:
			screen.send_command('clisp')
			
		self.update_population(population)
			
	def send_command(self, screen_number, command):
		self.screens[screen_number].send_command(command)
		
	def load_file(self, screen_number, file):
		command = '"(load ' + '\\"' + file + '\\")\r"'
		self.screens[screen_number].send_command(command)
		
	def update_population(self, population):
		self.chunks = []
		chunksize = int ( float( len(population) ) / self.num_screen )
		for i in range(self.num_screen-1):
			self.chunks.append(population[i*chunksize:(i+1)*chunksize])
		
		self.chunks.append(population[(self.num_screen-1)*chunksize:]) #makes sure we get everything
		
	def update_chunks(self, chunks):
		assert 0
class Evaluator():
	generation = 0 #the generation we're on
	population = [] #the population of agents
	datumlength = None
	data = None # a list of data, they all have to be the proper length for the problem, all the data must be the same length
	required = None #this is the file containing the code for all of the agents in the population
	source = 'eval_source' #specifices  'source_generation.lisp', this is the file we write our lisp test source to.
	stream = 'lisp_stream' #specifies 'stream,_generation where the lisp file will print to
	source_folder = None
	parallelizer = None
	
	#the stream and source can be specified as a tuple with either as None, if no tuple is specified defaults are used
	def __init__(self, population, data, required, source_folder, parallelizer, *stream_source):
		self.parallelizer = parallelizer
		self.source_folder = source_folder
		self.population = population
		self.required = required
		self.data = data
		self.datumlength = len(data[1])
		for datum in data:
			assert len(datum) == self.datumlength
		try :
			source, stream = stream_source[0,1]
			if(source != None):
				self.source = source
			if(stream != None):
				self.stream = stream
		except TypeError:
			pass
	
	def evaluate(self):
		for chunknum, chunk in zip(range(len(self.parallelizer.chunks)), self.parallelizer.chunks):
			write_to = self.source_folder + '/' + self.source + str(self.generation) + 'chunk:' + repr(chunknum)+ '.lisp'
			lisp.start_writing(write_to)
			lisp.comment("----Automatically generated code")
			lisp.comment("----Autogened by agents.py - Joe Doliner")
			lisp.comment("----Generated on: " + str(datetime.date.today()))
			lisp.comment("------------- at: " + time.strftime('%H:%M:%S', time.localtime(time.time())))
		
			for agent in chunk:
				if(agent.argcount == self.datumlength):
					stream_to = self.source_folder + '/' + self.stream + '_' + str(self.generation) + '_' + agent.name
					agent.stream = stream_to
					lisp.comment("Opening file...      " + stream_to)
					lisp.open_stream(stream_to)
					lisp.lprint("Evaluating " + agent.client.name + "...") 
					lisp.comment("Code to evaluate agent " + agent.name)
					for datum in self.data:
						agent.evaluate(datum)
					lisp.close_stream()
				
			lisp.comment("----Evaluation ends here")
			lisp.comment("----signal that the evaluation has ended to the host")
			
			#the following writes code to signal the grader when it's done
			lisp.comment("Opening fifo..." + self.parallelizer.fifo)
			lisp.open_stream(self.parallelizer.fifo)
			lisp.streamprint("'" + str(chunknum))
			lisp.close_stream()
			
			lisp.stop_writing()
			if(self.required):
				self.parallelizer.load_file(chunknum, self.required)
			self.parallelizer.load_file(chunknum, write_to)
			 
class Grader():
	generation = 0
	population = [] #the population we're working with
	parallelizer = None
	answer_key = [] #the answers to the test the evaluator gives
	payment_function = None #this function is responsible for awarding $ for correct answers, the systems accuracy works best when this awards on the order of 10^0 (0-1 values are best)
	max_payment = 0
	total_payed = 0
	best_score = 0 #the best score an agent has achieved
	mvp = None #the program that acheived the best score
	final_answers = []
	
	def __init__(self, population, answer_key, payment_function, max_payment_per_problem):
		self.population = population
		self.answer_key = answer_key
		self.payment_function = payment_function
		self.max_payment = max_payment_per_problem * len(answer_key)
	
	def pay(self, receiver, amount):
		receiver.money += amount
		receiver.receive_payment(amount)
		
	#range should be [start,end]
	def grade_chunk(self, chunk):
		for agent in chunk:
			payment = 0
			if(agent.stream != None):
				results = None
				print "OPENING: ", agent.stream
				results = open(agent.stream)
				results.readline() #lisp adds in a blank line at the top
				for correct_ans in self.answer_key:
					answer = results.readline()
					payment += self.payment_function( float(answer), correct_ans)
				results.close()
				self.pay(agent, payment)
				self.total_payed += payment
				if payment >= self.best_score:
					self.best_score = payment
					self.mvp = agent
				if payment == self.max_payment:
					self.final_answers.append(agent)
					
	def grade(self):
		fifo = open(self.parallelizer.fifo,'r')
		
		completed = []
		for chunk in self.parallelizer.chunks:
			completed.append(False)
			
		while not all(completed):
			message = fifo.readline()
			try:
				chunk = int(message)
				self.grade_chunk(parallelizer.chunks[chunk])
				completed[chunk] = True
			except:
				pass #in case we get some input that isn't a number we should ignore it
			
#the breeder is the heart of the entire program it controls how a new
#population is formed from an old one all of the interesting aspects of a genetic
#programming model come from this class as such there are endless design decisions made within
#the breeder class
class Breeder():
	total_money = 0 #the total money that the population has
	generation = 0
	population = []
	population_size = 1000 #the size we will repopulate to
	prob_of_none = .4 #the probability that an element of a new agents complist will be
	__argslist = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
	
	def __init__(self, population, population_size):
		self.population = population
		self.population_size = population_size
		for agent in self.population:
			self.total_money += agent.money
			
	def refresh(self):
		self.total_money = 0
		for agent in self.population:
			self.total_money += agent.money
			
	
	#returns true or false evenly, unless a probability is specified
	def flip_coin(self, prob_of_true):
		if(random.random() < prob_of_true):
			return True
		else:
			return False
	
	#to generate pinchlists it's important to be able to great a list of variable names
	def argrange(self, n):
		return self.__argslist[:n]
		
	#agents are selected to be used in new functions based on their money (of course)
	#however we have a tricky balance to maintain between exploitation of what, given our
	#data appear to be better functions and exploration of other functions
	def naturally_select(self,):
		selection = random.random()*self.total_money
		for agent in self.population:
			selection -= agent.money
			if(selection < 0):
				return agent
	
	def new_function(self, name):
		base_function = self.naturally_select().client
		complist = []
		argcount = 0
		pinchlist = []
		for meaningless in range(base_function.argcount):
			if (self.flip_coin(self.prob_of_none)):
				complist.append(None)
				argcount += 1
			else:
				composer = self.naturally_select()
				complist.append(composer.client)
				argcount += composer.argcount
		
		potentialarguments = self.argrange(argcount)
		for i in range(argcount):
			pinchlist.append(random.choice(potentialarguments))
			
		return Derived(name, base_function, complist, pinchlist)
		
	def breed(self):
		self.refresh()
		new_population = []
		#fills out the population with brand new agents
		for i in range(self.population_size):
			name = 'gen_' + str(self.generation) + '_fun_' + str(i)
			new_population.append(Agent(self.new_function(name)))
			
		return new_population
	
#once a new population has been created this guy's job is to create the source to implement it
class Coder():
	generation = 0
	population = []
	required = None #the file that implements the previous generation for the composition functions to work this needs to be source note bytecode
	source_string = 'gpcode' #this string has "_self.generation.lisp" concatenated to create the actual source name
	source_folder = None
	
	def __init__(self, population, required, source_folder):
		self.generation = 0
		self.population = population
		self.required = required
		self.source_folder = source_folder
		
	def code(self):
		sourcename = self.source_folder + '/' + self.source_string + '_' + str(self.generation) + '.lisp'
		bytecodename = self.source_folder + '/' + self.source_string + '_' + str(self.generation) + '.fas'
		lisp.start_writing(sourcename)
		lisp.comment("Code to implement generation " + str(self.generation))
		if (self.required != None):
			lisp.load(self.required)
		for agent in self.population:
			lisp.defun(agent.client)
		lisp.stop_writing()
		#lisp.compile(sourcename)
		self.required = bytecodename
		return [sourcename, bytecodename] #returns the bytecode and the source as both are needed

