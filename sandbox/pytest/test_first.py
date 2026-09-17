def clean_title(raw):
    return raw.strip()

def test_fnb_remove_space():
    assert clean_title('   hello pytest    ')=='hello pytest'

def test_no_space_no_change():
    assert clean_title('hi pytest')=='hi pytest'

def test_empty_title():
    assert clean_title('    ')==''

