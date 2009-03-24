import os
__all__ = ["Lisp","Function","double","times"]

class Function():
	name = None
	args = []
	argcount = 0
	body = None #right now this should just be a string of lisp code
	agent = None #the agent which represents the function
	def __init__(self, name, args, body):
		self.name = name
		self.args = args
		self.argcount = len(args)
		self.body = body
	def defun(self):
		ret = '(defun '
		ret += self.name
		ret += ' '
		ret += '('
		for i in self.args:
			ret += i
			ret += ' '
		ret += ')\n'
		ret += '	'
		ret += self.body
		ret += ')\n'
		return ret
	def __repr__(self):
		string = '<'
		string += 'lisp.function: '
		string += self.name + ': '
		for i in self.args:
			string += i
			string += ' '
		string += '-->'
		string += self.body
		string += '>'
		return string
		
	def __str__(self):
		return self.name

"""Class to interact with lisp and to create lisp source files"""
class Lisp():
	#command used to invoke lisp
	invoke = "clisp"
	command = None
	source = None
	stream = 'pylisp' #this is the symbol that will be used in streams
	scratch = 'pylispscratch.lisp'
	flag_compile = True #compile on load, slower load but faster exec"
	#by defualt the lisp command is clisp, but you can change it
	#depending on the system
	#returns the present state of the lisp API
	def state(self):
		print "Invoke command:", self.invoke
		print "Present command string:", self.command
		print "Writing source to file:", self.source
		print "Compile Flag:", self.flag_compile
	
	def clear(self):
		self.command = None
		self.source = None
		
	def delete_scratch(self):
		os.system('rm ' + self.scratch)
		
	def go(self):
		os.system(self.command)
		
	def run(self, file, *out):
		self.command = self.invoke
		self.space()
		self.command += file
		self.space()
		if (None):
			self.command += '>'
			self.command += out
		self.go()
		self.clear()
		
	def compile(self, input, *output):
		self.command = self.invoke
		self.command += ' -i '
		self.command += input
		self.command += ' -c '
		self.command += input
		if(output):
			self.command += ' -o '
			self.command += output
		self.go()
		

	def space(self):
		self.command += " "
		
	def start_writing(self,filename):
		self.source = open(filename, "w")
		
	#flushes command when called
	def stop_writing(self):
		if (self.command != None):
			self.write()
		self.source.close()
		self.source = None
		
	def write(self): #writes the present command to the source file
		if(self.source == None): #some sanity checking
			raise IOError, 'No source file specified'
		else:
			self.source.write(self.command)
			self.command = None
			
	def write_string(self): #returns what would have been written as a string
		temp = self.command
		self.command = None
		return temp
		
	def list(self,list, *as_string):
		self.command = '(list '
		for i in list:
			self.command += i + ' '
		self.command += ')'
		if(as_string):
			return self.write_string()
		else:
			self.write()
		
	#calls to defun have the side effect of clearing the command at
	#the start and end, as well as writing to the source file
	def defun(self, function, *as_string):
		self.command = function.defun()
		if(as_string):
			return self.write_string()
		else:
			self.write()
		
	def setq(self, symbol, value, *as_string):
		self.command = '('
		self.command += 'setq'
		self.space()
		self.command += symbol
		self.space()
		self.command += str(value)
		self.command += ')\n'
		if(as_string):
			return self.write_string()
		else:
			self.write()
			
	def lprint(self, message, *as_string):
		self.command = '('
		self.command += 'print '
		self.command += '"' + message + '"'
		self.command += ')\n'
		if(as_string):
			return self.write_string()
		else:
			self.write()
		
	def call(self, func, args, *as_string):
		self.command = '('
		if(isinstance(func, Function)):
			self.command += func.name
		else:
			self.command += func
		self.space()
		for i in args:
			self.command += str(i)
			self.space()
		self.command += ') '
		if(as_string):
			return self.write_string()
		else:
			self.write()
			
	def complist(self, list):
		self.command = '(list '
		for f_or_none in list:
			if f_or_none == None:
				self.command += 'None '
			else:
				self.command += ('(safe-function ' + f_or_none.name + ')')
				
		self.command += ')'
		return self.command
		
	def pinchlist(self, list):
		self.command = '(list '
		for argument in list:
			self.command += "'" + argument + ' '
		self.command += ')'
		return self.command
		
	def load(self, file, *as_string):
		self.command = '('
		self.command += 'load '
		self.command += ('"' + file + '"')
		self.command += ')\n'
		if(as_string):
			return self.write_string()
		else:
			self.write()
		
	def open_stream(self, file, *as_string):
		self.command = '(setq '
		self.command += 'pylisp '
		self.command += '(open '
		self.command += ('"' + file + '" ')
		self.command += ':if-does-not-exist :create '
		self.command += ':direction :output'
		self.command += '))\n'
		if(as_string):
			return self.write_string()
		else:
			self.write()
		
	def streamprint(self, expression, *as_string):
		self.command = '(print '
		self.command += (expression + ' ')
		self.command += ('pylisp' + ')\n')
		if(as_string):
			return self.write_string()
		else:
			self.write()
			
	def close_stream(self, *as_string):
		self.command = '(close '
		self.command += ('pylisp' + ')\n')
		if(as_string):
			return self.write_string()
		else:
			self.write
		self.stream = None
			
	def comment(self, comment):
		self.command = ';;'
		self.command += comment
		self.command += '\n'
		self.write()
		
_inst = Lisp()
stream = _inst.stream
state = _inst.state
clear = _inst.clear
go = _inst.go
run = _inst.run
compile = _inst.compile
start_writing = _inst.start_writing
stop_writing = _inst.stop_writing
write = _inst.write
write_string = _inst.write_string
list = _inst.list
defun = _inst.defun
setq = _inst.setq
lprint = _inst.lprint
call = _inst.call
complist = _inst.complist
pinchlist = _inst.pinchlist
load = _inst.load
open_stream = _inst.open_stream
streamprint = _inst.streamprint
close_stream = _inst.close_stream
comment = _inst.comment

#here are some nice test functions for debugging purposes
#these should all be compileable lisp functions
double = Function('double', ['x'], '(* x 2)')
times = Function('timess', ['x','y'], '(* x y)')
