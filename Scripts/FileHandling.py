import csv

def writing():
    with open("../Data/Testing.csv", "a") as file:
        file.write("Hello World")
        file.write("Writing test")


def reading():
    try:
        with open("../Data/Testing.csv", "r") as file:
            content = file.read()
            print(content)
    except FileNotFoundError as e:
        print(f"Error: {e}")


def columnNames():
    columns = [f"landmark_{i}_{axis}" for i in range(21) for axis in ['x', 'y', 'z']]
    columns.append('Testing')
    with open("../Data/Testing2.csv", "a") as file:
        writer = csv.writer(file)
        writer.writerow(columns)


def main():
    while True:
        print("[1] - Write")
        print("[2] - Read")
        print("[3] - Column Names")
        print("[0] - Exit")
        option = int(input("Please choose one option: "))

        if option == 1:
            writing()
        elif option == 2:
            reading()
        elif option == 3:
            columnNames()
        elif option == 0:
            break
        else:
            print("Invalid input, try again\n\n")

if __name__ == "__main__":
    main()