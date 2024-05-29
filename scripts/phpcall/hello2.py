#import sys so the var passed from php can be used
import sys

# Access command-line arguments
# sys.argv[0] is the script name, so we start from index 1
if len(sys.argv) > 1:
    php_variable = sys.argv[1]
else:
    php_variable = "Default value if not passed"

php_variable=php_variable+'altered'

# example.py
var1 = "Hello"
var2 = "World"

# Print variables along with the PHP variable
print(f"VAR1: {var1}\nVAR2: {var2}\nPHP_Variable: {php_variable}")
