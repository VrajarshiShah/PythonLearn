p1="Make a lot of money"
p2="click this"

message=input("Add comment:")

if(p1 in message or p2 in message):
    print("This comment is spam")

else:
    print("Valid message")