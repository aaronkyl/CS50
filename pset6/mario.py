import cs50

while True:
    print("Height: ", end = "")
    height = cs50.get_int()
    if height > 0 and height < 23:
        break
    
for row in range(height):
    print(" " * (height - row - 1), end = "")
    print("#" * (row + 1), end = "")
    print("  ", end = "")
    print("#" * (row + 1))
