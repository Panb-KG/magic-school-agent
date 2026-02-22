# 测试指南

## 测试框架概述

本项目使用 pytest 作为测试框架，提供了完整的测试基础设施，包括单元测试、集成测试和冒烟测试。

## 测试目录结构

```
tests/
├── conftest.py              # pytest 全局配置和 fixtures
├── test_base.py             # 测试基类（ToolTestBase, DatabaseTestBase 等）
├── tools/                   # 工具测试
│   ├── test_student_db_tool.py
│   ├── test_homework_db_tool.py
│   └── ...
├── agents/                  # Agent 测试
└── integration/             # 集成测试
```

## 测试分类

### 1. 单元测试 (Unit Tests)
- **标记**: `@pytest.mark.unit`
- **特点**: 快速、独立、不依赖外部服务
- **用途**: 测试单个函数、类或模块的功能

示例：
```python
@pytest.mark.unit
def test_create_student_success():
    result = create_student(...)
    assert "成功" in result
```

### 2. 集成测试 (Integration Tests)
- **标记**: `@pytest.mark.integration`
- **特点**: 需要数据库、API 等外部服务
- **用途**: 测试组件之间的交互

示例：
```python
@pytest.mark.integration
def test_student_homework_workflow():
    # 测试学生和作业的完整流程
    pass
```

### 3. 冒烟测试 (Smoke Tests)
- **标记**: `@pytest.mark.smoke`
- **特点**: 快速验证核心功能是否正常
- **用途**: 每次部署前快速检查

示例：
```python
@pytest.mark.smoke
def test_core_features():
    # 测试核心功能
    pass
```

### 4. 工具测试 (Tool Tests)
- **标记**: `@pytest.mark.tool`
- **特点**: 专门测试 LangChain 工具

示例：
```python
@pytest.mark.unit
@pytest.mark.tool
class TestCreateStudent(ToolTestBase):
    def test_create_student_success(self):
        pass
```

### 5. 慢速测试 (Slow Tests)
- **标记**: `@pytest.mark.slow`
- **特点**: 耗时较长的测试
- **用途**: 测试需要大量计算或 I/O 的功能

## 运行测试

### 运行所有测试
```bash
pytest
```

### 运行特定类型的测试
```bash
# 只运行单元测试
pytest -m unit

# 只运行集成测试
pytest -m integration

# 只运行冒烟测试
pytest -m smoke

# 只运行工具测试
pytest -m tool

# 排除慢速测试
pytest -m "not slow"
```

### 运行特定文件
```bash
pytest tests/tools/test_student_db_tool.py
```

### 运行特定测试类或方法
```bash
# 运行特定类
pytest tests/tools/test_student_db_tool.py::TestCreateStudent

# 运行特定测试方法
pytest tests/tools/test_student_db_tool.py::TestCreateStudent::test_create_student_success
```

### 详细输出
```bash
# 显示详细的测试输出
pytest -v

# 显示失败的测试的局部变量
pytest -l

# 显示测试的耗时
pytest -d

# 显示简短的测试摘要
pytest -ra
```

### 并行运行测试（需要 pytest-xdist）
```bash
pytest -n auto
```

## 测试覆盖率

### 安装覆盖率工具
```bash
pip install pytest-cov
```

### 生成覆盖率报告
```bash
# 生成终端报告
pytest --cov=src --cov-report=term-missing

# 生成 HTML 报告
pytest --cov=src --cov-report=html

# 生成 XML 报告（用于 CI/CD）
pytest --cov=src --cov-report=xml
```

### 查看覆盖率报告
```bash
# 打开 HTML 报告
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

## 编写测试

### 基本测试结构

```python
import pytest
from tests.test_base import ToolTestBase

@pytest.mark.unit
class TestMyFunction(ToolTestBase):
    """测试我的函数"""
    
    def test_normal_case(self, mock_runtime):
        """测试正常情况"""
        result = my_function(param1, param2, runtime=mock_runtime)
        assert "成功" in result
    
    def test_edge_case(self):
        """测试边界情况"""
        result = my_function(empty_param)
        assert "错误" in result
```

### 使用 Mock 对象

```python
from unittest.mock import Mock, patch

def test_with_mock(self, mock_runtime):
    # Mock 数据库会话
    with patch('tools.my_tool.get_session', return_value=self.mock_db_session):
        # Mock 管理器
        with patch('tools.my_tool.MyManager') as mock_mgr_class:
            mock_mgr = Mock()
            mock_mgr.my_method = Mock(return_value="测试结果")
            mock_mgr_class.return_value = mock_mgr
            
            # 执行测试
            result = my_tool.my_function(runtime=mock_runtime)
            
            # 验证
            self.assert_success_response(result, ["测试结果"])
```

### 使用 Fixtures

```python
def test_with_fixtures(self, mock_student, mock_runtime):
    """使用 fixtures 的测试"""
    with patch('tools.my_tool.get_student_by_id', return_value=mock_student):
        result = my_tool.get_info(student_id=1, runtime=mock_runtime)
        assert mock_student.name in result
```

## 测试最佳实践

### 1. 遵循 AAA 模式
- **Arrange（准备）**: 设置测试数据和 Mock 对象
- **Act（执行）**: 调用被测试的函数
- **Assert（断言）**: 验证结果

```python
def test_example(self):
    # Arrange
    mock_student = self.create_mock_student(name="张三")
    
    # Act
    result = get_student_info(student_id=1, runtime=self.create_mock_runtime())
    
    # Assert
    assert "张三" in result
```

### 2. 使用描述性的测试名称
```python
# 好的测试名称
def test_create_student_with_empty_name_should_return_error(self):
    pass

# 不好的测试名称
def test_create_student(self):
    pass
```

### 3. 测试边界条件
```python
def test_with_zero_value(self):
    pass

def test_with_negative_value(self):
    pass

def test_with_max_value(self):
    pass
```

### 4. 测试错误处理
```python
def test_database_error(self):
    """测试数据库错误"""
    with patch('tools.my_tool.get_session', side_effect=Exception("数据库错误")):
        result = my_tool.my_function(runtime=mock_runtime)
        assert "失败" in result
```

### 5. 保持测试独立
每个测试应该独立运行，不依赖其他测试的状态。

### 6. 使用测试基类
```python
from tests.test_base import ToolTestBase

class MyToolTests(ToolTestBase):
    # 继承测试基类，获得通用的 setup 和辅助方法
    pass
```

## CI/CD 集成

### GitHub Actions 示例

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov pytest-xdist
      - name: Run tests
        run: pytest --cov=src --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## 调试测试

### 使用 pdb 调试
```bash
pytest --pdb
```

### 在失败时进入 pdb
```bash
pytest --pdb --trace
```

### 只运行上次失败的测试
```bash
pytest --lf
```

### 在失败时停止
```bash
pytest -x
```

## 常见问题

### Q: 如何跳过某个测试？
```python
@pytest.mark.skip(reason="暂未实现")
def test_not_implemented(self):
    pass
```

### Q: 如何有条件地跳过测试？
```python
@pytest.mark.skipif(sys.version_info < (3, 8), reason="需要 Python 3.8+")
def test_requires_new_python(self):
    pass
```

### Q: 如何预期某个测试会失败？
```python
@pytest.mark.xfail(reason="已知问题")
def test_known_issue(self):
    pass
```

## 参考资料

- [pytest 官方文档](https://docs.pytest.org/)
- [pytest 中文文档](https://pytest-chinese-doc.readthedocs.io/)
- [unittest.mock 文档](https://docs.python.org/3/library/unittest.mock.html)
