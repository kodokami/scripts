import random
import sys

global uppercase
global lowercase
global numbers

def genpin(count) :
	s = ''
	for i in range(count) :
		s += numbers[random.randint(0,len(numbers)-1)]
	return s

def genlowercasepasswd(count) :
	s = ''
	for i in range(count) :
		s += lowercase[random.randint(0,len(lowercase)-1)]
	return s

def genuppercasepasswd(count) :
	s = ''
	for i in range(count) :
		s += uppercase[random.randint(0,len(uppercase)-1)]
	return s

def gensimplepasswd(count) :
	s = ''
	signs = lowercase + numbers
	for i in range(count) :
		s += signs[random.randint(0,len(signs)-1)]
	return s

def gencomplexpasswd(count) :
	s = ''
	signs = uppercase + lowercase + numbers
	for i in range(count) :
		s += signs[random.randint(0,len(signs)-1)]
	return s

def help() :
	s = '\ngenpasswd - python password generator v0.1\n\n' \
		'usage: genpasswd passwordType passwordLength\n' \
		'allowed types:\n' \
		'\tpin\t\t - password generated with numbers only\n' \
		'\tsimple\t\t - password generated with numbers and lowercase characters\n' \
		'\tcomplex\t\t - password generated with numbers, lowercase and uppercase characters\n' \
		'\tlowercase\t - password generated with lowercase characters only\n' \
		'\tuppercase\t - password generated with uppercase characters only\n'
	print(s)

####################
# MAIN FUNCTION
if __name__ == '__main__' :
	uppercase = ['A','B','C','D','E','F','G','H','J','K','L','M','N','P','Q','R','S','T','U','V','W','X','Y','Z']
	lowercase = ['a','b','c','d','e','f','g','h','i','j','k','m','n','p','q','r','s','t','u','v','w','x','y','z']
	numbers = ['0','1','2','3','4','5','6','7','8','9']

	switch = {'help': help, 'pin': genpin, 'simple': gensimplepasswd, 'complex': gencomplexpasswd, 'lowercase': genlowercasepasswd, 'uppercase': genuppercasepasswd}
	
	if len(sys.argv) == 1 : help()
	elif len(sys.argv) != 3 : raise SystemExit('err: genpasswd needs exactly 2 arguments')
	else :
		try :
			i = int(sys.argv[2])
			if i < 0 : raise SystemExit('err: password length cannot be a negative number')
		except ValueError :
			raise SystemExit('err: second argument must be a number')

		if sys.argv[1] in switch.keys() :
			print switch[sys.argv[1]](int(sys.argv[2]))
		else : raise SystemExit('err: unknown password type')
