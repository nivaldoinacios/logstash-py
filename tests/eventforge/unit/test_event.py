from eventforge.core.event import Event


def test_event_field_reference_operations():
    event = Event.new("hello")
    event.set("[a][b]", 1)
    assert event.get("[a][b]") == 1

    event.append("[a][list]", "x")
    event.append("[a][list]", "y")
    assert event.get("[a][list]") == ["x", "y"]

    event.rename("[a][b]", "[a][c]")
    assert event.get("[a][b]") is None
    assert event.get("[a][c]") == 1

    removed = event.remove("[a][c]")
    assert removed == 1
    assert event.get("[a][c]") is None
