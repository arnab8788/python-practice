#New Line Character and Seperator in Python Print
print("###New Line Character and Seperator###")
#New Line Character with \n
print('Hello\nWorld')

#New Line with the help of end
print("Hello World ", end="")
print('In Same Line')

#Seperator to change the deault white space to given value in case of multiple arguments
print('1','2','3','4','5','6','7',sep=", ")

#Using both end and seperator
print('1','2','3','4','5','6','7',sep=", ",end=" $$$$$ ")
print('1000')


#Basic Formatting with the help of the Print Statement and Format function
print('\n###Basic Formatting with Format Function###')
      
#Using {} to print the values in customized order
print('My name is {}'.format('Arnab'))
print('My First Name is {} and Last Name is {}'.format('Arnab','Desarkar'))

#Using {} and index value to print the values in customized order
print('My First Name is {1} and Last Name is {0}'.format('Desarkar','Arnab'))

#Using {} and keys to print the values in customized order
print('My First Name is {f} and Last Name is {l}'.format(l='Desarkar',f='Arnab'))
print('Two times my first name is {f} {f}'.format(l='Desarkar',f='Arnab'))


#Using variable to repeat the above functionality
print("\n###Using variable to repeat the above functionality###")

fname="Arnab"
lname="Desarkar"
print('My name is {}'.format(fname))
print('My First Name is {} and Last Name is {}'.format(fname,lname))
print('My First Name is {1} and Last Name is {0}'.format(lname,fname))
print('My First Name is {f} and Last Name is {l}'.format(l=lname,f=fname))
print('Two times my first name is {f} {f}'.format(l=lname,f=fname))




#Passing the curly braces thorugh variables
print("\n###Passing the curly braces thorugh variables###")
myvariable="My First Name is {} and Last Name is {}"
print(myvariable.format(fname,lname))



##############################################################################
#Below is the Ouput provided for each of the print statements#
##############################################################################
####New Line Character and Seperator###
#Hello
#World
#Hello World In Same Line
#1, 2, 3, 4, 5, 6, 7
#1, 2, 3, 4, 5, 6, 7 $$$$$ 1000
#
####Basic Formatting with Format Function###
#My name is Arnab
#My First Name is Arnab and Last Name is Desarkar
#My First Name is Arnab and Last Name is Desarkar
#My First Name is Arnab and Last Name is Desarkar
#Two times my first name is Arnab Arnab
#
####Using variable to repeat the above functionality###
#My name is Arnab
#My First Name is Arnab and Last Name is Desarkar
#My First Name is Arnab and Last Name is Desarkar
#My First Name is Arnab and Last Name is Desarkar
#Two times my first name is Arnab Arnab
#
####Passing the curly braces thorugh variables###
#My First Name is Arnab and Last Name is Desarkar
##############################################################################