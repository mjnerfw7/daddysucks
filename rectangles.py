def get_dimension(name: str) -> float:
	while True:
		try:
			value = float(input(f"Enter the rectangle's {name}: "))
			if value < 0:
				print("The measurement cannot be negative.")
				continue
			return value
		except ValueError:
			print("Please enter a number.")


length = get_dimension("length")
width = get_dimension("width")
area = length * width

print(f"The area of the rectangle is {area:.2f} square units.")
