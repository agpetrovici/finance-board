from typing import Any, Dict, List


class ApexLineChartData:
    def __init__(self, labels: List[str], datasets: List[Dict[str, Any]]):
        self.labels = labels
        self.datasets = datasets

    def to_dict(self) -> dict:
        return {"labels": self.labels, "datasets": self.datasets}


class ApexColumnChartData:
    def __init__(self, series: List[str], categories: List[Dict[str, Any]]):
        self.series = series
        self.categories = categories

    def to_dict(self) -> dict:
        return {"series": self.series, "categories": self.categories}
