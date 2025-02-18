import subprocess
import platform
import time
import sys
import itertools

def show_spinner_ip(ip_address, duration=6):
    """
    Displays a spinning line indicator while pinging an IP address.
    :param ip_address: The IP address of the device
    :param duration: The duration of the spinning indicator in seconds, default is 6
    """
    spinner = itertools.cycle(['-', '\\', '|', '/'])
    end_time = time.time() + duration
    while time.time() < end_time:
        sys.stdout.write(f"\rPinging {ip_address}... {next(spinner)}")
        sys.stdout.flush()
        time.sleep(0.2)
    sys.stdout.write("\r\033[K")  # Clear the line
    sys.stdout.flush()

def ping_device(ip_address, duration=6, timeout=1):
    """
    Pings an IP address of a device, returns True if it's up, False if it's down.

    :param ip_address: The IP address of the device
    :param duration: How many pings are done to get a result
    :param timeout: How long each ping should be in seconds, regardless of connectivity
    :return: Boolean indicating if the device is reachable
    """
    try:
        # Determine the correct ping command based on OS
        if platform.system().lower() == "windows":
            command = ["ping", "-n", str(duration), "-w", str(timeout * 1000), ip_address]
        else:
            command = ["ping", "-c", str(duration),  "-W", str(timeout), ip_address]

        show_spinner_ip(ip_address, duration)

        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.returncode == 0
    except Exception as e:
        return False

def get_internal_ip():
    """
    Gets the external, public IP address of your private network

    :return: Public IP address as a string
    """
    try:
        result = subprocess.run(["curl", "-s", "https://api64.ipify.org"], stdout=subprocess.PIPE, text=True)
        return result.stdout.strip()
    except Exception as e:
        print(f"Error retrieving external IP: {e}")
        return None

if __name__ == "__main__":
    get_internal_ip()