from pystash.core.event import Event


def test_nested_set_get_delete():
    e = Event()
    e.set("[foo][bar]", 7)
    assert e.get("[foo][bar]") == 7
    e.delete("[foo][bar]")
    assert e.get("[foo][bar]") is None
