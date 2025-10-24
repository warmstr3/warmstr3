
# Import Libaries
from flask import Flask, request, jsonify
from lxml import etree
import threading
import requests
import json
import time
import urllib3

# Suppress InsecureRequestWarning for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

# Simulated DER status database (in memory)
der_status = {}

# Splunk HEC configuration
SPLUNK_HEC_URL = "https://172.18.143.66:8088/services/collector"  # Splunk HEC endpoint
SPLUNK_HEC_TOKEN = "b0e0eaf9-11c4-48e8-9c56-9fe428e0f768"          # Your HEC token
SPLUNK_INDEX = "main"                                               # Splunk index

def send_to_splunk(event_msg):
    """Send event to Splunk via HEC."""
    headers = {
        "Authorization": f"Splunk {SPLUNK_HEC_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "time": int(time.time()),
        "host": "MockDERServer",
        "source": "mock_IEEE2030.5",
        "sourcetype": "der_status",
        "index": SPLUNK_INDEX,
        "event": event_msg
    }
    try:
        response = requests.post(SPLUNK_HEC_URL, headers=headers, data=json.dumps(payload), verify=False)
        if response.status_code != 200:
            print(f"[Splunk] Failed to send event: {response.text}")
    except Exception as e:
        print(f"[Splunk] Exception sending event: {e}")


@app.route("/der/<der_id>/status", methods=["POST"])
def update_der_status(der_id):
    try:
        xml_data = request.data
        root = etree.fromstring(xml_data)

        voltage = root.findtext("voltage")
        current = root.findtext("current")
        realPower = root.findtext("realPower")

        der_status[der_id] = {
            "voltage": voltage,
            "current": current,
            "realPower": realPower
        }

        # Include raw HTTP request info in the log
        log_msg = (
            f"{request.remote_addr} - - [{time.strftime('%d/%b/%Y %H:%M:%S')}] "
            f'"{request.method} {request.path} HTTP/{request.environ.get("SERVER_PROTOCOL")}" 200 -\n'
            f"[SERVER - {request.scheme.upper()}] Updated DER {der_id}: {der_status[der_id]}"
        )
        print(log_msg)
        send_to_splunk(log_msg)  # Send event to Splunk

        return jsonify({"message": "DER status updated", "DER": der_id}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/der/<der_id>/control", methods=["GET"])
def get_der_control(der_id):
    control_command = {
        "mRID": der_id,
        "command": "reducePower",
        "setPoint": "1.5"  # kW
    }

    # Include raw HTTP request info in the log
    log_msg = (
        f"{request.remote_addr} - - [{time.strftime('%d/%b/%Y %H:%M:%S')}] "
        f'"{request.method} {request.path} HTTP/{request.environ.get("SERVER_PROTOCOL")}" 200 -\n'
        f"[SERVER - {request.scheme.upper()}] Sent control for DER {der_id}"
    )
    print(log_msg)
    send_to_splunk(log_msg)  # Send event to Splunk

    return jsonify(control_command), 200


# Function to run a Flask server instance
def run_flask_server(host, port, ssl_context=None, protocol_name="HTTP"):
    print(f"Starting {protocol_name} server on {host}:{port}...")
    app.run(host=host, port=port, ssl_context=ssl_context)


if __name__ == "__main__":
    HTTPS_PORT = 8443
    HTTP_PORT = 8080

    # Start HTTPS server in a separate thread
    https_thread = threading.Thread(target=run_flask_server,
                                    args=("0.0.0.0", HTTPS_PORT, ("server.crt", "server.key"), "HTTPS"))
    https_thread.daemon = True
    https_thread.start()

    # Start HTTP server in a separate thread
    http_thread = threading.Thread(target=run_flask_server,
                                   args=("0.0.0.0", HTTP_PORT, None, "HTTP"))
    http_thread.daemon = True
    http_thread.start()

    print(f"\nMock IEEE 2030.5 Server running both HTTP on port {HTTP_PORT} and HTTPS on port {HTTPS_PORT}.")
    print("Press Ctrl+C to stop both servers.")

    try:
        while True:
            threading.Event().wait(1)
    except KeyboardInterrupt:
        print("\nServer stopped by user.")
