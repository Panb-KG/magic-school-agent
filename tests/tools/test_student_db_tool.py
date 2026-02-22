"""
学生管理工具测试
测试 create_student, get_student_info, add_student_points, upgrade_magic_level 等功能
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.tools.student_db_tool import (
    create_student,
    get_student_info,
    add_student_points,
    upgrade_magic_level
)
from tests.test_base import ToolTestBase


# Mock 权限检查函数，让所有测试都通过权限检查
@pytest.fixture(autouse=True)
def mock_permission_checks():
    """Mock 所有权限检查函数"""
    with patch('src.tools.tool_utils_fixed.check_student_access', return_value=True):
        with patch('auth.permissions_enhanced.check_student_access', return_value=True):
            yield


@pytest.mark.unit
@pytest.mark.tool
class TestCreateStudent(ToolTestBase):
    """测试创建学生功能"""
    
    def test_create_student_success(self, mock_runtime):
        """测试成功创建学生"""
        # Mock 数据库和 StudentManager
        mock_student = self.create_mock_student(student_id=1, name="张三")
        
        with patch('src.tools.student_db_tool.get_session', return_value=self.mock_db_session):
            with patch('src.tools.student_db_tool.StudentManager') as mock_mgr_class:
                mock_mgr = Mock()
                mock_mgr.create_student = Mock(return_value=mock_student)
                mock_mgr_class.return_value = mock_mgr
                
                # 执行测试 - 调用工具的 _run 方法
                result = create_student._run(
                    name="张三",
                    grade="3年级",
                    class_name="1班",
                    school="魔法小学",
                    parent_contact="13800138000",
                    nickname="小张",
                    runtime=mock_runtime,
                    config={}
                )
                
                # 验证结果
                self.assert_success_response(result, ["成功", "张三"])
    
    def test_create_student_empty_name(self, mock_runtime):
        """测试学生姓名为空的情况"""
        result = create_student._run(
            name="",
            grade="3年级",
            class_name="1班",
            school="魔法小学",
            parent_contact="13800138000",
            nickname="小张",
            runtime=mock_runtime,
                    config={}
        )
        
        # 验证错误响应
        self.assert_error_response(result, ["参数错误", "姓名"])
    
    def test_create_student_empty_grade(self, mock_runtime):
        """测试年级为空的情况"""
        result = create_student._run(
            name="张三",
            grade="",
            class_name="1班",
            school="魔法小学",
            parent_contact="13800138000",
            nickname="小张",
            runtime=mock_runtime,
                    config={}
        )
        
        # 验证错误响应
        self.assert_error_response(result, ["参数错误", "年级"])
    
    def test_create_student_database_error(self, mock_runtime):
        """测试数据库错误"""
        with patch('src.tools.student_db_tool.get_session', return_value=self.mock_db_session):
            with patch('src.tools.student_db_tool.StudentManager') as mock_mgr_class:
                mock_mgr = Mock()
                mock_mgr.create_student = Mock(side_effect=Exception("数据库连接失败"))
                mock_mgr_class.return_value = mock_mgr
                
                result = create_student._run(
                    name="张三",
                    grade="3年级",
                    class_name="1班",
                    school="魔法小学",
                    parent_contact="13800138000",
                    nickname="小张",
                    runtime=mock_runtime,
                    config={}
                )
                
                # 验证错误响应
                self.assert_error_response(result, ["失败"])


@pytest.mark.unit
@pytest.mark.tool
class TestGetStudentInfo(ToolTestBase):
    """测试获取学生信息功能"""
    
    def test_get_student_info_success(self, mock_runtime):
        """测试成功获取学生信息"""
        mock_student = self.create_mock_student(student_id=1, name="张三")
        
        with patch('src.tools.student_db_tool.get_session', return_value=self.mock_db_session):
            with patch('src.tools.student_db_tool.StudentManager') as mock_mgr_class:
                mock_mgr = Mock()
                mock_mgr.get_student_by_id = Mock(return_value=mock_student)
                mock_mgr_class.return_value = mock_mgr
                
                result = get_student_info._run(
                    student_id=1,
                    runtime=mock_runtime,
                    config={}
                )
                
                # 验证结果
                self.assert_success_response(result, ["张三", "3年级", "1班"])
    
    def test_get_student_info_not_found(self, mock_runtime):
        """测试学生不存在"""
        with patch('src.tools.student_db_tool.get_session', return_value=self.mock_db_session):
            with patch('src.tools.student_db_tool.StudentManager') as mock_mgr_class:
                mock_mgr = Mock()
                mock_mgr.get_student_by_id = Mock(return_value=None)
                mock_mgr_class.return_value = mock_mgr
                
                result = get_student_info._run(
                    student_id=999,
                    runtime=mock_runtime,
                    config={}
                )
                
                # 验证结果
                assert "未找到" in result or "不存在" in result
    
    def test_get_student_info_invalid_id(self, mock_runtime):
        """测试无效的学生ID"""
        result = get_student_info._run(
            student_id=-1,
            runtime=mock_runtime,
                    config={}
        )
        
        # 验证错误响应
        self.assert_error_response(result, ["参数错误", "ID"])
    
    def test_get_student_info_zero_id(self, mock_runtime):
        """测试学生ID为0的情况"""
        result = get_student_info._run(
            student_id=0,
            runtime=mock_runtime,
                    config={}
        )
        
        # 验证错误响应
        assert isinstance(result, str)
        assert ("错误" in result or "失败" in result)


@pytest.mark.unit
@pytest.mark.tool
class TestAddStudentPoints(ToolTestBase):
    """测试给学生增加积分功能"""
    
    def test_add_student_points_success(self, mock_runtime, mock_student):
        """测试成功增加积分"""
        # 模拟增加积分后的学生
        updated_student = Mock()
        updated_student.id = 1
        updated_student.name = "张三"
        updated_student.total_points = 150
        
        with patch('src.tools.student_db_tool.get_session', return_value=self.mock_db_session):
            with patch('src.tools.student_db_tool.StudentManager') as mock_mgr_class:
                mock_mgr = Mock()
                mock_mgr.get_student_by_id = Mock(return_value=mock_student)
                mock_mgr.add_points = Mock(return_value=updated_student)
                mock_mgr_class.return_value = mock_mgr
                
                result = add_student_points._run(
                    student_id=1,
                    points=50,
                    reason="完成作业",
                    runtime=mock_runtime,
                    config={}
                )
                
                # 验证结果
                self.assert_success_response(result, ["成功", "150", "完成作业"])
    
    def test_add_student_points_invalid_points(self, mock_runtime):
        """测试无效的积分数"""
        result = add_student_points._run(
            student_id=1,
            points="abc",  # 应该是整数
            reason="完成作业",
            runtime=mock_runtime,
                    config={}
        )
        
        # 验证错误响应
        self.assert_error_response(result, ["参数错误", "积分"])
    
    def test_add_student_points_empty_reason(self, mock_runtime):
        """测试原因为空的情况"""
        result = add_student_points._run(
            student_id=1,
            points=50,
            reason="",
            runtime=mock_runtime,
                    config={}
        )
        
        # 验证错误响应
        self.assert_error_response(result, ["参数错误", "原因"])
    
    def test_add_student_points_student_not_found(self, mock_runtime):
        """测试学生不存在"""
        with patch('src.tools.student_db_tool.get_session', return_value=self.mock_db_session):
            with patch('src.tools.student_db_tool.StudentManager') as mock_mgr_class:
                mock_mgr = Mock()
                mock_mgr.get_student_by_id = Mock(return_value=None)
                mock_mgr_class.return_value = mock_mgr
                
                result = add_student_points._run(
                    student_id=999,
                    points=50,
                    reason="完成作业",
                    runtime=mock_runtime,
                    config={}
                )
                
                # 验证结果
                assert "未找到" in result or "不存在" in result


@pytest.mark.unit
@pytest.mark.tool
class TestUpgradeMagicLevel(ToolTestBase):
    """测试升级魔法等级功能"""
    
    def test_upgrade_magic_level_success(self, mock_runtime, mock_student):
        """测试成功升级魔法等级"""
        # 模拟升级后的学生
        upgraded_student = Mock()
        upgraded_student.id = 1
        upgraded_student.name = "张三"
        upgraded_student.magic_level = 2
        
        with patch('src.tools.student_db_tool.get_session', return_value=self.mock_db_session):
            with patch('src.tools.student_db_tool.StudentManager') as mock_mgr_class:
                mock_mgr = Mock()
                mock_mgr.get_student_by_id = Mock(return_value=mock_student)
                mock_mgr.upgrade_magic_level = Mock(return_value=upgraded_student)
                mock_mgr_class.return_value = mock_mgr
                
                result = upgrade_magic_level._run(
                    student_id=1,
                    runtime=mock_runtime,
                    config={}
                )
                
                # 验证结果
                self.assert_success_response(result, ["恭喜", "升级", "2级"])
    
    def test_upgrade_magic_level_already_max(self, mock_runtime):
        """测试已经达到最高等级"""
        max_level_student = Mock()
        max_level_student.id = 1
        max_level_student.name = "张三"
        max_level_student.magic_level = 10
        
        with patch('src.tools.student_db_tool.get_session', return_value=self.mock_db_session):
            with patch('src.tools.student_db_tool.StudentManager') as mock_mgr_class:
                mock_mgr = Mock()
                mock_mgr.get_student_by_id = Mock(return_value=max_level_student)
                mock_mgr.upgrade_magic_level = Mock(return_value=max_level_student)
                mock_mgr_class.return_value = mock_mgr
                
                result = upgrade_magic_level._run(
                    student_id=1,
                    runtime=mock_runtime,
                    config={}
                )
                
                # 验证结果
                assert "最高等级" in result or "已经是" in result
    
    def test_upgrade_magic_level_student_not_found(self, mock_runtime):
        """测试学生不存在"""
        with patch('src.tools.student_db_tool.get_session', return_value=self.mock_db_session):
            with patch('src.tools.student_db_tool.StudentManager') as mock_mgr_class:
                mock_mgr = Mock()
                mock_mgr.get_student_by_id = Mock(return_value=None)
                mock_mgr_class.return_value = mock_mgr
                
                result = upgrade_magic_level._run(
                    student_id=999,
                    runtime=mock_runtime,
                    config={}
                )
                
                # 验证结果
                assert "未找到" in result or "不存在" in result
    
    def test_upgrade_magic_level_invalid_id(self, mock_runtime):
        """测试无效的学生ID"""
        result = upgrade_magic_level._run(
            student_id=-1,
            runtime=mock_runtime,
                    config={}
        )
        
        # 验证错误响应
        self.assert_error_response(result, ["参数错误", "ID"])


@pytest.mark.smoke
@pytest.mark.tool
class TestStudentToolsSmoke(ToolTestBase):
    """学生工具冒烟测试 - 快速验证核心功能"""
    
    def test_create_and_get_student_workflow(self, mock_runtime):
        """测试创建学生并获取信息的完整流程"""
        # 创建专门的冒烟测试学生
        smoke_student = self.create_mock_student(student_id=1, name="冒烟测试学生")
        
        with patch('src.tools.student_db_tool.get_session', return_value=self.mock_db_session):
            with patch('src.tools.student_db_tool.StudentManager') as mock_mgr_class:
                mock_mgr = Mock()
                mock_mgr.create_student = Mock(return_value=smoke_student)
                mock_mgr.get_student_by_id = Mock(return_value=smoke_student)
                mock_mgr_class.return_value = mock_mgr
                
                # 创建学生
                create_result = create_student._run(
                    name="冒烟测试学生",
                    grade="4年级",
                    class_name="2班",
                    school="测试小学",
                    parent_contact="13900139000",
                    nickname="冒烟",
                    runtime=mock_runtime,
                    config={}
                )
                assert "成功" in create_result
                
                # 获取学生信息
                get_result = get_student_info._run(
                    student_id=1,
                    runtime=mock_runtime,
                    config={}
                )
                assert "冒烟测试学生" in get_result
