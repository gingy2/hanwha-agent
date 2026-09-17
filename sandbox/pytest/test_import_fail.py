from app.core.config import get_settings

def test_get_settings():
    assert get_settings().app_mode=='mock'