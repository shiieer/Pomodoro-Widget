"""
Tests for core/task_store.py — TaskStore logic.

Covers:
  - add: new task structure, auto-active promotion, whitespace strip
  - all: ordering (active → todo → done)
  - active_task: returns correct task / None
  - pending_count / done_count
  - set_active: only one active at a time, done tasks can't be active
  - toggle_done: marks done, clears active, promotes next
  - toggle_done back to undone
  - delete: removes task, promotes next if was active
  - clear_done: removes all completed tasks
  - reorder: swaps positions
  - persistence: save then reload
  - edge cases: empty store, all done, unknown ids
"""

import json

import pytest

from core.task_store import TaskStore

# ── fixture ───────────────────────────────────────────────────────────────────


@pytest.fixture
def tmp_store(tmp_path):
    """Return a fresh TaskStore backed by a temp file."""
    return TaskStore(path=tmp_path / "tasks.json")


# ── add ───────────────────────────────────────────────────────────────────────


class TestAdd:
    def test_add_returns_task_dict(self, tmp_store):
        t = tmp_store.add("Do the dishes")
        assert t["title"] == "Do the dishes"
        assert t["done"] is False
        assert t["id"]  # non-empty string

    def test_add_strips_whitespace(self, tmp_store):
        t = tmp_store.add("  My Task  ")
        assert t["title"] == "My Task"

    def test_first_task_becomes_active(self, tmp_store):
        t = tmp_store.add("First")
        assert t["active"] is True

    def test_second_task_not_auto_active(self, tmp_store):
        tmp_store.add("First")
        t2 = tmp_store.add("Second")
        assert t2["active"] is False

    def test_add_increments_pending_count(self, tmp_store):
        tmp_store.add("A")
        tmp_store.add("B")
        assert tmp_store.pending_count() == 2

    def test_add_saves_to_file(self, tmp_path):
        path = tmp_path / "tasks.json"
        store = TaskStore(path=path)
        store.add("Saved task")
        loaded = json.loads(path.read_text())
        assert any(t["title"] == "Saved task" for t in loaded)


# ── all / ordering ────────────────────────────────────────────────────────────


class TestAll:
    def test_ordering_active_then_todo_then_done(self, tmp_store):
        tmp_store.add("A")  # becomes active (first)
        t2 = tmp_store.add("B")
        tmp_store.add("C")
        tmp_store.toggle_done(t2["id"])  # mark B done

        ordered = tmp_store.all()
        titles = [t["title"] for t in ordered]
        assert titles[0] == "A"  # active first
        assert "C" in titles[1:]  # todo next
        assert titles[-1] == "B"  # done last

    def test_all_returns_list(self, tmp_store):
        assert isinstance(tmp_store.all(), list)

    def test_all_on_empty_store(self, tmp_store):
        assert tmp_store.all() == []


# ── active_task ───────────────────────────────────────────────────────────────


class TestActiveTask:
    def test_active_task_is_first_added(self, tmp_store):
        tmp_store.add("Focus on this")
        assert tmp_store.active_task()["title"] == "Focus on this"

    def test_active_task_returns_none_when_empty(self, tmp_store):
        assert tmp_store.active_task() is None

    def test_active_task_returns_none_when_all_done(self, tmp_store):
        t = tmp_store.add("Done")
        tmp_store.toggle_done(t["id"])
        assert tmp_store.active_task() is None


# ── counts ────────────────────────────────────────────────────────────────────


class TestCounts:
    def test_pending_count_zero_initially(self, tmp_store):
        assert tmp_store.pending_count() == 0

    def test_done_count_zero_initially(self, tmp_store):
        assert tmp_store.done_count() == 0

    def test_pending_decreases_when_done(self, tmp_store):
        t = tmp_store.add("Task")
        assert tmp_store.pending_count() == 1
        tmp_store.toggle_done(t["id"])
        assert tmp_store.pending_count() == 0

    def test_done_count_increases_when_done(self, tmp_store):
        t = tmp_store.add("Task")
        tmp_store.toggle_done(t["id"])
        assert tmp_store.done_count() == 1

    def test_counts_with_mixed_tasks(self, tmp_store):
        t1 = tmp_store.add("A")
        tmp_store.add("B")
        t3 = tmp_store.add("C")
        tmp_store.toggle_done(t1["id"])
        tmp_store.toggle_done(t3["id"])
        assert tmp_store.pending_count() == 1
        assert tmp_store.done_count() == 2


# ── set_active ────────────────────────────────────────────────────────────────


class TestSetActive:
    def test_set_active_changes_active_task(self, tmp_store):
        tmp_store.add("First")
        t2 = tmp_store.add("Second")
        tmp_store.set_active(t2["id"])
        assert tmp_store.active_task()["id"] == t2["id"]

    def test_only_one_active_at_a_time(self, tmp_store):
        tmp_store.add("A")
        tmp_store.add("B")
        t3 = tmp_store.add("C")
        tmp_store.set_active(t3["id"])
        active_count = sum(1 for t in tmp_store.all() if t.get("active"))
        assert active_count == 1

    def test_done_task_cannot_be_set_active(self, tmp_store):
        t = tmp_store.add("Done task")
        tmp_store.toggle_done(t["id"])
        tmp_store.set_active(t["id"])  # should be silently ignored
        assert tmp_store.active_task() is None

    def test_set_active_unknown_id_no_crash(self, tmp_store):
        tmp_store.add("A")
        tmp_store.set_active("nonexistent-id")  # must not raise
        # active should be cleared since no match
        assert tmp_store.active_task() is None


# ── toggle_done ───────────────────────────────────────────────────────────────


class TestToggleDone:
    def test_marks_task_as_done(self, tmp_store):
        t = tmp_store.add("Finish report")
        tmp_store.toggle_done(t["id"])
        done_tasks = [x for x in tmp_store.all() if x["id"] == t["id"]]
        assert done_tasks[0]["done"] is True

    def test_done_task_is_no_longer_active(self, tmp_store):
        t = tmp_store.add("Task")
        assert tmp_store.active_task()["id"] == t["id"]
        tmp_store.toggle_done(t["id"])
        assert (
            tmp_store.active_task() is None or tmp_store.active_task()["id"] != t["id"]
        )

    def test_promotes_next_task_when_active_is_done(self, tmp_store):
        t1 = tmp_store.add("A")
        tmp_store.add("B")
        tmp_store.add("C")
        tmp_store.toggle_done(t1["id"])  # complete active task
        assert tmp_store.active_task() is not None
        assert tmp_store.active_task()["done"] is False

    def test_toggle_done_twice_marks_undone(self, tmp_store):
        t = tmp_store.add("Task")
        tmp_store.toggle_done(t["id"])
        tmp_store.toggle_done(t["id"])  # toggle back
        task = next(x for x in tmp_store.all() if x["id"] == t["id"])
        assert task["done"] is False

    def test_toggle_unknown_id_no_crash(self, tmp_store):
        tmp_store.toggle_done("unknown-id")  # must not raise


# ── delete ────────────────────────────────────────────────────────────────────


class TestDelete:
    def test_delete_removes_task(self, tmp_store):
        t = tmp_store.add("Remove me")
        tmp_store.delete(t["id"])
        assert not any(x["id"] == t["id"] for x in tmp_store.all())

    def test_delete_active_promotes_next(self, tmp_store):
        t1 = tmp_store.add("A")
        t2 = tmp_store.add("B")
        tmp_store.delete(t1["id"])  # delete active
        assert tmp_store.active_task() is not None
        assert tmp_store.active_task()["id"] == t2["id"]

    def test_delete_non_active_does_not_change_active(self, tmp_store):
        t1 = tmp_store.add("A")
        t2 = tmp_store.add("B")
        tmp_store.delete(t2["id"])  # delete non-active
        assert tmp_store.active_task()["id"] == t1["id"]

    def test_delete_last_task_leaves_empty_store(self, tmp_store):
        t = tmp_store.add("Only task")
        tmp_store.delete(t["id"])
        assert tmp_store.all() == []
        assert tmp_store.active_task() is None

    def test_delete_unknown_id_no_crash(self, tmp_store):
        tmp_store.delete("nonexistent-id")  # must not raise


# ── clear_done ────────────────────────────────────────────────────────────────


class TestClearDone:
    def test_clear_removes_all_done_tasks(self, tmp_store):
        tmp_store.add("Keep")
        t2 = tmp_store.add("Done 1")
        t3 = tmp_store.add("Done 2")
        tmp_store.toggle_done(t2["id"])
        tmp_store.toggle_done(t3["id"])
        tmp_store.clear_done()
        remaining = tmp_store.all()
        assert len(remaining) == 1
        assert remaining[0]["title"] == "Keep"

    def test_clear_done_keeps_undone_tasks(self, tmp_store):
        tmp_store.add("A")
        tmp_store.add("B")
        tmp_store.clear_done()
        assert tmp_store.pending_count() == 2

    def test_clear_done_on_empty_no_crash(self, tmp_store):
        tmp_store.clear_done()  # must not raise


# ── reorder ───────────────────────────────────────────────────────────────────


class TestReorder:
    def test_reorder_changes_position(self, tmp_store):
        tmp_store.add("A")
        tmp_store.add("B")
        tmp_store.add("C")
        tmp_store.reorder(0, 2)
        titles = [t["title"] for t in tmp_store._tasks]
        assert titles[2] == "A"

    def test_reorder_out_of_bounds_no_crash(self, tmp_store):
        tmp_store.add("A")
        tmp_store.reorder(0, 99)  # must not raise
        tmp_store.reorder(-1, 0)  # must not raise


# ── persistence ───────────────────────────────────────────────────────────────


class TestPersistence:
    def test_reload_recovers_tasks(self, tmp_path):
        path = tmp_path / "tasks.json"
        store1 = TaskStore(path=path)
        store1.add("Persisted task")

        store2 = TaskStore(path=path)
        assert any(t["title"] == "Persisted task" for t in store2.all())

    def test_reload_preserves_done_state(self, tmp_path):
        path = tmp_path / "tasks.json"
        store1 = TaskStore(path=path)
        t = store1.add("Task")
        store1.toggle_done(t["id"])

        store2 = TaskStore(path=path)
        task = next(x for x in store2.all() if x["id"] == t["id"])
        assert task["done"] is True

    def test_reload_preserves_active_state(self, tmp_path):
        path = tmp_path / "tasks.json"
        store1 = TaskStore(path=path)
        store1.add("A")
        t2 = store1.add("B")
        store1.set_active(t2["id"])

        store2 = TaskStore(path=path)
        assert store2.active_task()["id"] == t2["id"]

    def test_corrupt_file_loads_empty(self, tmp_path):
        path = tmp_path / "tasks.json"
        path.write_text("not json at all", encoding="utf-8")
        store = TaskStore(path=path)
        assert store.all() == []

    def test_missing_file_starts_empty(self, tmp_path):
        path = tmp_path / "does_not_exist.json"
        store = TaskStore(path=path)
        assert store.all() == []


# ── edge cases ────────────────────────────────────────────────────────────────


class TestEdgeCases:
    def test_no_double_active_after_multiple_adds(self, tmp_store):
        for i in range(10):
            tmp_store.add(f"Task {i}")
        active = [t for t in tmp_store.all() if t.get("active")]
        assert len(active) == 1

    def test_promote_skips_done_tasks(self, tmp_store):
        t1 = tmp_store.add("Active")
        t2 = tmp_store.add("Also done soon")
        t3 = tmp_store.add("Should be promoted")
        tmp_store.toggle_done(t2["id"])  # pre-mark t2 done
        tmp_store.toggle_done(t1["id"])  # complete active
        # t2 is done, so t3 should be promoted
        assert tmp_store.active_task()["id"] == t3["id"]

    def test_all_done_gives_no_active(self, tmp_store):
        tasks = [tmp_store.add(f"T{i}") for i in range(3)]
        for t in tasks:
            tmp_store.toggle_done(t["id"])
        assert tmp_store.active_task() is None
