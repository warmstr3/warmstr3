
# Import Libaries
import requests
from lxml import etree
import time
import urllib3
import random

# Suppress the InsecureRequestWarning for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- User Configuration ---
SERVER_IP = "10.12.59.2" # Your server's ens2 IP address
HTTPS_PORT = 8443        # Port for HTTPS (as configured in the server script)
HTTP_PORT = 8080         # Example port for HTTP (server would need to support this)
POLLING_INTERVAL_SECONDS = 5 # How often to send requests
# --- End User Configuration ---

def get_protocol_choice():
    """Prompts the user to choose between HTTP and HTTPS."""
    while True:
        choice = input("Choose protocol (http or https): ").lower().strip()
        if choice in ["http", "https"]:
            return choice
        else:
            print("Invalid choice. Please enter 'http' or 'https'.")

def send_der_traffic(server_url, use_https):
    # Generate random values for DER status
    voltage = round(random.uniform(220.0, 240.0), 1) # e.g., 220.0 to 240.0 V
    current = round(random.uniform(0.5, 15.0), 1)   # e.g., 0.5 to 15.0 A
    realPower = round(random.uniform(0.1, 5.0), 1)  # e.g., 0.1 to 5.0 kW

    # Create sample DERStatus XML
    root = etree.Element("DERStatus")
    etree.SubElement(root, "voltage").text = str(voltage)
    etree.SubElement(root, "current").text = str(current)
    etree.SubElement(root, "realPower").text = str(realPower)
    xml_bytes = etree.tostring(root, pretty_print=True)

    try:
        # Send status
        print(f"[{time.strftime('%H:%M:%S')}] Sending DER status (V:{voltage}, A:{current}, P:{realPower}) to {server_url}/der/DER001/status")
        resp = requests.post(
            f"{server_url}/der/DER001/status",
            data=xml_bytes,
            verify=False if use_https else False # Skip CA verification for self-signed certs (HTTPS)
                                                 # For HTTP, verify=False has no effect but is harmless
        )
        resp.raise_for_status()
        print(f"[{time.strftime('%H:%M:%S')}] Status update response: {resp.text}")

        # Get control command
        print(f"[{time.strftime('%H:%M:%S')}] Requesting control command from {server_url}/der/DER001/control")
        resp = requests.get(
            f"{server_url}/der/DER001/control",
            verify=False if use_https else False
        )
        resp.raise_for_status()
        print(f"[{time.strftime('%H:%M:%S')}] Control command received: {resp.text}")

    except requests.exceptions.ConnectionError as e:
        print(f"[{time.strftime('%H:%M:%S')}] Connection Error: {e}. Is the server running at {server_url} and accessible? "
              f"Remember the mock server is configured for HTTPS on port {HTTPS_PORT}.")
    except requests.exceptions.Timeout:
        print(f"[{time.strftime('%H:%M:%S')}] Timeout Error: The server did not respond in time.")
    except requests.exceptions.RequestException as e:
        print(f"[{time.strftime('%H:%M:%S')}] An unexpected error occurred: {e}")
    print("-" * 50)

if __name__ == "__main__":
    protocol_choice = get_protocol_choice()
    use_https = (protocol_choice == "https")

    if use_https:
        final_server_url = f"https://{SERVER_IP}:{HTTPS_PORT}"
        print(f"\nNOTE: The mock server provided in the guide runs HTTPS on port {HTTPS_PORT}. "
              f"Choosing HTTPS is recommended for this setup.")
    else:
        final_server_url = f"http://{SERVER_IP}:{HTTP_PORT}"
        print(f"\nWARNING: The mock server provided in the guide runs *only* HTTPS on port {HTTPS_PORT}. "
              f"If you selected HTTP, this client will attempt to connect to {final_server_url}, "
              f"which will likely fail unless your server is also configured to serve HTTP on port {HTTP_PORT}.")


    print(f"\nStarting continuous DER client with randomized values. Sending requests every {POLLING_INTERVAL_SECONDS} seconds to {final_server_url}")
    print("Press Ctrl+C to stop.")
    try:
        while True:
            send_der_traffic(final_server_url, use_https)
            time.sleep(POLLING_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        print("\nDER client stopped by user.")
