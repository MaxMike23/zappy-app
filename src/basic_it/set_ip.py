import subprocess
import argparse
import sys

def get_network_adapters():
    """
    Retrieves the list of network adapters available on the system and assigns numbers to them.

    :return: A list of network adapters, or an empty list if none are available
    """
    try:
        result = subprocess.run(
            ["netsh", "interface", "show", "interface"],
            capture_output=True, text=True, check=True
        )
        lines = result.stdout.split("\n")
        adapters = []
        for line in lines[2:]:  # Skip the first two lines (headers)
            parts = line.split()
            if len(parts) > 3:
                adapter_name = " ".join(parts[3:])  # Get everything after the third column
                adapters.append(adapter_name)
        return adapters
    except subprocess.CalledProcessError:
        return []

def set_static_ip(interface, ip_address, subnet_mask, gateway=None):
    """
    Sets a static IP address on a Windows machine.

    :param interface: Name of the network interface
    :param ip_address: Static IP address to assign
    :param subnet_mask: Subnet mask for the network
    :param gateway: Default gateway (optional)
    """
    try:
        command = [
            "netsh", "interface", "ip", "set", "address",
            interface, "static", ip_address, subnet_mask
        ]
        if gateway:
            command.append(gateway)

        subprocess.run(command, check=True)
        print(f"Successfully set static IP: {ip_address} on {interface}")
    except subprocess.CalledProcessError as e:
        print(f"Error setting static IP: {e}")

def set_dhcp(interface):
    """
    Sets the network interface to use DHCP for IP assignment.

    :param interface: Name of the network interface
    """
    try:
        subprocess.run(
            ["netsh", "interface", "ip", "set", "address", interface, "dhcp"],
            check=True
        )
        print(f"Successfully set {interface} to DHCP mode")
    except subprocess.CalledProcessError as e:
        print(f"Error setting DHCP: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Change Windows IP settings to Static or DHCP.",
                                     usage="python script.py [-h] [--interface INTERFACE] [--static IP MASK [GATEWAY] | --dhcp]")
    parser.add_argument("-i", "--interface", nargs="?", help="Network interface name or number (leave empty to list available adapters)")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--static", nargs="+", metavar=("IP", "MASK", "GATEWAY"),
                        help="Set static IP (requires IP, subnet mask, and optional gateway)")
    group.add_argument("--dhcp", action="store_true", help="Set interface to DHCP mode")

    args = parser.parse_args()

    adapters = get_network_adapters()

    if args.interface is None:
        if adapters:
            print("Available network adapters:")
            for idx, adapter in enumerate(adapters, start=1):
                print(f"  [{idx}] {adapter}")
        else:
            print("No network adapters found or error retrieving them.")
        sys.exit(0)

    try:
        interface_index = int(args.interface) - 1
        if 0 <= interface_index < len(adapters):
            selected_interface = adapters[interface_index]
        else:
            print("Invalid adapter number. Please select a valid number.")
            sys.exit(1)
    except ValueError:
        selected_interface = args.interface  # Assume it's a name if not a number

    if args.static:
        if len(args.static) < 2:
            print("\nError: --static requires at least an IP and subnet mask. The gateway is optional.")
            parser.print_help()
            sys.exit(2)
        ip, mask = args.static[:2]
        gateway = args.static[2] if len(args.static) > 2 else None
        set_static_ip(selected_interface, ip, mask, gateway)
    elif args.dhcp:
        set_dhcp(selected_interface)
    else:
        print("\nError: You must specify either --static with valid parameters or --dhcp.")
        parser.print_help()
        sys.exit(2)
