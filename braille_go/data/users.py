"""إدارة المستخدمين (طلاب ومدرب) لسهولة الاستخدام في الفصول والمراكز التدريبية."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from typing import List, Optional

from .db import Database


@dataclass
class User:
    id: int
    name: str
    role: str  # 'student' or 'teacher'
    created_at: str = ""


class UserManager:
    def __init__(self, db: Database) -> None:
        self._db = db

    def ensure_schema(self) -> None:
        # تم إنشاؤه في db.initialize لكن نضمن
        pass

    def add_user(self, name: str, role: str = "student") -> User:
        name = name.strip()
        if not name:
            raise ValueError("اسم المستخدم مطلوب")
        with self._db.transaction() as conn:
            cur = conn.execute(
                "INSERT INTO users(name, role, created_at) VALUES(?,?,datetime('now'))",
                (name, role),
            )
            uid = cur.lastrowid
        return self.get_user(uid) or User(id=uid, name=name, role=role)

    def list_users(self) -> List[User]:
        rows = self._db.query("SELECT id, name, role, created_at FROM users ORDER BY id ASC")
        return [User(id=r["id"], name=r["name"], role=r["role"], created_at=r["created_at"] or "") for r in rows]

    def get_user(self, user_id: int) -> Optional[User]:
        row = self._db.query_one("SELECT id, name, role, created_at FROM users WHERE id=?", (user_id,))
        if not row:
            return None
        return User(id=row["id"], name=row["name"], role=row["role"], created_at=row["created_at"] or "")

    def get_active_user(self) -> Optional[User]:
        row = self._db.query_one("SELECT u.id, u.name, u.role FROM app_state s JOIN users u ON u.id = CAST(s.value AS INTEGER) WHERE s.key='active_user_id'")
        if not row:
            return None
        return User(id=row["id"], name=row["name"], role=row["role"])

    def set_active_user(self, user_id: int) -> None:
        self._db.set_state("active_user_id", str(user_id))

    def delete_user(self, user_id: int) -> None:
        with self._db.transaction() as conn:
            conn.execute("DELETE FROM users WHERE id=?", (user_id,))
            conn.execute("UPDATE app_state SET value='1' WHERE key='active_user_id' AND value=?", (str(user_id),))
