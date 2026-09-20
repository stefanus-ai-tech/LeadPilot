from unittest.mock import Mock

import batch_process


def test_folder_continues_after_invalid_file(tmp_path, monkeypatch):
    (tmp_path / "a.csv").touch()
    (tmp_path / "b.csv").touch()
    (tmp_path / "notes.txt").touch()
    (tmp_path / "nested").mkdir()
    (tmp_path / "nested" / "ignored.csv").touch()
    process = Mock(side_effect=[ValueError("Missing headers"), (tmp_path, {"error": 0})])
    monkeypatch.setattr(batch_process, "process_csv", process)
    monkeypatch.setattr("sys.argv", ["batch_process.py", str(tmp_path)])
    assert batch_process.main() == 1
    assert [call.args[0].name for call in process.call_args_list] == ["a.csv", "b.csv"]


def test_cancelled_picker_does_not_process(monkeypatch):
    process = Mock()
    picker = Mock(return_value="")
    monkeypatch.setattr(batch_process, "process_csv", process)
    monkeypatch.setattr(batch_process, "pick_path", picker)
    monkeypatch.setattr("sys.argv", ["batch_process.py", "--pick", "file"])
    assert batch_process.main() == 0
    picker.assert_called_once_with("file")
    process.assert_not_called()
