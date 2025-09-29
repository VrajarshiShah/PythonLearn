marks={
    "Chirag":100,
    "Manoj":86,
    "Vraj":78
}

print(marks["Vraj"]) # prints values of key
print(marks.items())

print(marks.keys())
print(marks.values())

marks.update({"Vraj":95})

print(marks.get("Manoj3")) # Prints None
print(marks["Chirag3"]) # Returns an error