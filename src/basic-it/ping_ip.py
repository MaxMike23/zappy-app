import subprocess
import platform
import argparse
import time
import sys
import re
import itertools



def validate_ip(ip_address):
    """
    Validates if the given IP address is in the correct IPv4 format.

    :param ip_address: The IP address to validate
    :return: True if valid, False otherwise
    """
    pattern = re.compile(r'^(25[0-5]|2[0-4][0-9]|1?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|1?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|1?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|1?[0-9][0-9]?)$')
    return bool(pattern.match(ip_address))


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
    if not validate_ip(ip_address):
        print(f"Error: Invalid IP address format - {ip_address}")
        return False

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


def check_internet_connectivity():
    """
    Checks if the computer is connected to the internet by pinging known external IPs.

    :return: True if at least one external IP is reachable, False otherwise
    """
    test_ips = ["8.8.8.8", "8.8.4.4"]

    print("Checking internet connectivity...")
    for ip in test_ips:
        if ping_device(ip):
            print(f"[UP] Internet is reachable via {ip}.")
            return True
    print("[DOWN] No internet connection detected.")
    return False


def get_external_ip():
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


def check_ping(ip_address):
    """
    Checks the status of the ping result, return a string if reachable or unreachable

    :param ip_address: The IP address of the device being pinged
    :return: Test confirmation as a string
    """
    if ip_address:
        if ping_device(ip_address):
            print(f"[UP] {ip_address} is reachable.")
        else:
            print(f"[DOWN] {ip_address} is unreachable.")
        return
    else:
        print(f"Error: Invalid IP address format - {ip_address}")



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ping a device, check internet connectivity, or get external IP.")
    parser.add_argument("--ip", help="Specify an IP address to ping.")
    parser.add_argument("--internet", action="store_true", help="Check internet connectivity.")
    parser.add_argument("--external", action="store_true", help="Get the internal (public) IP address.")
    args = parser.parse_args()

    if args.ip:
        check_ping(args.ip)
    elif args.internet:
        check_internet_connectivity()
    elif args.external:
        external_ip = get_external_ip()
        if external_ip:
            print(f"Internal IP: {external_ip}")
        else:
            print("Could not retrieve internal IP.")
    else:
        parser.print_help()