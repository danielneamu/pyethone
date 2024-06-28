import sys
import traceback

try:
    import yfinance as yf
except ModuleNotFoundError:
    print("Module 'yfinance' not found. Check installation or environment setup.")
    traceback.print_exc()
    sys.exit(1)
except Exception as e:
    print(f"An error occurred: {e}")
    traceback.print_exc()
    sys.exit(1)


var1 = "Hello"
var2 = "World"

def process_var(var):
    return str(var)

if __name__ == "__main__":
    try:
        var = sys.argv[1]
        result = process_var(var)
        print(result)
    except ValueError:
        print("Invalid variable provided.")
        sys.exit(1)

print(f"VAR1: {var1}\nVAR2: {var2}")



