from __future__ import annotations

import json
import uuid
from pathlib import Path

from config import TASKS_PATH


def _new_task(title: str) -> dict:
    return {
        "id": str(uuid.uuid4()),
        "title": title.strip(),
        "done": False,
        "active": False,
    }


class TaskStore:
    def __init__(self, path: Path = TASKS_PATH):
        self.path = path
        self._tasks: list[dict] = []
        self.load()

    # ── persistence ───────────────────────────────────────────────────────────

    def load(self) -> None:
        if not self.path.exists():
            self._tasks = []
            return
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            if isinstance(data, list):
                self._tasks = data
        except (json.JSONDecodeError, OSError):
            self._tasks = []

    def save(self) -> None:
        self.path.write_text(
            json.dumps(self._tasks, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    # ── read ──────────────────────────────────────────────────────────────────

    def all(self) -> list[dict]:
        """Return a shallow copy of all tasks (ordered: active first, then todo, then done)."""
        active = [t for t in self._tasks if t.get("active")]
        todo = [t for t in self._tasks if not t.get("done") and not t.get("active")]
        done = [t for t in self._tasks if t.get("done")]
        return active + todo + done

    def active_task(self) -> dict | None:
        for t in self._tasks:
            if t.get("active"):
                return t
        return None

    def pending_count(self) -> int:
        return sum(1 for t in self._tasks if not t.get("done"))

    def done_count(self) -> int:
        return sum(1 for t in self._tasks if t.get("done"))

    # ── write ─────────────────────────────────────────────────────────────────

    def add(self, title: str) -> dict:
        task = _new_task(title)
        # if nothing is active yet, make the first task active automatically
        if not any(t.get("active") for t in self._tasks) and not any(
            not t.get("done") for t in self._tasks
        ):
            task["active"] = True
        self._tasks.append(task)
        self.save()
        return task

    def set_active(self, task_id: str) -> None:
        for t in self._tasks:
            t["active"] = t["id"] == task_id and not t.get("done")
        self.save()

    def toggle_done(self, task_id: str) -> None:
        for t in self._tasks:
            if t["id"] == task_id:
                t["done"] = not t["done"]
                if t["done"]:
                    t["active"] = False
                    # promote next undone task to active
                    self._promote_next()
        self.save()

    def delete(self, task_id: str) -> None:
        was_active = any(t["id"] == task_id and t.get("active") for t in self._tasks)
        self._tasks = [t for t in self._tasks if t["id"] != task_id]
        if was_active:
            self._promote_next()
        self.save()

    def clear_done(self) -> None:
        self._tasks = [t for t in self._tasks if not t.get("done")]
        self.save()

    def reorder(self, from_index: int, to_index: int) -> None:
        if 0 <= from_index < len(self._tasks) and 0 <= to_index < len(self._tasks):
            task = self._tasks.pop(from_index)
            self._tasks.insert(to_index, task)
            self.save()

    # ── internal ──────────────────────────────────────────────────────────────

    def _promote_next(self) -> None:
        """Make the first undone task the active one (if none is already)."""
        if any(t.get("active") for t in self._tasks):
            return
        for t in self._tasks:
            if not t.get("done"):
                t["active"] = True
                break
