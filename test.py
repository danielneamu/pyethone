# test_debug.py

def add_numbers(a, b):
    result = a + b
    print(f"Adding {a} + {b} = {result}")
    return result

def main():
    x = 5
    y = 10
    sum_result = add_numbers(x, y)

    for i in range(3):
        print(f"Loop iteration {i}")
        if i == 1:
            print("Breakpoint can be tested here")
    
    if sum_result > 10:
        print("Sum is greater than 10")
    else:
        print("Sum is 10 or less")

if __name__ == "__main__":
    main()
