"""
测试基类和工具
为所有测试提供通用的 setup、teardown 和辅助函数
"""

import os
import sys
import pytest
from typing import Generator, Optional
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path


# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class ToolTestBase:
    """
    工具测试基类
    为所有工具测试提供通用的 setup 和 teardown
    """
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """每个测试方法执行前的 setup"""
        # 重置环境变量
        os.environ['COZE_WORKSPACE_PATH'] = str(project_root)
        os.environ['COZE_WORKLOAD_IDENTITY_API_KEY'] = 'test_api_key'
        os.environ['COZE_INTEGRATION_MODEL_BASE_URL'] = 'https://test.api.com'
        
        # Mock 数据库连接
        self.mock_db_session = Mock()
        self.mock_db_session.__enter__ = Mock(return_value=self.mock_db_session)
        self.mock_db_session.__exit__ = Mock(return_value=False)
        
        yield
        
        # Cleanup
        self.mock_db_session.reset_mock()
    
    def create_mock_runtime(self, user_id: Optional[int] = 1, user_role: Optional[str] = 'parent') -> Mock:
        """
        创建模拟的 ToolRuntime
        
        Args:
            user_id: 用户ID
            user_role: 用户角色
        
        Returns:
            Mock 的 ToolRuntime 实例
        """
        runtime = Mock()
        runtime.context = {
            'configurable': {
                'user_id': user_id,
                'user_role': user_role
            }
        }
        return runtime
    
    def create_mock_student(self, student_id: int = 1, name: str = "测试学生") -> Mock:
        """
        创建模拟的学生对象
        
        Args:
            student_id: 学生ID
            name: 学生姓名
        
        Returns:
            Mock 的 Student 实例
        """
        student = Mock()
        student.id = student_id
        student.name = name
        student.nickname = "小魔法师"
        student.grade = "3年级"
        student.class_name = "1班"
        student.school = "魔法小学"
        student.parent_contact = "13800138000"
        student.magic_level = 1
        student.total_points = 100
        student.user_id = 1
        return student
    
    def assert_success_response(self, response: str, expected_keywords: list):
        """
        断言响应是成功的
        
        Args:
            response: 响应字符串
            expected_keywords: 期望包含的关键词列表
        """
        assert isinstance(response, str)
        assert len(response) > 0
        for keyword in expected_keywords:
            assert keyword in response, f"响应中缺少关键词: {keyword}"
    
    def assert_error_response(self, response: str, error_keywords: list):
        """
        断言响应包含错误信息
        
        Args:
            response: 响应字符串
            error_keywords: 错误关键词列表
        """
        assert isinstance(response, str)
        for keyword in error_keywords:
            assert keyword in response or "失败" in response, f"响应中缺少错误关键词: {keyword}"


class DatabaseTestBase:
    """
    数据库测试基类
    为需要数据库连接的测试提供通用的 setup
    """
    
    @pytest.fixture(autouse=True)
    def setup_database(self):
        """设置数据库测试环境"""
        # 这里可以设置测试数据库
        # 例如：使用 SQLite 内存数据库
        pass
    
    def cleanup_database(self):
        """清理测试数据库"""
        pass


class AgentTestBase:
    """
    Agent 测试基类
    为 Agent 测试提供通用的 setup
    """
    
    @pytest.fixture(autouse=True)
    def setup_agent(self):
        """设置 Agent 测试环境"""
        # Mock LLM
        self.mock_llm = Mock()
        self.mock_llm.invoke = Mock(return_value=Mock(content="测试响应"))
        
        # Mock 工具
        self.mock_tool = Mock()
        self.mock_tool.name = "test_tool"
        self.mock_tool.func = Mock(return_value="工具执行结果")
        
        yield
        
        # Cleanup
        self.mock_llm.reset_mock()
        self.mock_tool.reset_mock()


def assert_valid_json_response(response: str):
    """
    断言响应是有效的 JSON
    
    Args:
        response: 响应字符串
    """
    import json
    try:
        json.loads(response)
    except json.JSONDecodeError as e:
        pytest.fail(f"响应不是有效的 JSON: {e}")


def assert_contains_all(response: str, keywords: list):
    """
    断言响应包含所有指定的关键词
    
    Args:
        response: 响应字符串
        keywords: 关键词列表
    """
    missing = [kw for kw in keywords if kw not in response]
    if missing:
        pytest.fail(f"响应中缺少关键词: {missing}")


def mock_file_operations(file_path: str, content: str = "测试内容"):
    """
    Mock 文件操作
    
    Args:
        file_path: 文件路径
        content: 文件内容
    """
    with patch('builtins.open', create=True) as mock_open:
        mock_file = MagicMock()
        mock_file.read.return_value = content
        mock_file.write.return_value = None
        mock_open.return_value.__enter__.return_value = mock_file
        return mock_open


class IntegrationTestBase:
    """
    集成测试基类
    为集成测试提供通用的 setup
    """
    
    @pytest.fixture(autouse=True)
    def setup_integration(self):
        """设置集成测试环境"""
        # 这里可以启动外部服务（如数据库、API等）
        pass
    
    def teardown_integration(self):
        """清理集成测试环境"""
        pass
