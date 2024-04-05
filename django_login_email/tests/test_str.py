def test_format():
    assert "hello {name}".format(name="world") == "hello world"
