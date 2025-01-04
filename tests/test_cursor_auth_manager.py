import unittest
import os
import sqlite3
from unittest.mock import patch, MagicMock
from cursor_auth_manager import CursorAuthManager


class TestCursorAuthManager(unittest.TestCase):
    def setUp(self):
        # 创建临时测试数据库
        self.test_db_path = "test_state.vscdb"

        # 创建测试数据库和表
        self.conn = sqlite3.connect(self.test_db_path)
        self.cursor = self.conn.cursor()
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS itemTable (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """
        )
        self.conn.commit()

        # 模拟 CursorAuthManager 的数据库路径
        with patch.object(CursorAuthManager, "__init__", return_value=None):
            self.auth_manager = CursorAuthManager()
            self.auth_manager.db_path = self.test_db_path

    def tearDown(self):
        # 清理测试数据库
        self.conn.close()
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)

    def test_update_auth_new_values(self):
        """测试更新新的认证信息"""
        result = self.auth_manager.update_auth(
            email="test@example.com",
            access_token="test_access_token",
            refresh_token="test_refresh_token",
        )

        self.assertTrue(result)

        # 验证数据是否正确写入
        cursor = self.conn.cursor()

        # 检查邮箱
        cursor.execute(
            "SELECT value FROM itemTable WHERE key=?", ("cursorAuth/cachedEmail",)
        )
        self.assertEqual(cursor.fetchone()[0], "test@example.com")

        # 检查访问令牌
        cursor.execute(
            "SELECT value FROM itemTable WHERE key=?", ("cursorAuth/accessToken",)
        )
        self.assertEqual(cursor.fetchone()[0], "test_access_token")

        # 检查刷新令牌
        cursor.execute(
            "SELECT value FROM itemTable WHERE key=?", ("cursorAuth/refreshToken",)
        )
        self.assertEqual(cursor.fetchone()[0], "test_refresh_token")

        # 检查注册类型
        cursor.execute(
            "SELECT value FROM itemTable WHERE key=?", ("cursorAuth/cachedSignUpType",)
        )
        self.assertEqual(cursor.fetchone()[0], "Auth_0")

    def test_update_auth_partial_update(self):
        """测试只更新部分认证信息"""
        result = self.auth_manager.update_auth(email="test@example.com")

        self.assertTrue(result)

        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT value FROM itemTable WHERE key=?", ("cursorAuth/cachedEmail",)
        )
        self.assertEqual(cursor.fetchone()[0], "test@example.com")

    def test_update_auth_no_values(self):
        """测试不提供任何更新值的情况"""
        result = self.auth_manager.update_auth()
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
