from src.MonitorProcesses import *


class TestMonitorProcesses:
    def test_process_added_zero(self):
        old_set = ["one"]
        new_set = ["one"]
        diff = get_added_processes(old_set, new_set)
        assert len(diff) == 0
        assert diff == []

    def test_process_added_one(self):
        old_set = ["one"]
        new_set = ["one", "two"]
        diff = get_added_processes(old_set, new_set)
        assert len(diff) == 1
        assert diff == ["two"]

    def test_process_added_multi(self):
        old_set = ["one"]
        new_set = ["one", "two", "three"]
        diff = get_added_processes(old_set, new_set)
        assert len(diff) == 2
        assert diff == ["two", "three"]

    def test_process_added_when_also_a_removal(self):
        old_set = ["one", "three"]
        new_set = ["one", "two"]
        diff = get_added_processes(old_set, new_set)
        assert len(diff) == 1
        assert diff == ["two"]

    def test_process_removed_zero(self):
        old_set = ["one"]
        new_set = ["one"]
        diff = get_removed_processes(old_set, new_set)
        assert len(diff) == 0
        assert diff == []

    def test_process_removed_one(self):
        old_set = ["one", "two"]
        new_set = ["one"]
        diff = get_removed_processes(old_set, new_set)
        assert len(diff) == 1
        assert diff == ["two"]

    def test_process_removed_multi(self):
        old_set = ["one", "two", "three"]
        new_set = ["one"]
        diff = get_removed_processes(old_set, new_set)
        assert len(diff) == 2
        assert diff == ["two", "three"]

    def test_process_removed_when_also_an_addition(self):
        old_set = ["one", "two"]
        new_set = ["one", "three"]
        diff = get_removed_processes(old_set, new_set)
        assert len(diff) == 1
        assert diff == ["two"]
