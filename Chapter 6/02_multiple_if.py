age=32
married=False

if(age>18):
    print("You are elgible to watch movie.")
    if(married==False):
        print("You are not elgible to watch adult + romantic movie")
    elif(married==True):
        print("You are elgible to watch adult + romantic movie")

if(age%2==0):
    print("Number can be divided by 2")