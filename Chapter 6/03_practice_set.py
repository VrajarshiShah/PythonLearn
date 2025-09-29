m1=int(input("Maths:"))
m2=int(input("English:"))
m3=int(input("Science:"))

avg=(m1+m2+m3)/3

if(avg>90):
    print("You have got EX grade with ",avg)

elif(avg>80 and avg<90):
    print("You have got A grade with ",avg)

elif(avg>70 and avg<80):
    print("You have got B grade with ",avg)

elif(avg>60 and avg<70):
    print("You have got C grade with ",avg)