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
