import os
import json
import io
from datetime import datetime, timezone, timedelta

from flask import Flask, jsonify
import requests
import redis
from minio import Minio
from minio.error import S3Error
from prometheus_flask_exporter import PrometheusMetrics


app = Flask(__name__)
metrics = PrometheusMetrics(app)

__version__ = "v0.3.0"

DEFAULT_SENSEBOX_IDS = (
    "5eba5fbad46fb8001b799786,"
    "5c21ff8f919bf8001adf2488,"
    "5ade1acf223bd80019a1011c"
)

SENSEBOX_IDS = os.environ.get("SENSEBOX_IDS", DEFAULT_SENSEBOX_IDS).split(",")

MAX_AGE = timedelta(hours=1)
CACHE_TTL = 300
CACHE_KEY = "temperature_data"

REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))

MINIO_HOST = os.environ.get("MINIO_HOST", "localhost:9000")
MINIO_ACCESS_KEY = os.environ.get("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.environ.get("MINIO_SECRET_KEY", "minioadmin123")
MINIO_BUCKET = os.environ.get("MINIO_BUCKET", "hivebox-data")

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

minio_client = Minio(
    MINIO_HOST,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False,
)


def ensure_bucket_exists():
    if not minio_client.bucket_exists(MINIO_BUCKET):
        minio_client.make_bucket(MINIO_BUCKET)


def get_status(temp):
    if temp < 10:
        return "Too Cold"
    elif temp > 36:
        return "Too Hot"
    else:
        return "Good"


def fetch_fresh_temperature_data():
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
        return None

    average = sum(readings) / len(readings)

    return {
        "temperature": round(average, 2),
        "unit": "celsius",
        "status": get_status(average),
        "sensors_used": len(readings),
        "cached_at": now.isoformat(),
    }


def refresh_cache():
    result = fetch_fresh_temperature_data()
    if result:
        redis_client.set(CACHE_KEY, json.dumps(result), ex=CACHE_TTL)
    return result


@app.route("/version", methods=["GET"])
def version():
    return jsonify({"version": __version__})


@app.route("/temperature", methods=["GET"])
def temperature():
    cached = redis_client.get(CACHE_KEY)

    if cached:
        return jsonify(json.loads(cached))

    result = refresh_cache()

    if not result:
        return jsonify({"error": "No fresh temperature data available (within last hour)"}), 503

    return jsonify(result)


@app.route("/cache", methods=["GET"])
def cache():
    result = refresh_cache()

    if not result:
        return jsonify({"error": "No fresh temperature data available (within last hour)"}), 503

    return jsonify({"message": "Cache updated", "data": result})


@app.route("/store", methods=["GET"])
def store():
    cached = redis_client.get(CACHE_KEY)

    if cached:
        data = json.loads(cached)
    else:
        data = fetch_fresh_temperature_data()

    if not data:
        return jsonify({"error": "No fresh temperature data available to store"}), 503

    ensure_bucket_exists()

    now = datetime.now(timezone.utc)
    object_name = f"temperature-{now.strftime('%Y%m%dT%H%M%S')}.json"

    payload = json.dumps(data).encode("utf-8")

    try:
        minio_client.put_object(
            MINIO_BUCKET,
            object_name,
            io.BytesIO(payload),
            length=len(payload),
            content_type="application/json",
        )
    except S3Error as e:
        return jsonify({"error": f"Failed to store data: {str(e)}"}), 500

    return jsonify({"message": "Data stored", "object": object_name})


@app.route("/readyz", methods=["GET"])
def readyz():
    reachable_boxes = 0
    for box_id in SENSEBOX_IDS:
        try:
            url = f"https://api.opensensemap.org/boxes/{box_id}"
            response = requests.get(url, timeout=3)
            if response.status_code == 200:
                reachable_boxes += 1
        except requests.RequestException:
            continue

    total_boxes = len(SENSEBOX_IDS)
    if reachable_boxes < (total_boxes / 2):
        return jsonify({"status": "not ready", "reason": "too many senseBoxes unreachable"}), 503

    return jsonify({"status": "ready"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
