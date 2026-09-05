from flask import Flask, jsonify
import requests
from datetime import datetime, timezone, timedelta

app = Flask(__name__)

__version__ = "v0.1.0"

SENSEBOX_IDS = [
    "5eba5fbad46fb8001b799786",
    "5c21ff8f919bf8001adf2488",
    "5ade1acf223bd80019a1011c",
]

MAX_AGE = timedelta(hours=1)

@app.route("/version", methods=["GET"])
def version():
    return jsonify({"version": __version__})

@app.route("/temperature", methods=["GET"])
def temperature():
    readings = []
    now = datetime.now(timezone.utc)

    for box_id in SENSEBOX_IDS:
        url = f"https://api.opensensemap.org/boxes/{box_id}"
        response = requests.get(url, timeout=5)

        if response.status_code != 200:
            continue

        data = response.json()

        for sensor in data.get("sensors", []):
            title = sensor.get("title", "").lower()
            if title not in ("temperatur", "temperature"):
                continue

            last = sensor.get("lastMeasurement")
            if not last or not last.get("value"):
                continue

            measured_at = datetime.fromisoformat(last["createdAt"].replace("Z", "+00:00"))
            age = now - measured_at

            if age > MAX_AGE:
                continue

            readings.append(float(last["value"]))

    if not readings:
        return jsonify({"error": "No fresh temperature data available (within last hour)"}), 503

    average = sum(readings) / len(readings)

    return jsonify({
        "temperature": round(average, 2),
        "unit": "celsius",
        "sensors_used": len(readings)
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
