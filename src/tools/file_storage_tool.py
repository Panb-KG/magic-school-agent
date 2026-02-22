import os
from langchain.tools import tool, ToolRuntime
from tools.tool_utils_fixed import (
    get_user_context,
    check_student_access,
    require_student_access,
    get_student_name_by_id
)
from coze_coding_dev_sdk.s3 import S3SyncStorage


def get_storage():
    """获取S3存储客户端"""
    return S3SyncStorage(
        endpoint_url=os.getenv("COZE_BUCKET_ENDPOINT_URL"),
        access_key="",
        secret_key="",
        bucket_name=os.getenv("COZE_BUCKET_NAME"),
        region="cn-beijing",
    )


@tool
@require_student_access()
def upload_homework_attachment(
    file_content: bytes,
    file_name: str,
    student_id: int,
    runtime: ToolRuntime
) -> str:
    """上传作业附件到对象存储
    
    Args:
        file_content: 文件内容（bytes）
        file_name: 文件名
        student_id: 学生ID
    
    Returns:
        文件的S3对象key
    """
    storage = get_storage()
    # 使用学生ID作为前缀
    prefix = f"students/{student_id}/homework/"
    full_file_name = f"{prefix}{file_name}"
    object_key = storage.upload_file(
        file_content=file_content,
        file_name=full_file_name,
        content_type="application/octet-stream"
    )
    return object_key


@tool
@require_student_access()
def upload_homework_submission(
    file_content: bytes,
    file_name: str,
    student_id: int,
    runtime: ToolRuntime
) -> str:
    """上传作业提交文件到对象存储
    
    Args:
        file_content: 文件内容（bytes）
        file_name: 文件名
        student_id: 学生ID
    
    Returns:
        文件的S3对象key
    """
    storage = get_storage()
    prefix = f"students/{student_id}/submissions/"
    full_file_name = f"{prefix}{file_name}"
    object_key = storage.upload_file(
        file_content=file_content,
        file_name=full_file_name,
        content_type="application/octet-stream"
    )
    return object_key


@tool
@require_student_access()
def upload_courseware(
    file_content: bytes,
    file_name: str,
    student_id: int,
    file_type: str,
    runtime: ToolRuntime
) -> str:
    """上传课件到对象存储
    
    Args:
        file_content: 文件内容（bytes）
        file_name: 文件名
        student_id: 学生ID
        file_type: 文件类型（pdf/doc/ppt/image/video/other）
    
    Returns:
        文件的S3对象key
    """
    storage = get_storage()
    prefix = f"students/{student_id}/coursewares/"
    full_file_name = f"{prefix}{file_name}"
    object_key = storage.upload_file(
        file_content=file_content,
        file_name=full_file_name,
        content_type="application/octet-stream"
    )
    return object_key


@tool
@require_student_access()
def upload_achievement_icon(
    file_content: bytes,
    file_name: str,
    student_id: int,
    runtime: ToolRuntime
) -> str:
    """上传成就图标到对象存储
    
    Args:
        file_content: 文件内容（bytes）
        file_name: 文件名
        student_id: 学生ID
    
    Returns:
        文件的S3对象key
    """
    storage = get_storage()
    prefix = f"students/{student_id}/achievements/"
    full_file_name = f"{prefix}{file_name}"
    object_key = storage.upload_file(
        file_content=file_content,
        file_name=full_file_name,
        content_type="image/png"
    )
    return object_key


@tool
def download_file(
    file_key: str,
    runtime: ToolRuntime
) -> bytes:
    """从对象存储下载文件
    
    Args:
        file_key: 文件的S3对象key
    
    Returns:
        文件内容（bytes）
    """
    storage = get_storage()
    return storage.read_file(file_key=file_key)


@tool
def generate_file_url(
    file_key: str,
    runtime: ToolRuntime,
    expire_time: int = 1800
) -> str:
    """生成文件下载链接

    Args:
        file_key: 文件的S3对象key
        runtime: ToolRuntime对象
        expire_time: 过期时间（秒），默认30分钟

    Returns:
        签名的下载URL
    """
    storage = get_storage()
    return storage.generate_presigned_url(key=file_key, expire_time=expire_time)


@tool
def delete_file(
    file_key: str,
    runtime: ToolRuntime
) -> bool:
    """删除对象存储中的文件
    
    Args:
        file_key: 文件的S3对象key
    
    Returns:
        是否删除成功
    """
    storage = get_storage()
    return storage.delete_file(file_key=file_key)


@tool
@require_student_access()
def list_student_files(
    student_id: int,
    file_type: str,
    runtime: ToolRuntime
) -> str:
    """列出学生的所有文件
    
    Args:
        student_id: 学生ID
        file_type: 文件类型（homework/courseware/achievement/submission）
    
    Returns:
        文件列表的JSON字符串
    """
    storage = get_storage()
    prefix = f"students/{student_id}/{file_type}/"
    result = storage.list_files(prefix=prefix, max_keys=100)
    return f"文件列表: {result['keys']}"
