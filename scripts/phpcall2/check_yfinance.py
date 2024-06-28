import sys
import yfinance as yf

# Check if the correct number of arguments are passed
if len(sys.argv) != 3:
    print("Usage: check_yfinance.py <var1> <var2>")
    sys.exit(1)

# Get the arguments from command line
var1 = sys.argv[1]
var2 = sys.argv[2]

# Print the received arguments
print(f"Received variables: var1={var1}, var2={var2}")

# Your existing code
print("yfinance imported successfully.")
