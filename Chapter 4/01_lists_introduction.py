friends=["Apple","Vibhisan",12,True,345.06]
print(friends)
friends[0]="Grapes" #Unlike strings, List are mutable
print(friends[0])
print(friends[0:5:2])

friends.append("Morgn chase")
print(friends)

friends.pop(1)
print(friends)

l1=[87,45,55,98,54]
l1.sort()
print(l1)
print(l1.reverse())
print(l1)
l1.insert(3,38) #insert at specified index
print(l1)
l1.remove(38) #remove specified item at index specified
print(l1)