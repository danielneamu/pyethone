import subprocess
import time
import re

def ping_host(host):
    """
    Function to ping a host and return the response time.
    Returns None if ping fails.
    """
    try:
        # Using 'ping' command with count 1 and capturing output
        output = subprocess.check_output(['ping', '-n', '1', host], stderr=subprocess.STDOUT, universal_newlines=True)

        # Parsing the output to extract response time
        time_ms = parse_ping_time(output)
        return time_ms
    except subprocess.CalledProcessError as e:
        print(f"Ping failed: {e}")
        return None
    except Exception as e:
        print(f"Error during ping: {e}")
        return None

def parse_ping_time(output):
    """
    Function to parse the ping output and extract the response time.
    Returns the response time in milliseconds.
    """
    # Using regex to find the time in milliseconds from the output
    pattern = r"time=(\d+(?:\.\d+)?)ms"
    match = re.search(pattern, output, re.IGNORECASE)
    if match:
        return float(match.group(1))
    else:
        return None

def main(host, duration):
    """
    Main function to ping the host every 5 seconds for the given duration (in seconds).
    Prints response times after each ping and returns the list of response times at the end.
    """
    response_times = []

    # Calculate end time
    end_time = time.time() + duration

    while time.time() < end_time:
        # Ping the host
        response_time = ping_host(host)

        if response_time is not None:
            response_times.append(response_time)
            print(f"Response time: {response_time} ms")
        else:
            print(f"Ping failed to {host}")

        # Wait for 5 seconds
        time.sleep(5)

    return response_times

if __name__ == "__main__":
    host_to_ping = "piedone.go.ro"  # Replace with your desired host or IP address
    duration_seconds = 60  # Duration for which to ping (in seconds)

    print(f"Pinging {host_to_ping} every 5 seconds for {duration_seconds} seconds...")
    response_times = main(host_to_ping, duration_seconds)

    print("\nResponse times recorded:")
    print(response_times)
