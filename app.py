import os
from flask import Flask, redirect, render_template, request, session, url_for
import requests
from authlib.integrations.flask_client import OAuth
from itsdangerous import URLSafeTimedSerializer

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "localsonly-local")
app.config["GOOGLE_CLIENT_ID"] = os.getenv("GOOGLE_CLIENT_ID", "")
app.config["GOOGLE_CLIENT_SECRET"] = os.getenv("GOOGLE_CLIENT_SECRET", "")
app.config["SSO_SECRET"] = os.getenv("SSO_SECRET", app.config["SECRET_KEY"])

oauth = OAuth(app)
if app.config["GOOGLE_CLIENT_ID"] and app.config["GOOGLE_CLIENT_SECRET"]:
    oauth.register(name="google", client_id=app.config["GOOGLE_CLIENT_ID"], client_secret=app.config["GOOGLE_CLIENT_SECRET"], server_metadata_url="https://accounts.google.com/.well-known/openid-configuration", client_kwargs={"scope": "openid email profile"})


CL_SERVICE_URL = os.getenv("CL_SERVICE_URL", "http://cl:5001").rstrip("/")
WEATHER_SERVICE_URL = os.getenv("WEATHER_SERVICE_URL", "http://weather:5002").rstrip("/")
META_SERVICE_URL = os.getenv("META_SERVICE_URL", "http://meta-web-1:5004").rstrip("/")
ASTRONOMY_SERVICE_URL = os.getenv("ASTRONOMY_SERVICE_URL", "http://astronomy:5003").rstrip("/")
CL_PUBLIC_URL = os.getenv("CL_PUBLIC_URL", CL_SERVICE_URL).rstrip("/")
WEATHER_PUBLIC_URL = os.getenv("WEATHER_PUBLIC_URL", WEATHER_SERVICE_URL).rstrip("/")
META_PUBLIC_URL = os.getenv("META_PUBLIC_URL", "http://localhost:5004").rstrip("/")
ASTRONOMY_PUBLIC_URL = os.getenv("ASTRONOMY_PUBLIC_URL", ASTRONOMY_SERVICE_URL).rstrip("/")


def get_current_user():
    if not session.get("user_sub"):
        return None
    return {"sub": session["user_sub"], "email": session.get("user_email", ""), "name": session.get("user_name", ""), "picture": session.get("user_picture", "")}


def sso_token():
    return URLSafeTimedSerializer(app.config["SSO_SECRET"], salt="localsonly-sso-v1").dumps(get_current_user())


@app.context_processor
def auth_context():
    return {"current_user": get_current_user()}


@app.route("/auth/login")
def google_login():
    if "google" not in oauth._clients:
        return "Google OAuth is not configured.", 503
    next_url = request.args.get("next", "/")
    session["login_next"] = next_url if next_url.startswith("/") and not next_url.startswith("//") else "/"
    return oauth.google.authorize_redirect(url_for("google_callback", _external=True))


@app.route("/auth/callback")
def google_callback():
    if "google" not in oauth._clients:
        return "Google OAuth is not configured.", 503
    try:
        oauth.google.authorize_access_token()
        user_info = oauth.google.userinfo()
    except Exception as exc:
        return f"Google sign-in failed: {exc}", 502
    google_sub = user_info.get("sub") or user_info.get("email")
    email = (user_info.get("email") or "").strip()
    if not google_sub or not email or user_info.get("email_verified") is False:
        return "Google account did not return a verified email and stable identity.", 400
    next_url = session.get("login_next", "/")
    session.clear()
    session["user_sub"] = google_sub
    session["user_email"] = email
    session["user_name"] = (user_info.get("name") or email or "Google User").strip()
    session["user_picture"] = (user_info.get("picture") or "").strip()
    return redirect(next_url if next_url.startswith("/") and not next_url.startswith("//") else "/")


@app.route("/auth/logout")
def google_logout():
    session.clear()
    return redirect("/")


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
    return render_template("index.html", weather=weather, astronomy=astronomy, cl_url=CL_PUBLIC_URL, weather_url=WEATHER_PUBLIC_URL, astronomy_url=ASTRONOMY_PUBLIC_URL, meta_url=META_PUBLIC_URL)


@app.route("/weather")
def weather():
    return render_template("service.html", title="Weather", service_url=WEATHER_PUBLIC_URL, weather_url=WEATHER_PUBLIC_URL)


@app.route("/forecast")
def forecast():
    return render_template("service.html", title="Forecast", service_url=f"{WEATHER_PUBLIC_URL}/forecast", weather_url=WEATHER_PUBLIC_URL)


@app.route("/historical")
def historical():
    return render_template("service.html", title="Weather Historical Data", service_url=f"{WEATHER_PUBLIC_URL}/historical", weather_url=WEATHER_PUBLIC_URL)


@app.route("/weather/control")
def weather_control():
    return render_template("service.html", title="Weather Control Panel", service_url=f"{WEATHER_PUBLIC_URL}/control", weather_url=WEATHER_PUBLIC_URL)


@app.route("/astronomy")
def astronomy():
    return render_template("service.html", title="Astronomy", service_url=ASTRONOMY_PUBLIC_URL)

@app.route("/apod")
def apod():
    return render_template("service.html", title="APOD", service_url=f"{ASTRONOMY_PUBLIC_URL}/apod")

@app.route("/astronomy/historical")
def astronomy_historical():
    return render_template("service.html", title="Astronomy Historical Data", service_url=f"{ASTRONOMY_PUBLIC_URL}/historical")

@app.route("/astronomy/control")
def astronomy_control():
    return render_template("service.html", title="Astronomy Control Panel", service_url=f"{ASTRONOMY_PUBLIC_URL}/control")

@app.route("/apod")
def apod():
    return render_template("service.html", title="APOD", service_url=f"{ASTRONOMY_PUBLIC_URL}/apod")

@app.route("/astronomy/historical")
def astronomy_historical():
    return render_template("service.html", title="Astronomy Historical Data", service_url=f"{ASTRONOMY_PUBLIC_URL}/historical")

@app.route("/astronomy/control")
def astronomy_control():
    return render_template("service.html", title="Astronomy Control Panel", service_url=f"{ASTRONOMY_PUBLIC_URL}/control")


@app.route("/facebook")
def facebook():
    return render_template("service.html", title="Facebook", service_url=META_PUBLIC_URL)

@app.route("/facebook/control")
def facebook_control():
    return render_template("service.html", title="Facebook Control Panel", service_url=f"{META_PUBLIC_URL}/control")

@app.route("/facebook/control")
def facebook_control():
    return render_template("service.html", title="Facebook Control Panel", service_url=f"{META_PUBLIC_URL}/control")


@app.route("/listings")
def cl_service_path(path, title):
    if not get_current_user():
        return redirect(url_for("google_login", next=request.path))
    service_url = f"{CL_PUBLIC_URL}/auth/sso?next={path}&token={sso_token()}"
    return render_template("service.html", title=title, service_url=service_url)

@app.route("/listings")
def listings():
    return cl_service_path("/", "Local Listings")

@app.route("/listings/control")
def listings_control():
    return cl_service_path("/control", "CL Control Panel")


@app.route("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
