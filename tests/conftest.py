"""
pytest 配置文件
提供全局的 fixtures 和配置
"""

import pytest
import os
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock


# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture(scope="session")
def workspace_path():
    """项目工作目录"""
    return project_root


@pytest.fixture(scope="session", autouse=True)
def setup_environment():
    """设置测试环境变量"""
    os.environ['COZE_WORKSPACE_PATH'] = str(project_root)
    os.environ['COZE_WORKLOAD_IDENTITY_API_KEY'] = 'test_api_key_12345'
    os.environ['COZE_INTEGRATION_MODEL_BASE_URL'] = 'https://test-api.example.com'
    os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
    os.environ['STORAGE_BUCKET'] = 'test-bucket'
    
    yield
    
    # 清理
    for key in ['COZE_WORKSPACE_PATH', 'COZE_WORKLOAD_IDENTITY_API_KEY', 
                'COZE_INTEGRATION_MODEL_BASE_URL', 'DATABASE_URL', 'STORAGE_BUCKET']:
        os.environ.pop(key, None)


@pytest.fixture
def mock_db_session():
    """Mock 数据库会话"""
    session = Mock()
    session.__enter__ = Mock(return_value=session)
    session.__exit__ = Mock(return_value=False)
    session.query = Mock()
    session.add = Mock()
    session.commit = Mock()
    session.rollback = Mock()
    session.close = Mock()
    return session


@pytest.fixture
def mock_runtime():
    """Mock 工具运行时上下文"""
    runtime = Mock()
    runtime.context = {
        'configurable': {
            'user_id': 1,
            'user_role': 'parent'
        }
    }
    return runtime


@pytest.fixture
def mock_student():
    """Mock 学生对象"""
    student = Mock()
    student.id = 1
    student.name = "测试学生"
    student.nickname = "小魔法师"
    student.grade = "3年级"
    student.class_name = "1班"
    student.school = "魔法小学"
    student.parent_contact = "13800138000"
    student.magic_level = 1
    student.total_points = 100
    student.user_id = 1
    return student


@pytest.fixture
def mock_homework():
    """Mock 作业对象"""
    homework = Mock()
    homework.id = 1
    homework.title = "数学作业"
    homework.subject = "数学"
    homework.description = "完成练习册第10页"
    homework.due_date = "2024-12-31"
    homework.priority = "high"
    homework.status = "pending"
    homework.student_id = 1
    return homework


@pytest.fixture
def mock_course():
    """Mock 课程对象"""
    course = Mock()
    course.id = 1
    course.title = "魔法数学课"
    course.subject = "数学"
    course.teacher = "邓布利多老师"
    course.class_name = "3年级1班"
    course.weekday = 1
    course.start_time = "09:00"
    course.end_time = "10:30"
    course.room = "魔药教室"
    return course


def pytest_configure(config):
    """pytest 配置钩子"""
    config.addinivalue_line(
        "markers", "unit: 单元测试标记"
    )
    config.addinivalue_line(
        "markers", "integration: 集成测试标记"
    )
    config.addinivalue_line(
        "markers", "slow: 慢速测试标记"
    )
    config.addinivalue_line(
        "markers", "smoke: 冒烟测试标记"
    )


@pytest.fixture
def temp_file(tmp_path):
    """创建临时文件"""
    def _create_temp_file(content: str = "测试内容", filename: str = "test.txt"):
        file_path = tmp_path / filename
        file_path.write_text(content, encoding='utf-8')
        return file_path
    return _create_temp_file


@pytest.fixture
def mock_llm():
    """Mock LLM"""
    llm = Mock()
    llm.invoke = Mock(return_value=Mock(content="测试响应"))
    return llm
