import sys


def add_one(num):
    """
    Adds 1 to the given number.
    
    Args:
        num (int): The number to add 1 to.
    
    Returns:
        int: The number plus 1.
    """
    return num + 1


if __name__ == "__main__":
    # Get the number from the command line argument
    if len(sys.argv) < 2:
        print("Please provide a number as an argument.")
        sys.exit(1)

    try:
        num = int(sys.argv[1])
        result = add_one(num)
        print(result)
    except ValueError:
        print("Invalid number provided.")
        sys.exit(1)
