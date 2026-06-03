import pandas as pd

from config import ALERT_THRESHOLD_DRIFT, ALERT_THRESHOLD_LOCKIN, ALERT_THRESHOLD_SKEPTICISM


class DriftDetector:
    def __init__(self, panel: pd.DataFrame):
        self.panel = panel.copy()

    def check_alerts(self) -> list[dict]:
        alerts: list[dict] = []
        if self.panel.empty:
            return alerts

        latest_rows = self.panel.sort_values("month").groupby("product_id").tail(1)
        for _, row in latest_rows.iterrows():
            product_alerts: list[str] = []
            if row.get("semantic_gap_coarse", 0) > ALERT_THRESHOLD_DRIFT:
                product_alerts.append(f"semantic gap {row['semantic_gap_coarse']:.3f}")
            if row.get("skepticism_ratio", 0) > ALERT_THRESHOLD_SKEPTICISM:
                product_alerts.append(f"skepticism ratio {row['skepticism_ratio']:.2%}")
            if row.get("scenario_entropy", 1) < ALERT_THRESHOLD_LOCKIN:
                product_alerts.append(f"low scenario entropy {row['scenario_entropy']:.3f}")
            if product_alerts:
                alerts.append(
                    {
                        "product_id": row["product_id"],
                        "month": row["month"],
                        "messages": product_alerts,
                    }
                )
        return alerts

