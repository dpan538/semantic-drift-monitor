from datetime import datetime
from pathlib import Path


def log_alert(alerts: list[dict], log_path: Path) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as handle:
        for alert in alerts:
            messages = "; ".join(alert["messages"])
            handle.write(f"{datetime.now().isoformat()} | {alert['product_id']} | {alert['month']} | {messages}\n")


def send_alert(*args, **kwargs) -> None:
    raise NotImplementedError("Email alerting is a second-stage feature. Use log_alert for the pilot.")

