import pytest
from unittest.mock import Mock, MagicMock

from sqlalchemy import BinaryExpression
from sqlalchemy.orm import Session

from app.models.task import Task
from app.models.user import User
from app.db.crud.task import (
    create_task,
    get_task,
    get_task_by_user,
    update_task,
    delete_task
)


class TestCreateTask:
    """Тесты для функции create_task"""

    def test_create_task_success(self):
        """Тест успешного создания задачи"""
        # Arrange
        db_mock = Mock(spec=Session)
        task = Task(id=1, title="Test Task", description='Test description', difficulty=1, creator_id=1)

        # Act
        result = create_task(db_mock, task)

        # Assert
        db_mock.add.assert_called_once_with(task)
        db_mock.commit.assert_called_once()
        db_mock.refresh.assert_called_once_with(task)
        assert result == task

    def test_create_task_with_commit_error(self):
        """Тест обработки ошибки при commit"""
        # Arrange
        db_mock = Mock(spec=Session)
        task = Task(id=1, title="Test Task", description='Test description', difficulty=1, creator_id=1)
        db_mock.commit.side_effect = Exception("Database error")

        # Act & Assert
        with pytest.raises(Exception, match="Database error"):
            create_task(db_mock, task)

        db_mock.add.assert_called_once_with(task)
        db_mock.commit.assert_called_once()
        db_mock.refresh.assert_not_called()


class TestGetTask:
    """Тесты для функции get_task"""

    def test_get_task_found(self):
        """Тест получения существующей задачи"""
        # Arrange
        db_mock = Mock(spec=Session)
        task_id = 1
        expected_task = Task(id=task_id, title="Test Task", creator_id=1)

        query_mock = MagicMock()
        filter_mock = MagicMock()
        query_mock.filter.return_value = filter_mock
        filter_mock.first.return_value = expected_task
        db_mock.query.return_value = query_mock

        # Act
        result = get_task(db_mock, task_id)

        # Assert
        db_mock.query.assert_called_once_with(Task)
        query_mock.filter.assert_called_once()
        filter_args, _ = query_mock.filter.call_args
        assert isinstance(filter_args[0], BinaryExpression)
        assert str(filter_args[0]) == str(Task.id == task_id)
        filter_mock.first.assert_called_once()
        assert result == expected_task

    def test_get_task_not_found(self):
        """Тест получения несуществующей задачи"""
        # Arrange
        db_mock = Mock(spec=Session)
        task_id = 999

        query_mock = MagicMock()
        filter_mock = MagicMock()
        query_mock.filter.return_value = filter_mock
        filter_mock.first.return_value = None
        db_mock.query.return_value = query_mock

        # Act
        result = get_task(db_mock, task_id)

        # Assert
        db_mock.query.assert_called_once_with(Task)
        query_mock.filter.assert_called_once()
        filter_args, _ = query_mock.filter.call_args
        assert isinstance(filter_args[0], BinaryExpression)
        assert str(filter_args[0]) == str(Task.id == task_id)
        filter_mock.first.assert_called_once()
        assert result is None


class TestGetTaskByUser:
    """Тесты для функции get_task_by_user"""

    def test_get_task_by_user_with_tasks(self):
        """Тест получения задач пользователя (есть задачи)"""
        # Arrange
        db_mock = Mock(spec=Session)
        user_id = 1
        expected_tasks = [
            Task(id=1, title="Task 1", creator_id=user_id),
            Task(id=2, title="Task 2", creator_id=user_id)
        ]

        query_mock = MagicMock()
        filter_mock = MagicMock()
        query_mock.filter.return_value = filter_mock
        filter_mock.all.return_value = expected_tasks
        db_mock.query.return_value = query_mock

        # Act
        result = get_task_by_user(db_mock, user_id)

        # Assert
        db_mock.query.assert_called_once_with(Task)
        query_mock.filter.assert_called_once()
        filter_args, _ = query_mock.filter.call_args
        assert isinstance(filter_args[0], BinaryExpression)
        assert str(filter_args[0]) == str(Task.creator_id == user_id)
        filter_mock.all.assert_called_once()
        assert result == expected_tasks
        assert len(result) == 2

    def test_get_task_by_user_empty_list(self):
        """Тест получения задач пользователя (нет задач)"""
        # Arrange
        db_mock = Mock(spec=Session)
        user_id = 1

        query_mock = MagicMock()
        filter_mock = MagicMock()
        query_mock.filter.return_value = filter_mock
        filter_mock.all.return_value = []
        db_mock.query.return_value = query_mock

        # Act
        result = get_task_by_user(db_mock, user_id)

        # Assert
        db_mock.query.assert_called_once_with(Task)
        filter_args, _ = query_mock.filter.call_args
        assert isinstance(filter_args[0], BinaryExpression)
        assert str(filter_args[0]) == str(Task.creator_id == user_id)
        filter_mock.all.assert_called_once()
        assert len(result) == 0


class TestUpdateTask:
    """Тесты для функции update_task"""

    def test_update_task_success(self):
        """Тест успешного обновления задачи"""
        # Arrange
        db_mock = Mock(spec=Session)
        task = Task(id=1, title="Old Title", creator_id=1)
        update_data = {"title": "New Title", "description": "New Description"}

        # Act
        result = update_task(db_mock, task, update_data)

        # Assert
        assert task.title == "New Title"
        assert task.description == "New Description"
        db_mock.commit.assert_called_once()
        db_mock.refresh.assert_called_once_with(task)
        assert result == task

    def test_update_task_empty_data(self):
        """Тест обновления задачи с пустыми данными"""
        # Arrange
        db_mock = Mock(spec=Session)
        task = Task(id=1, title="Original Title", creator_id=1)
        original_title = task.title
        update_data = {}

        # Act
        result = update_task(db_mock, task, update_data)

        # Assert
        assert task.title == original_title  # Не должно измениться
        db_mock.commit.assert_called_once()
        db_mock.refresh.assert_called_once_with(task)
        assert result == task

    def test_update_task_partial_data(self):
        """Тест частичного обновления задачи"""
        # Arrange
        db_mock = Mock(spec=Session)
        task = Task(id=1, title="Old Title", description="Old Description", creator_id=1)
        update_data = {"title": "New Title"}  # Обновляем только title

        # Act
        result = update_task(db_mock, task, update_data)

        # Assert
        assert task.title == "New Title"
        assert task.description == "Old Description"  # Не должно измениться
        db_mock.commit.assert_called_once()
        db_mock.refresh.assert_called_once_with(task)
        assert result == task

    def test_update_task_with_commit_error(self):
        """Тест обработки ошибки при commit во время обновления"""
        # Arrange
        db_mock = Mock(spec=Session)
        task = Task(id=1, title="Old Title", creator_id=1)
        update_data = {"title": "New Title"}
        db_mock.commit.side_effect = Exception("Database error")

        # Act & Assert
        with pytest.raises(Exception, match="Database error"):
            update_task(db_mock, task, update_data)

        assert task.title == "New Title"  # Изменения в объекте остались
        db_mock.commit.assert_called_once()
        db_mock.refresh.assert_not_called()


class TestDeleteTask:
    """Тесты для функции delete_task"""

    def test_delete_task_success(self):
        """Тест успешного удаления задачи"""
        # Arrange
        db_mock = Mock(spec=Session)
        task = Task(id=1, title="Task to Delete", creator_id=1)

        # Act
        result = delete_task(db_mock, task)

        # Assert
        db_mock.delete.assert_called_once_with(task)
        db_mock.commit.assert_called_once()
        assert result is None

    def test_delete_task_with_commit_error(self):
        """Тест обработки ошибки при commit во время удаления"""
        # Arrange
        db_mock = Mock(spec=Session)
        task = Task(id=1, title="Task to Delete", creator_id=1)
        db_mock.commit.side_effect = Exception("Database error")

        # Act & Assert
        with pytest.raises(Exception, match="Database error"):
            delete_task(db_mock, task)

        db_mock.delete.assert_called_once_with(task)
        db_mock.commit.assert_called_once()


# Параметризованные тесты
class TestTaskCRUDParametrized:
    """Параметризованные тесты для проверки различных сценариев"""

    @pytest.mark.parametrize("task_id,expected_calls", [
        (1, 1),
        (999, 1),
        (0, 1),
        (-1, 1),
    ])
    def test_get_task_with_different_ids(self, task_id, expected_calls):
        """Тест получения задач с различными ID"""
        # Arrange
        db_mock = Mock(spec=Session)
        query_mock = MagicMock()
        filter_mock = MagicMock()
        query_mock.filter.return_value = filter_mock
        filter_mock.first.return_value = None
        db_mock.query.return_value = query_mock

        # Act
        get_task(db_mock, task_id)

        # Assert
        assert db_mock.query.call_count == expected_calls

    @pytest.mark.parametrize("update_data,expected_changes", [
        ({"title": "New Title"}, {"title": "New Title"}),
        ({"description": "New Desc"}, {"description": "New Desc"}),
        ({"title": "New Title", "status": "done"}, {"title": "New Title", "status": "done"}),
        ({}, {}),
    ])
    def test_update_task_with_different_data(self, update_data, expected_changes):
        """Тест обновления задач с различными данными"""
        # Arrange
        db_mock = Mock(spec=Session)
        task = Task(id=1, title="Old Title", description="Old Desc", creator_id=1)
        original_values = {
            "title": task.title,
            "description": task.description,
            "creator_id": task.creator_id
        }

        # Act
        update_task(db_mock, task, update_data)

        # Assert
        for key, expected_value in expected_changes.items():
            assert getattr(task, key) == expected_value

        # Проверяем, что неизмененные поля остались прежними
        for key, original_value in original_values.items():
            if key not in expected_changes:
                assert getattr(task, key) == original_value