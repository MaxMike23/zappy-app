import subprocess
import platform
import re
import socket
import argparse
import sys
import os
import netifaces

# Dynamically add 'basic-it' directory to sys.path
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(script_dir, "../basic_it"))
sys.path.insert(0, parent_dir)

from ping_ip import check_internet_connectivity

def get_interface_name(interface):
    """
    Retrieves a user-friendly name for the network interface.
    """
    if platform.system().lower() == "windows":
        try:
            import win32com.client
            objWMI = win32com.client.GetObject("winmgmts:\\.\root\cimv2")
            for objNic in objWMI.ExecQuery("Select * from Win32_NetworkAdapter"):
                if objNic.NetConnectionID and objNic.GUID == interface:
                    return objNic.NetConnectionID
        except ImportError:
            return interface  # Fallback to original name if win32com is not available
    else:  # For Linux/MacOS
        try:
            result = subprocess.run(["nmcli", "-t", "device", "show", interface], capture_output=True, text=True)
            match = re.search(r'GENERAL.CONNECTION:(.+)', result.stdout)
            return match.group(1).strip() if match else interface
        except Exception:
            return interface
    return interface

def get_adapter_info():
    """
    Retrieves network adapter information including IP address, subnet mask, gateway, and connection type using netifaces.
    """
    adapters = []
    for interface in netifaces.interfaces():
        addrs = netifaces.ifaddresses(interface)
        ipv4_info = addrs.get(netifaces.AF_INET, [{}])[0]
        gateway_info = netifaces.gateways().get('default', {}).get(netifaces.AF_INET, [None, None])[0]

        ip_address = ipv4_info.get('addr', 'N/A')
        subnet_mask = ipv4_info.get('netmask', 'N/A')
        gateway = gateway_info if gateway_info else 'N/A'
        connection_type = "Wireless" if "wlan" in interface.lower() or "wi-fi" in interface.lower() else "Wired"

        # Get user-friendly name
        friendly_name = get_interface_name(interface)

        adapter = {
            "Interface": friendly_name,
            "IP Address": ip_address,
            "Subnet Mask": subnet_mask,
            "Gateway": gateway,
            "Connection Type": connection_type,
            "DHCP Enabled": is_dhcp_enabled(interface),
            "APIPA": is_apipa(ip_address)
        }
        adapters.append(adapter)

    return adapters

def is_dhcp_enabled(interface):
    """
    Determines if the network adapter is using DHCP.
    """
    try:
        if platform.system().lower() == "windows":
            result = subprocess.run(["netsh", "interface", "ip", "show", "config", interface], capture_output=True, text=True)
            return "DHCP Enabled: Yes" in result.stdout
        else:
            result = subprocess.run(["nmcli", "device", "show", interface], capture_output=True, text=True)
            return "IP4.DHCP4" in result.stdout
    except Exception:
        return False

def is_apipa(ip_address):
    """
    Checks if the IP address is an APIPA (Automatic Private IP Addressing) address.
    """
    return ip_address.startswith("169.254.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Retrieve network adapter status.")
    parser.add_argument("--internet", action="store_true", help="Check if the device is connected to the internet.")
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
