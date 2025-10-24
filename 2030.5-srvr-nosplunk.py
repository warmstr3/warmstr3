
# Import Libaries
from flask import Flask, request, jsonify
from lxml import etree
import threading # Import threading module

app = Flask(__name__)

# Simulated DER status database (in memory)
der_status = {}

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

        print(f"[SERVER - {request.scheme.upper()}] Updated DER {der_id}: {der_status[der_id]}")
        return jsonify({"message": "DER status updated", "DER": der_id}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/der/<der_id>/control", methods=["GET"])
def get_der_control(der_id):
    # Simulate returning control command (e.g., curtailment)
    control_command = {
        "mRID": der_id,
        "command": "reducePower",
        "setPoint": "1.5"  # kW
    }
    print(f"[SERVER - {request.scheme.upper()}] Sent control for DER {der_id}")
    return jsonify(control_command), 200

# Function to run a Flask server instance
def run_flask_server(host, port, ssl_context=None, protocol_name="HTTP"):
    print(f"Starting {protocol_name} server on {host}:{port}...")
    app.run(host=host, port=port, ssl_context=ssl_context)

if __name__ == "__main__":
    HTTPS_PORT = 8443
    HTTP_PORT = 8080 # Define a port for HTTP traffic

    # Start HTTPS server in a separate thread
    https_thread = threading.Thread(target=run_flask_server,
                                    args=("0.0.0.0", HTTPS_PORT, ("server.crt", "server.key"), "HTTPS"))
    https_thread.daemon = True # Allow main program to exit even if threads are running
    https_thread.start()

    # Start HTTP server in a separate thread
    http_thread = threading.Thread(target=run_flask_server,
                                   args=("0.0.0.0", HTTP_PORT, None, "HTTP")) # ssl_context=None for HTTP
    http_thread.daemon = True # Allow main program to exit even if threads are running
    http_thread.start()

    print(f"\nMock IEEE 2030.5 Server running both HTTP on port {HTTP_PORT} and HTTPS on port {HTTPS_PORT}.")
    print("Press Ctrl+C to stop both servers.")

    # Keep the main thread alive so the daemon threads can continue running
    try:
        while True:
            threading.Event().wait(1) # Wait for 1 second, then repeat
    except KeyboardInterrupt:
        print("\nServer stopped by user.")
