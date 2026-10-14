"""إدارة قاعدة البيانات المحلية (SQLite).

التطبيق يعمل بالكامل دون اتصال بالإنترنت، ويحفظ كل شيء في قاعدة بيانات
SQLite واحدة داخل مجلّد بيانات المستخدم. تراعي هذه الوحدة:

* **السلامة عند الإغلاق المفاجئ**: وضع WAL مع commit بعد كل معاملة، حتى لا
  يُفقد تقدّم المتعلّم إذا أُغلق التطبيق بصورة غير متوقعة.
* **معالجة الأخطاء**: أي خطأ في SQLite يُحوَّل إلى :class:`DatabaseError`
  برسالة عربية مفهومة بدلًا من إظهار أثر برمجي للمستخدم.
* **التعافي من التلف**: إذا فشل فتح القاعدة أو كانت تالفة، تُنقل جانبًا
  وتُنشأ قاعدة جديدة بدل أن يتوقف التطبيق.
"""

from __future__ import annotations

import os
import shutil
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator, Sequence

#: إصدار مخطط قاعدة البيانات الحالي.
SCHEMA_VERSION = 1

#: اسم مجلّد بيانات التطبيق داخل مجلّد بيانات المستخدم.
APP_DIR_NAME = "BrailleGo"

#: اسم ملف قاعدة البيانات.
DATABASE_FILENAME = "braille_go.sqlite3"

#: متغيّر بيئة اختياري لتجاوز مجلّد البيانات (مفيد في الاختبارات).
DATA_DIR_ENV = "BRAILLE_GO_DATA_DIR"


class DatabaseError(RuntimeError):
    """خطأ في قاعدة البيانات برسالة صديقة للمستخدم."""


def default_data_dir() -> Path:
    """مجلّد بيانات التطبيق الافتراضي."""
    override = os.environ.get(DATA_DIR_ENV)
    if override:
        return Path(override).expanduser()
    appdata = os.environ.get("APPDATA")
    if appdata:
        return Path(appdata) / APP_DIR_NAME
    return Path.home() / f".{APP_DIR_NAME.lower()}"


def default_database_path() -> Path:
    """مسار قاعدة البيانات الافتراضي."""
    return default_data_dir() / DATABASE_FILENAME


def utc_now() -> str:
    """الوقت الحالي بصيغة ISO-8601 بعيدًا عن المناطق الزمنية."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


_SCHEMA_STATEMENTS: tuple[str, ...] = (
    """
    CREATE TABLE IF NOT EXISTS meta (
        key   TEXT PRIMARY KEY,
        value TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS settings (
        key        TEXT PRIMARY KEY,
        value      TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS lesson_progress (
        lesson_key    TEXT PRIMARY KEY,
        level_key     TEXT NOT NULL,
        attempts      INTEGER NOT NULL DEFAULT 0,
        best_score    REAL    NOT NULL DEFAULT 0,
        last_score    REAL    NOT NULL DEFAULT 0,
        correct_total INTEGER NOT NULL DEFAULT 0,
        answered_total INTEGER NOT NULL DEFAULT 0,
        completed     INTEGER NOT NULL DEFAULT 0,
        completed_at  TEXT,
        updated_at    TEXT    NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS exercise_results (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        exercise_key TEXT NOT NULL,
        lesson_key  TEXT NOT NULL,
        level_key   TEXT NOT NULL,
        kind        TEXT NOT NULL,
        language    TEXT NOT NULL DEFAULT 'ar',
        symbol_keys TEXT NOT NULL DEFAULT '',
        is_correct  INTEGER NOT NULL,
        given       TEXT NOT NULL DEFAULT '',
        expected    TEXT NOT NULL DEFAULT '',
        created_at  TEXT NOT NULL
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_results_lesson ON exercise_results(lesson_key)",
    "CREATE INDEX IF NOT EXISTS idx_results_correct ON exercise_results(is_correct)",
    "CREATE INDEX IF NOT EXISTS idx_results_symbols ON exercise_results(symbol_keys)",
    """
    CREATE TABLE IF NOT EXISTS symbol_stats (
        symbol_key TEXT PRIMARY KEY,
        attempts   INTEGER NOT NULL DEFAULT 0,
        correct    INTEGER NOT NULL DEFAULT 0,
        updated_at TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS app_state (
        key        TEXT PRIMARY KEY,
        value      TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """,
)


class Database:
    """غلاف آمن حول اتصال SQLite.

    يمكن استخدامه مباشرة أو عبر مدير السياق::

        with Database() as db:
            db.initialize()
    """

    def __init__(self, path: str | os.PathLike[str] | None = None) -> None:
        self.path = Path(path).expanduser() if path else default_database_path()
        self._conn: sqlite3.Connection | None = None

    # ------------------------------------------------------------------
    # Connection lifecycle
    # ------------------------------------------------------------------
    @property
    def connection(self) -> sqlite3.Connection:
        if self._conn is None:
            raise DatabaseError("قاعدة البيانات غير متصلة. استدعِ connect() أولًا.")
        return self._conn

    @property
    def is_connected(self) -> bool:
        return self._conn is not None

    def connect(self) -> sqlite3.Connection:
        """افتح الاتصال مع محاولة التعافي إذا كانت القاعدة تالفة."""
        if self._conn is not None:
            return self._conn
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
        except OSError as exc:  # pragma: no cover - depends on the file system
            raise DatabaseError(f"تعذّر إنشاء مجلّد البيانات: {exc}") from exc

        try:
            self._conn = self._open()
        except sqlite3.DatabaseError:
            # القاعدة تالفة: ننقلها جانبًا وننشئ واحدة جديدة.
            self._quarantine_corrupt_database()
            self._conn = self._open()

        self._configure()
        return self._conn

    def _open(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.path), timeout=15.0, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        # اختبار سريع للتأكد من أن الملف ليس تالفًا.
        conn.execute("PRAGMA schema_version")
        return conn

    def _configure(self) -> None:
        conn = self.connection
        # WAL يجعل الكتابة آمنة وسريعة ويقلّل خطر فقدان البيانات.
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute("PRAGMA busy_timeout=5000")

    def _quarantine_corrupt_database(self) -> None:
        if self.path.exists():
            backup = self.path.with_suffix(self.path.suffix + f".corrupt-{utc_now().replace(':', '')}")
            try:
                shutil.move(str(self.path), str(backup))
            except OSError:  # pragma: no cover - best effort
                try:
                    self.path.unlink()
                except OSError:
                    pass

    def initialize(self) -> None:
        """أنشئ الجداول وحدّث المخطط إن لزم."""
        with self.transaction() as conn:
            for statement in _SCHEMA_STATEMENTS:
                conn.execute(statement)
            conn.execute(
                "INSERT OR IGNORE INTO meta(key, value) VALUES('schema_version', ?)",
                (str(SCHEMA_VERSION),),
            )
        self._migrate()

    def _migrate(self) -> None:
        """تهيئة الترقية المستقبلية للمخطط."""
        current = self.get_meta("schema_version", "0")
        try:
            version = int(current)
        except (TypeError, ValueError):
            version = 0
        if version > SCHEMA_VERSION:
            raise DatabaseError(
                "قاعدة البيانات أُنشئت بإصدار أحدث من التطبيق. حدّث التطبيق للمتابعة."
            )
        # لا توجد ترقيات بعد الإصدار الأول.
        if version < SCHEMA_VERSION:
            self.set_meta("schema_version", str(SCHEMA_VERSION))

    # ------------------------------------------------------------------
    # Transactions and execution
    # ------------------------------------------------------------------
    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        """معاملة آمنة: commit عند النجاح وrollback عند الفشل."""
        conn = self.connect() if self._conn is None else self._conn
        try:
            yield conn
        except sqlite3.Error as exc:
            conn.rollback()
            raise DatabaseError(_friendly_sqlite_error(exc)) from exc
        except Exception:
            conn.rollback()
            raise
        else:
            conn.commit()

    def execute(self, sql: str, params: Sequence[Any] = ()) -> sqlite3.Cursor:
        """نفّذ جملة SQL ضمن معاملة."""
        with self.transaction() as conn:
            return conn.execute(sql, tuple(params))

    def executemany(self, sql: str, seq: Sequence[Sequence[Any]]) -> None:
        with self.transaction() as conn:
            conn.executemany(sql, seq)

    def query(self, sql: str, params: Sequence[Any] = ()) -> list[sqlite3.Row]:
        """نفّذ استعلام قراءة وأعد الصفوف."""
        try:
            cursor = self.connection.execute(sql, tuple(params))
            return list(cursor.fetchall())
        except sqlite3.Error as exc:
            raise DatabaseError(_friendly_sqlite_error(exc)) from exc

    def query_one(self, sql: str, params: Sequence[Any] = ()) -> sqlite3.Row | None:
        rows = self.query(sql, params)
        return rows[0] if rows else None

    # ------------------------------------------------------------------
    # meta / app_state helpers
    # ------------------------------------------------------------------
    def get_meta(self, key: str, default: str | None = None) -> str | None:
        row = self.query_one("SELECT value FROM meta WHERE key = ?", (key,))
        return row["value"] if row else default

    def set_meta(self, key: str, value: str) -> None:
        self.execute(
            "INSERT INTO meta(key, value) VALUES(?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (key, value),
        )

    def get_state(self, key: str, default: str | None = None) -> str | None:
        row = self.query_one("SELECT value FROM app_state WHERE key = ?", (key,))
        return row["value"] if row else default

    def set_state(self, key: str, value: str) -> None:
        self.execute(
            "INSERT INTO app_state(key, value, updated_at) VALUES(?, ?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = excluded.updated_at",
            (key, value, utc_now()),
        )

    # ------------------------------------------------------------------
    # Maintenance
    # ------------------------------------------------------------------
    def checkpoint(self) -> None:
        """دمج سجل WAL في ملف القاعدة الرئيسي (يُستدعى عند الإغلاق)."""
        if self._conn is None:
            return
        try:
            self._conn.commit()
            self._conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        except sqlite3.Error:  # pragma: no cover - best effort on shutdown
            pass

    def backup_to(self, destination: str | os.PathLike[str]) -> Path:
        """نسخة احتياطية كاملة من القاعدة."""
        target = Path(destination)
        target.parent.mkdir(parents=True, exist_ok=True)
        try:
            with sqlite3.connect(str(target)) as backup_conn:
                self.connection.backup(backup_conn)
        except sqlite3.Error as exc:
            raise DatabaseError(f"تعذّر إنشاء نسخة احتياطية: {exc}") from exc
        return target

    def close(self) -> None:
        if self._conn is None:
            return
        self.checkpoint()
        try:
            self._conn.close()
        finally:
            self._conn = None

    # ------------------------------------------------------------------
    def __enter__(self) -> "Database":
        self.connect()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()


def _friendly_sqlite_error(exc: sqlite3.Error) -> str:
    text = str(exc)
    if "readonly" in text.lower():
        return "تعذّر الحفظ: قاعدة البيانات للقراءة فقط. تحقّق من صلاحيات المجلّد."
    if "locked" in text.lower() or "busy" in text.lower():
        return "قاعدة البيانات مشغولة حاليًا. انتظر لحظة ثم أعد المحاولة."
    if "malformed" in text.lower() or "not a database" in text.lower():
        return "ملف قاعدة البيانات تالف أو غير صالح."
    if "disk" in text.lower() and "full" in text.lower():
        return "المساحة التخزينية ممتلئة، تعذّر حفظ التقدّم."
    return f"حدث خطأ في قاعدة البيانات: {text}"
