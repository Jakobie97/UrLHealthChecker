# URL Health Checker

Simple Python script that checks a list of URLs and logs status codes to a local SQLite database.

**Files:**
- `main.py`: main script that reads `config.yaml`, queries URLs, and inserts rows into the database.
- `config.yaml`: list of URLs and settings (request timeout and check frequency).
- `Database/`: folder where the SQLite DB file `MyUrlChecksDBStorage.db` lives.
- `requirements.txt`: Python dependencies (`requests`, `PyYAML`).
- `Dockerfile` / `.dockerignore`: for building a container image of the script.

**Requirements:**
- Python 3.11 (recommended) or compatible Python 3.x
- Docker (optional — for containerized runs)

**Configuration (`config.yaml`)**
- `urls_to_monitor`: YAML list of URL strings (must include scheme `http://` or `https://`).
- `settings.request_timeout_seconds`: float or int for request timeout.
- `settings.check_frequency_minutes`: how often you intend to check (the script currently runs once and exits).

**Database**
The script writes to `./Database/MyUrlChecksDBStorage.db` and expects a table named `Url_Responses`. If you need to create the table manually, use:

```sql
CREATE TABLE IF NOT EXISTS Url_Responses (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  url TEXT,
  status_code INTEGER,
  timestamp TEXT
);
```

Make sure the `Database/` directory exists and is writable before running the script or the container.

**Build & Run with Docker**
Build the image from the project root (`UrLHealthChecker`):

```bash
docker build -t url-health-checker .
```

Run the container once and persist the database to the host `Database/` folder (recommended):

```bash
# From project root (bash)
docker run --rm -v "$(pwd)/Database:/app/Database" url-health-checker
```

This mounts your local `Database/` into the container so the SQLite file persists across runs.

**Run locally (without Docker)**
Create a virtualenv and run:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

**Scheduling / Periodic Runs**
The current `main.py` executes the checks once and exits. To run it periodically consider one of the following options:

- Host cron (example runs every 15 minutes):

```cron
*/15 * * * * cd /absolute/path/to/UrLHealthChecker && docker run --rm -v "/absolute/path/to/UrLHealthChecker/Database:/app/Database" url-health-checker
```

- Use `docker-compose` with a cron-like scheduler container or an external scheduler.
- Modify `main.py` to loop indefinitely using `time.sleep(CHECK_FREQUENCY * 60)` between checks.

**Notes & Tips**
- The container prints status to stdout — use Docker logging or redirect logs when running under a scheduler.
- Ensure `config.yaml` contains valid URLs and settings before building the image (the Dockerfile copies `config.yaml` into the image).
- If you want the container to be able to reconfigure `config.yaml` without rebuilding, mount it as a volume: `-v "$(pwd)/config.yaml:/app/config.yaml:ro"`.

If you want, I can:
- Add a small `docker-compose.yml` example for scheduling.
- Modify `main.py` to run continuously according to `CHECK_FREQUENCY`.
