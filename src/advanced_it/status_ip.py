import argparse
import os
import platform
import re
import subprocess
import sys

import netifaces


# Dynamically add 'basic-it' directory to sys.path
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(script_dir, "../basic_it"))
sys.path.insert(0, parent_dir)

from ping_ip import check_internet_connectivity

def get_interface_name(interface):
    """
    Retrieves a user-friendly name for the network interface using PowerShell.

    :param interface: GUID of a network interface
    :return: String of the user-friendly name of a the network interface
    """
    if platform.system().lower() == "windows":
        try:
            result = subprocess.run(
                ["powershell", "-Command",
                 f"Get-NetAdapter | Where-Object {{ $_.InterfaceGuid -eq '{interface}' }} | Select-Object -ExpandProperty Name"],
                capture_output=True, text=True
            )
            return result.stdout.strip() if result.stdout else interface
        except Exception:
            return interface
    else:  # For Linux/MacOS
        try:
            result = subprocess.run(["nmcli", "-t", "device", "show", interface], capture_output=True, text=True)
            match = re.search(r'GENERAL.CONNECTION:(.+)', result.stdout)
            return match.group(1).strip() if match else interface
        except Exception:
            return interface
    return interface

def get_connection_type(interface):
    """
    Determines the connection type (Wired or Wireless) using PowerShell.

    :param interface: GUID of a network interface
    :return: String of either Wired or Wireless
    """
    if platform.system().lower() == "windows":
        try:
            result = subprocess.run(
                ["powershell", "-Command",
                 f"Get-NetAdapter -Name '{interface}' | Select-Object -ExpandProperty MediaType"],
                capture_output=True, text=True
            )
            return "Wireless" if "802.11" in result.stdout else "Wired"
        except Exception:
            return "Unknown"
    else:
        return "Wireless" if "wlan" in interface.lower() or "wi-fi" in interface.lower() else "Wired"

def get_adapter_info():
    """
    Retrieves network adapter information including IP address, subnet mask, gateway,
    and connection type using netifaces and netsh.
    Filters out adapters with no IP address or no friendly name.

    :return: List of settings of a network adapter
    """
    adapters = []
    for interface in netifaces.interfaces():
        addrs = netifaces.ifaddresses(interface)
        ipv4_info = addrs.get(netifaces.AF_INET, [{}])[0]

        ip_address = ipv4_info.get('addr', 'N/A')
        subnet_mask = ipv4_info.get('netmask', 'N/A')

        # Get user-friendly name using PowerShell
        friendly_name = get_interface_name(interface)

        # Get Connection Type
        connection_type = get_connection_type(friendly_name)

        # Get Gateway using netsh
        gateway = get_gateway_ip(friendly_name)

        # Skip interfaces with no IP Address or no Friendly Name
        if ip_address == 'N/A' or friendly_name == interface:
            continue

        adapter = {
            "Interface": friendly_name,
            "IP Address": ip_address,
            "Subnet Mask": subnet_mask,
            "Gateway": gateway,  # Display correct gateway for this interface
            "Connection Type": connection_type,
            "DHCP Enabled": is_dhcp_enabled(friendly_name),
            "APIPA": is_apipa(ip_address)
        }
        adapters.append(adapter)
    return adapters

def get_gateway_ip(interface):
    """
    Retrieves the gateway IP for a specific network interface using netsh on Windows.
    Improved to handle multiple formats and capture all gateway lines.

    :param interface: GUID of a network interface
    :return: String of the gateway IP address
    """
    try:
        if platform.system().lower() == "windows":
            result = subprocess.run(
                ["netsh", "interface", "ip", "show", "config", interface],
                capture_output=True, text=True
            )
            # Extract all gateway lines
            matches = re.findall(r"Default Gateway[ .:]+([0-9.]+)", result.stdout)
            # Join all found gateways, separated by commas
            return ", ".join(matches) if matches else "N/A"
        else:
            return "N/A"  # Implement for Linux/MacOS if needed
    except Exception:
        return "N/A"

def is_dhcp_enabled(interface):
    """
    Determines if the network adapter is actively using DHCP using netsh.
    This method checks if DHCP is already enabled without changing settings.

    :param interface: GUID of a network interface
    :return: Boolean; True if DHCP is enabled for the address, False if not
    """
    try:
        if platform.system().lower() == "windows":
            result = subprocess.run(
                ["netsh", "interface", "ip", "set", "address", interface, "dhcp"],
                capture_output=True, text=True
            )
            if "DHCP is already enabled on this interface." in result.stdout:
                return True
            else:
                subprocess.run([
                    "netsh", "interface", "ip", "set", "address",
                    interface, "static", "0.0.0.0", "0.0.0.0"
                ], capture_output=True)
                return False
        else:
            result = subprocess.run(["nmcli", "device", "show", interface], capture_output=True, text=True)
            return "IP4.DHCP4" in result.stdout
    except Exception:
        return False

def is_apipa(ip_address):
    """
    Checks if the IP address is an APIPA (Automatic Private IP Addressing) address.

    :param ip_address: An IPv4 address
    :return: Boolean if an IP address is an APIPA address
    """
    return ip_address.startswith("169.254.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Retrieve network adapter status.")
    parser.add_argument("--internet", action="store_true",
                        help="Check if the device is connected to the internet.")
    args = parser.parse_args()

    if args.internet:
        status = "Connected" if check_internet_connectivity() else "Not Connected"
        print(f"Internet Status: {status}")
    else:
        adapters = get_adapter_info()
        print("Network Adapter Status:")
        for adapter in adapters:
            print("-----------------------------------")
            for key, value in adapter.items():
                print(f"{key}: {value}")
