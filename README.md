# localsonly

A front-end dashboard that brings together the existing CL, Weather, and Astronomy applications.

## Architecture

localsonly is the presentation layer. The existing applications remain responsible for their own databases, schedulers, scraping, weather collection, astronomy collection, and APIs.

There are two kinds of service URLs:

- `*_SERVICE_URL` — used by the localsonly container to call a service.
- `*_PUBLIC_URL` — used by the browser for service pages embedded in the dashboard.

For Docker Compose, service URLs can use container DNS names while public URLs use the host-facing addresses.

## Environment

- `CL_SERVICE_URL` — default `http://cl:5001`
- `WEATHER_SERVICE_URL` — default `http://weather:5002`
- `ASTRONOMY_SERVICE_URL` — default `http://astronomy:5003`
- `CL_PUBLIC_URL` — defaults to `CL_SERVICE_URL`
- `WEATHER_PUBLIC_URL` — defaults to `WEATHER_SERVICE_URL`
- `ASTRONOMY_PUBLIC_URL` — defaults to `ASTRONOMY_SERVICE_URL`
- `FLASK_SECRET_KEY` — session secret for localsonly
- `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` — Google OAuth credentials owned by localsonly
- `SSO_SECRET` — shared signing secret used for the short-lived CL SSO handoff

For a browser accessing the services through localhost:

```yaml
environment:
  CL_SERVICE_URL: http://cl:5001
  WEATHER_SERVICE_URL: http://weather:5002
  ASTRONOMY_SERVICE_URL: http://astronomy:5003
  CL_PUBLIC_URL: http://localhost:5001
  WEATHER_PUBLIC_URL: http://localhost:5002
  ASTRONOMY_PUBLIC_URL: http://localhost:5003
```

## Run

```bash
docker build -t localsonly .
docker run -p 5000:5000 localsonly
```

Then open `http://localhost:5000`.

## Pages

- `/` — unified local dashboard
- `/weather` — current Weather service
- `/forecast` — Weather forecast
- `/astronomy` — Astronomy service
- `/listings` — CL
- `/health` — front-end health check


## Docker Compose

The Compose file runs localsonly on port 5000 and connects it to the existing CL, Weather, and Astronomy Docker networks.

Start the front end:

```bash
docker compose up -d --build
```

The existing service containers must already be running on the external `cl_shared_data` Docker network.

Open:

```
http://localhost:5000
```

localsonly talks to the services over Docker DNS:
- `cl-web-1:5001`
- `weather-web-1:5002`
- `astronomy-web-1:5003`

Google sign-in is owned by localsonly. After authentication, localsonly issues a short-lived signed SSO assertion to CL, where the existing CL `users` record and blog permissions are preserved. Register the Google OAuth callback at `http://localhost:5000/auth/callback` (and `http://127.0.0.1:5000/auth/callback` if you use that hostname).

Your browser follows the public URLs, which default to localhost ports.
