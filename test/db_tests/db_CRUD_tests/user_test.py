import pytest
from unittest.mock import Mock, MagicMock

from sqlalchemy import BinaryExpression
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.task import Task
from app.db.CRUD.user import (
    create_user,
    get_user_by_email,
    get_user_by_username,
    update_user,
    delete_user
)


class TestCreateUser:
    """Тесты для функции create_user"""

    def test_create_user_success(self):
        """Тест успешного создания пользователя"""
        # Arrange
        db_mock = Mock(spec=Session)
        user = User(id=1, username="test_user", email="test@example.com")

        # Act
        result = create_user(db_mock, user)

        # Assert
        db_mock.add.assert_called_once_with(user)
        db_mock.commit.assert_called_once()
        db_mock.refresh.assert_called_once_with(user)
        assert result == user

    def test_create_user_with_commit_error(self):
        """Тест обработки ошибки при commit"""
        # Arrange
        db_mock = Mock(spec=Session)
        user = User(id=1, username="test_user", email="test@example.com")
        db_mock.commit.side_effect = Exception("Database error")

        # Act & Assert
        with pytest.raises(Exception, match="Database error"):
            create_user(db_mock, user)

        db_mock.add.assert_called_once_with(user)
        db_mock.commit.assert_called_once()
        db_mock.refresh.assert_not_called()

    def test_create_user_with_refresh_error(self):
        """Тест обработки ошибки при refresh"""
        # Arrange
        db_mock = Mock(spec=Session)
        user = User(id=1, username="test_user", email="test@example.com")
        db_mock.refresh.side_effect = Exception("Refresh error")

        # Act & Assert
        with pytest.raises(Exception, match="Refresh error"):
            create_user(db_mock, user)

        db_mock.add.assert_called_once_with(user)
        db_mock.commit.assert_called_once()
        db_mock.refresh.assert_called_once_with(user)


class TestGetUserByEmail:
    """Тесты для функции get_user_by_email"""

    def test_get_user_by_email_found(self):
        """Тест получения пользователя по существующему email"""
        # Arrange
        db_mock = Mock(spec=Session)
        email = "test@example.com"
        expected_user = User(id=1, username="test_user", email=email)

        query_mock = MagicMock()
        filter_mock = MagicMock()
        query_mock.filter.return_value = filter_mock
        filter_mock.first.return_value = expected_user
        db_mock.query.return_value = query_mock

        # Act
        result = get_user_by_email(db_mock, email)

        # Assert
        db_mock.query.assert_called_once_with(User)
        query_mock.filter.assert_called_once()
        filter_args, _ = query_mock.filter.call_args
        assert isinstance(filter_args[0], BinaryExpression)
        assert str(filter_args[0]) == str(User.email == email)
        filter_mock.first.assert_called_once()
        assert result == expected_user

    def test_get_user_by_email_not_found(self):
        """Тест получения пользователя по несуществующему email"""
        # Arrange
        db_mock = Mock(spec=Session)
        email = "nonexistent@example.com"

        query_mock = MagicMock()
        filter_mock = MagicMock()
        query_mock.filter.return_value = filter_mock
        filter_mock.first.return_value = None
        db_mock.query.return_value = query_mock

        # Act
        result = get_user_by_email(db_mock, email)

        # Assert
        db_mock.query.assert_called_once_with(User)
        query_mock.filter.assert_called_once()
        filter_args, _ = query_mock.filter.call_args
        assert isinstance(filter_args[0], BinaryExpression)
        assert str(filter_args[0]) == str(User.email == email)
        filter_mock.first.assert_called_once()
        assert result is None

    def test_get_user_by_email_with_database_error(self):
        """Тест обработки ошибки базы данных при поиске по email"""
        # Arrange
        db_mock = Mock(spec=Session)
        email = "test@example.com"
        db_mock.query.side_effect = Exception("Database connection error")

        # Act & Assert
        with pytest.raises(Exception, match="Database connection error"):
            get_user_by_email(db_mock, email)

        db_mock.query.assert_called_once_with(User)

    @pytest.mark.parametrize("email", [
        "test@example.com",
        "user123@domain.org",
        "admin@company.co.uk",
        "user+tag@example.com",
        "",  # Пустая строка
        "   ",  # Пробелы
    ])
    def test_get_user_by_email_different_inputs(self, email):
        """Тест получения пользователя с различными email"""
        # Arrange
        db_mock = Mock(spec=Session)
        query_mock = MagicMock()
        filter_mock = MagicMock()
        query_mock.filter.return_value = filter_mock
        filter_mock.first.return_value = None
        db_mock.query.return_value = query_mock

        # Act
        result = get_user_by_email(db_mock, email)

        # Assert
        db_mock.query.assert_called_once_with(User)
        db_mock.query.assert_called_once_with(User)
        query_mock.filter.assert_called_once()
        filter_args, _ = query_mock.filter.call_args
        assert isinstance(filter_args[0], BinaryExpression)
        assert str(filter_args[0]) == str(User.email == email)
        filter_mock.first.assert_called_once()
        assert result is None


class TestGetUserByUsername:
    """Тесты для функции get_user_by_username"""

    def test_get_user_by_username_found(self):
        """Тест получения пользователя по существующему username"""
        # Arrange
        db_mock = Mock(spec=Session)
        username = "test_user"
        expected_user = User(id=1, username=username, email="test@example.com")

        query_mock = MagicMock()
        filter_mock = MagicMock()
        query_mock.filter.return_value = filter_mock
        filter_mock.first.return_value = expected_user
        db_mock.query.return_value = query_mock

        # Act
        result = get_user_by_username(db_mock, username)

        # Assert
        db_mock.query.assert_called_once_with(User)
        query_mock.filter.assert_called_once()
        filter_args, _ = query_mock.filter.call_args
        assert isinstance(filter_args[0], BinaryExpression)
        assert str(filter_args[0]) == str(User.username == username)
        filter_mock.first.assert_called_once()
        assert result == expected_user

    def test_get_user_by_username_not_found(self):
        """Тест получения пользователя по несуществующему username"""
        # Arrange
        db_mock = Mock(spec=Session)
        username = "non_existent_user"

        query_mock = MagicMock()
        filter_mock = MagicMock()
        query_mock.filter.return_value = filter_mock
        filter_mock.first.return_value = None
        db_mock.query.return_value = query_mock

        # Act
        result = get_user_by_username(db_mock, username)

        # Assert
        db_mock.query.assert_called_once_with(User)
        query_mock.filter.assert_called_once()
        filter_args, _ = query_mock.filter.call_args
        assert isinstance(filter_args[0], BinaryExpression)
        assert str(filter_args[0]) == str(User.username == username)
        filter_mock.first.assert_called_once()
        assert result is None

    def test_get_user_by_username_with_database_error(self):
        """Тест обработки ошибки базы данных при поиске по username"""
        # Arrange
        db_mock = Mock(spec=Session)
        username = "test_user"
        db_mock.query.side_effect = Exception("Database connection error")

        # Act & Assert
        with pytest.raises(Exception, match="Database connection error"):
            get_user_by_username(db_mock, username)

        db_mock.query.assert_called_once_with(User)

    @pytest.mark.parametrize("username", [
        "test_user",
        "admin",
        "user_123",
        "UPPERCASE",
        "special-chars",
        "user@domain",
        "",  # Пустая строка
        "   ",  # Пробелы
    ])
    def test_get_user_by_username_different_inputs(self, username):
        """Тест получения пользователя с различными username"""
        # Arrange
        db_mock = Mock(spec=Session)
        query_mock = MagicMock()
        filter_mock = MagicMock()
        query_mock.filter.return_value = filter_mock
        filter_mock.first.return_value = None
        db_mock.query.return_value = query_mock

        # Act
        result = get_user_by_username(db_mock, username)

        # Assert
        db_mock.query.assert_called_once_with(User)
        query_mock.filter.assert_called_once()
        filter_args, _ = query_mock.filter.call_args
        assert isinstance(filter_args[0], BinaryExpression)
        assert str(filter_args[0]) == str(User.username == username)
        filter_mock.first.assert_called_once()
        assert result is None


class TestUpdateUser:
    """Тесты для функции update_user"""

    def test_update_user_success(self):
        """Тест успешного обновления пользователя"""
        # Arrange
        db_mock = Mock(spec=Session)
        user = User(id=1, username="old_user", email="old@example.com")
        update_data = {"username": "new_user", "email": "new@example.com"}

        # Act
        result = update_user(db_mock, user, update_data)

        # Assert
        assert user.username == "new_user"
        assert user.email == "new@example.com"
        db_mock.commit.assert_called_once()
        db_mock.refresh.assert_called_once_with(user)
        assert result == user

    def test_update_user_partial_data(self):
        """Тест частичного обновления пользователя"""
        # Arrange
        db_mock = Mock(spec=Session)
        user = User(id=1, username="test_user", email="test@example.com")
        update_data = {"first_name": "Jane"}  # Обновляем только имя

        # Act
        result = update_user(db_mock, user, update_data)

        # Assert
        assert user.username == "test_user"  # Не должно измениться
        assert user.email == "test@example.com"  # Не должно измениться
        db_mock.commit.assert_called_once()
        db_mock.refresh.assert_called_once_with(user)
        assert result == user

    def test_update_user_empty_data(self):
        """Тест обновления пользователя с пустыми данными"""
        # Arrange
        db_mock = Mock(spec=Session)
        user = User(id=1, username="test_user", email="test@example.com")
        original_username = user.username
        original_email = user.email
        update_data = {}

        # Act
        result = update_user(db_mock, user, update_data)

        # Assert
        assert user.username == original_username
        assert user.email == original_email
        db_mock.commit.assert_called_once()
        db_mock.refresh.assert_called_once_with(user)
        assert result == user

    def test_update_user_with_commit_error(self):
        """Тест обработки ошибки базы данных при commit"""
        # Arrange
        db_mock = Mock(spec=Session)
        user = User(id=1, username="test_user", email="test@example.com")
        update_data = {"username": "new_user"}
        db_mock.commit.side_effect = Exception("Database error")

        # Act & Assert
        with pytest.raises(Exception, match="Database error"):
            update_user(db_mock, user, update_data)

        assert user.username == "new_user"  # Изменения в объекте остались
        db_mock.commit.assert_called_once()
        db_mock.refresh.assert_not_called()

    def test_update_user_with_refresh_error(self):
        """Тест обработки ошибки при refresh"""
        # Arrange
        db_mock = Mock(spec=Session)
        user = User(id=1, username="test_user", email="test@example.com")
        update_data = {"username": "new_user"}
        db_mock.refresh.side_effect = Exception("Refresh error")

        # Act & Assert
        with pytest.raises(Exception, match="Refresh error"):
            update_user(db_mock, user, update_data)

        assert user.username == "new_user"
        db_mock.commit.assert_called_once()
        db_mock.refresh.assert_called_once_with(user)

    @pytest.mark.parametrize("update_data,expected_changes", [
        ({"username": "new_user"}, {"username": "new_user"}),
        ({"email": "new@test.com"}, {"email": "new@test.com"}),
        ({"username": "user", "email": "user@test.com"}, {"username": "user", "email": "user@test.com"}),
        ({"is_active": False}, {"is_active": False}),
    ])
    def test_update_user_parametrized(self, update_data, expected_changes):
        """Параметризованный тест обновления пользователя с различными данными"""
        # Arrange
        db_mock = Mock(spec=Session)
        user = User(
            id=1,
            username="old",
            email="old@test.com",
            is_active=True,
        )

        # Act
        result = update_user(db_mock, user, update_data)

        # Assert
        for key, expected_value in expected_changes.items():
            assert getattr(user, key) == expected_value
        assert result == user


class TestDeleteUser:
    """Тесты для функции delete_user"""

    def test_delete_user_success(self):
        """Тест успешного удаления пользователя"""
        # Arrange
        db_mock = Mock(spec=Session)
        user = User(id=1, username="testuser", email="test@example.com")

        # Act
        result = delete_user(db_mock, user)

        # Assert
        db_mock.delete.assert_called_once_with(user)
        db_mock.commit.assert_called_once()
        assert result is None

    def test_delete_user_with_commit_error(self):
        """Тест обработки ошибки базы данных при удалении"""
        # Arrange
        db_mock = Mock(spec=Session)
        user = User(id=1, username="testuser", email="test@example.com")
        db_mock.commit.side_effect = Exception("Database error")

        # Act & Assert
        with pytest.raises(Exception, match="Database error"):
            delete_user(db_mock, user)

        db_mock.delete.assert_called_once_with(user)
        db_mock.commit.assert_called_once()

    def test_delete_user_with_delete_error(self):
        """Тест обработки ошибки при delete"""
        # Arrange
        db_mock = Mock(spec=Session)
        user = User(id=1, username="testuser", email="test@example.com")
        db_mock.delete.side_effect = Exception("Delete error")

        # Act & Assert
        with pytest.raises(Exception, match="Delete error"):
            delete_user(db_mock, user)

        db_mock.delete.assert_called_once_with(user)
        db_mock.commit.assert_not_called()


class TestUserCRUDEdgeCases:
    """Тесты граничных случаев и особых сценариев"""

    def test_create_user_with_special_characters(self):
        """Тест создания пользователя со специальными символами"""
        # Arrange
        db_mock = Mock(spec=Session)
        user = User(
            id=1,
            username="user@#$%^&*()",
            email="test+tag@example.com",
        )

        # Act
        result = create_user(db_mock, user)

        # Assert
        db_mock.add.assert_called_once_with(user)
        db_mock.commit.assert_called_once()
        db_mock.refresh.assert_called_once_with(user)
        assert result == user

    def test_update_user_with_unicode_characters(self):
        """Тест обновления пользователя с Unicode символами"""
        # Arrange
        db_mock = Mock(spec=Session)
        user = User(id=1, username="testuser", email="test@example.com")
        update_data = {
            "first_name": "Ñoël",
            "last_name": "李小明",
            "bio": "Hello 👋 World 🌍"
        }

        # Act
        result = update_user(db_mock, user, update_data)

        # Assert
        assert user.first_name == "Ñoël"
        assert user.last_name == "李小明"
        assert user.bio == "Hello 👋 World 🌍"
        assert result == user

    def test_operations_with_large_data(self):
        """Тест операций с большими объемами данных"""
        # Arrange
        db_mock = Mock(spec=Session)
        large_text = "x" * 10000  # 10KB текста
        user = User(id=1, username="test_user", email="test@example.com")
        update_data = {"username": large_text}

        # Act
        result = update_user(db_mock, user, update_data)

        # Assert
        assert user.username == large_text
        assert len(user.username) == 10000
        assert result == user


class TestUserCRUDTyping:
    """Тесты для проверки типизации функций"""

    def test_return_types(self):
        """Тест проверки возвращаемых типов"""
        # Arrange
        db_mock = Mock(spec=Session)
        user = User(id=1, username="test_user", email="test@example.com")

        # Настройка моков для get функций
        query_mock = MagicMock()
        filter_mock = MagicMock()
        query_mock.filter.return_value = filter_mock
        filter_mock.first.return_value = user
        db_mock.query.return_value = query_mock

        # Act & Assert - create_user возвращает User
        result_create = create_user(db_mock, user)
        assert isinstance(result_create, User)

        # Act & Assert - get_user_by_email возвращает User или None
        result_get_email = get_user_by_email(db_mock, "test@example.com")
        assert isinstance(result_get_email, User) or result_get_email is None

        # Act & Assert - get_user_by_username возвращает User или None
        result_get_username = get_user_by_username(db_mock, "test_user")
        assert isinstance(result_get_username, User) or result_get_username is None

        # Act & Assert - update_user возвращает User
        result_update = update_user(db_mock, user, {"username": "new_user"})
        assert isinstance(result_update, User)

        # Act & Assert - delete_user возвращает None
        result_delete = delete_user(db_mock, user)
        assert result_delete is None


# Интеграционные тесты (заготовка)
class TestUserCRUDIntegration:
    """Интеграционные тесты для User CRUD"""

    @pytest.fixture
    def sample_user_data(self):
        """Фикстура с данными для тестового пользователя"""
        return {
            "username": "test_user",
            "email": "test@example.com",
            "is_active": True
        }