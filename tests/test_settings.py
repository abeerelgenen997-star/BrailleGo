"""اختبارات الإعدادات."""

from pathlib import Path

from braille_go.data import db, settings


def test_settings_defaults():
    b = settings.MemorySettingsBackend()
    s = settings.Settings(b)
    assert s.mastery_threshold == 85.0
    assert s.theme in ("light", "dark")


def test_settings_persist():
    d = db.Database(":memory:")
    d.connect()
    d.initialize()
    s = settings.Settings(settings.SqliteSettingsBackend(d))
    s.set("font_scale", 1.5)
    s.set("speech_enabled", True)
    # new instance
    s2 = settings.Settings(settings.SqliteSettingsBackend(d))
    assert abs(s2.font_scale - 1.5) < 0.001
    assert s2.speech_enabled is True
    d.close()


def test_settings_coerce_bounds():
    b = settings.MemorySettingsBackend()
    s = settings.Settings(b)
    s.set("font_scale", 10.0)
    assert s.font_scale <= 3.0
    s.set("mastery_threshold", -5)
    assert s.mastery_threshold >= 0.0


def test_settings_reset():
    b = settings.MemorySettingsBackend()
    s = settings.Settings(b)
    s.set("theme", "dark")
    s.reset()
    assert s.theme == "light"
