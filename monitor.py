

import csv
import os
from datetime import datetime, timezone
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

SOURCES = {
    "chaturbate": "https://chaturbate.com/",
    "stripchat": "https://stripchat.com/",
}

FILE = "monitor_history.csv"


def check_source(name, url):
    now = datetime.now(timezone.utc).isoformat()
    status = "ok"
    http_code = ""
    error = ""

    try:
        request = Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (compatible; PublicStatsMonitor/1.0)"}
        )
        with urlopen(request, timeout=20) as response:
            http_code = response.status
    except HTTPError as exc:
        status = "error"
        http_code = exc.code
        error = str(exc)
    except (URLError, TimeoutError, OSError) as exc:
        status = "error"
        error = str(exc)

    return {
        "time_utc": now,
        "platform": name,
        "http_status": http_code,
        "status": status,
        "error": error,
        "models_online": "",
        "viewers_online": "",
    }


def main():
    rows = [check_source(name, url) for name, url in SOURCES.items()]
    exists = os.path.exists(FILE)

    with open(FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        if not exists:
            writer.writeheader()
        writer.writerows(rows)

    for row in rows:
        print(
            f"{row['platform']}: {row['status']}, "
            f"HTTP {row['http_status'] or '-'}"
        )

    print("Saved checks to", FILE)


if __name__ == "__main__":
    main()
