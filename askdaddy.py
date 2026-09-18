import math


def main() -> None:
    while True:
        try:
            radius = float(input("Enter the radius of the circle: "))
            if radius < 0:
                print("The radius cannot be negative.")
                continue
            break
        except ValueError:
            print("Please enter a number.")

    circumference = 2 * math.pi * radius
    area = math.pi * radius ** 2

    print(f"Circumference: {circumference:.2f}")
    print(f"Area: {area:.2f}")


if __name__ == "__main__":
    main()
