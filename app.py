import os
from flask import Flask, render_template
import requests

app = Flask(__name__)

CL_SERVICE_URL = os.getenv("CL_SERVICE_URL", "http://cl:5001").rstrip("/")
WEATHER_SERVICE_URL = os.getenv("WEATHER_SERVICE_URL", "http://weather:5002").rstrip("/")
ASTRONOMY_SERVICE_URL = os.getenv("ASTRONOMY_SERVICE_URL", "http://astronomy:5003").rstrip("/")


def get_json(base, path):
    try:
        response = requests.get(f"{base}{path}", timeout=4)
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return None


@app.route("/")
def index():
    weather = get_json(WEATHER_SERVICE_URL, "/api/current")
    astronomy = get_json(ASTRONOMY_SERVICE_URL, "/api/latest")
    return render_template(
        "index.html",
        weather=weather,
        astronomy=astronomy,
        cl_url=CL_SERVICE_URL,
        weather_url=WEATHER_SERVICE_URL,
        astronomy_url=ASTRONOMY_SERVICE_URL,
    )


@app.route("/weather")
def weather():
    return render_template("service.html", title="Weather", service_url=WEATHER_SERVICE_URL)


@app.route("/forecast")
def forecast():
    return render_template("service.html", title="Forecast", service_url=f"{WEATHER_SERVICE_URL}/forecast")


@app.route("/astronomy")
def astronomy():
    return render_template("service.html", title="Astronomy", service_url=ASTRONOMY_SERVICE_URL)


@app.route("/listings")
def listings():
    return render_template("service.html", title="Local Listings", service_url=CL_SERVICE_URL)


@app.route("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
