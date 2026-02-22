"""
工具日志配置
为所有工具提供统一的日志记录功能
"""

import logging
import sys
from typing import Optional
from functools import wraps

# 配置日志格式
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'


def get_tool_logger(name: Optional[str] = None):
    """
    获取工具的 logger
    
    Args:
        name: logger 名称，如果为 None 则使用调用者的模块名
    
    Returns:
        配置好的 logger 实例
    """
    if name is None:
        # 获取调用者的模块名
        import inspect
        frame = inspect.currentframe()
        name = frame.f_back.f_globals.get('__name__', 'tool')
    
    logger = logging.getLogger(name)
    
    # 如果还没有配置过，则配置
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    
    return logger


def log_tool_call(func):
    """
    工具调用日志装饰器
    
    自动记录工具的调用、参数和返回值
    
    Args:
        func: 被装饰的函数
    
    Returns:
        包装后的函数
    """
    logger = get_tool_logger(func.__module__)
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        func_name = func.__name__
        
        # 记录调用
        logger.info(f"🔧 调用工具: {func_name}")
        
        # 记录参数（过滤掉 runtime 和 password 等敏感信息）
        safe_kwargs = {k: v for k, v in kwargs.items() 
                     if k not in ['runtime', 'password', 'token']}
        if safe_kwargs:
            logger.debug(f"  参数: {safe_kwargs}")
        
        try:
            # 执行函数
            result = func(*args, **kwargs)
            
            # 记录成功
            logger.info(f"✅ 工具 {func_name} 执行成功")
            return result
        
        except Exception as e:
            # 记录错误
            logger.error(f"❌ 工具 {func_name} 执行失败: {str(e)}", exc_info=True)
            raise
    
    return wrapper


def handle_tool_error(func):
    """
    工具错误处理装饰器
    
    自动捕获工具函数的异常并返回友好的错误消息
    
    Args:
        func: 被装饰的函数
    
    Returns:
        包装后的函数
    """
    logger = get_tool_logger(func.__module__)
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            # 参数错误
            logger.warning(f"⚠️  参数错误: {str(e)}")
            return f"参数错误：{str(e)}"
        except PermissionError as e:
            # 权限错误
            logger.warning(f"⚠️  权限错误: {str(e)}")
            return f"权限错误：{str(e)}"
        except FileNotFoundError as e:
            # 文件未找到
            logger.warning(f"⚠️  文件未找到: {str(e)}")
            return f"文件未找到：{str(e)}"
        except Exception as e:
            # 其他错误
            logger.error(f"❌ 工具执行失败: {str(e)}", exc_info=True)
            return f"执行失败：{str(e)}"
    
    return wrapper


class ToolExecutionError(Exception):
    """工具执行错误基类"""
    
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        """
        初始化工具执行错误
        
        Args:
            message: 错误消息
            original_error: 原始异常
        """
        self.message = message
        self.original_error = original_error
        super().__init__(self.message)
    
    def __str__(self):
        if self.original_error:
            return f"{self.message} (原始错误: {str(self.original_error)})"
        return self.message


class DatabaseError(ToolExecutionError):
    """数据库操作错误"""
    pass


class PermissionDeniedError(ToolExecutionError):
    """权限拒绝错误"""
    pass


class ValidationError(ToolExecutionError):
    """数据验证错误"""
    pass


class ResourceNotFoundError(ToolExecutionError):
    """资源未找到错误"""
    pass


def safe_execute(func, error_message: str = "操作失败"):
    """
    安全执行函数的辅助函数
    
    Args:
        func: 要执行的函数
        error_message: 错误消息前缀
    
    Returns:
        函数执行结果或错误消息
    """
    logger = get_tool_logger()
    
    try:
        return func()
    except DatabaseError as e:
        logger.error(f"数据库错误: {str(e)}", exc_info=True)
        return f"{error_message}（数据库错误）：{str(e)}"
    except PermissionDeniedError as e:
        logger.warning(f"权限错误: {str(e)}")
        return f"{error_message}（权限错误）：{str(e)}"
    except ValidationError as e:
        logger.warning(f"验证错误: {str(e)}")
        return f"{error_message}（验证错误）：{str(e)}"
    except ResourceNotFoundError as e:
        logger.warning(f"资源未找到: {str(e)}")
        return f"{error_message}（资源未找到）：{str(e)}"
    except Exception as e:
        logger.error(f"未知错误: {str(e)}", exc_info=True)
        return f"{error_message}：{str(e)}"
