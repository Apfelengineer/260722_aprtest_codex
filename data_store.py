"""CSV persistence for なんでも質問保存箱."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


CSV_NAME = "data.csv"
FIELDNAMES = ("質問", "回答")


@dataclass(frozen=True)
class QuestionAnswer:
    question: str
    answer: str


class CsvStore:
    def __init__(self, folder: str | Path) -> None:
        self.folder = Path(folder).expanduser().resolve()
        self.path = self.folder / CSV_NAME

    def ensure_ready(self) -> None:
        self.folder.mkdir(parents=True, exist_ok=True)
        if not self.path.exists() or self.path.stat().st_size == 0:
            with self.path.open("w", encoding="utf-8-sig", newline="") as file:
                csv.DictWriter(file, fieldnames=FIELDNAMES).writeheader()

    def append(self, item: QuestionAnswer) -> None:
        self.ensure_ready()
        with self.path.open("a", encoding="utf-8-sig", newline="") as file:
            csv.DictWriter(file, fieldnames=FIELDNAMES).writerow(
                {"質問": item.question, "回答": item.answer}
            )

    def read_all(self) -> list[QuestionAnswer]:
        self.ensure_ready()
        with self.path.open("r", encoding="utf-8-sig", newline="") as file:
            reader = csv.DictReader(file)
            if reader.fieldnames is None or not set(FIELDNAMES).issubset(reader.fieldnames):
                raise ValueError("data.csv に「質問」「回答」の見出しがありません。")
            return [
                QuestionAnswer((row.get("質問") or "").strip(), (row.get("回答") or "").strip())
                for row in reader
            ]
