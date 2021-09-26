#try/except statement

astr = "Bob"

try:
    print("Hello")
    istr = int(astr)
    print("There") # never runs it!
except:
    istr = -1

print('Done', istr)



# bigest value
big = max(1, 4, 9)
print(big)


big = max("Hello World")
print(big)


#break and continue
#break
while True:
    line = input('> ')
    if line == 'done':
        break
    print(line)
print('Done')


#continue
while True:
    line = input('Please make your input>> ')
    if line[0] == '#':
        continue # if # goes back to question
    if line == 'done':
        break
    print(line)
print("Done")