"""
对话标题生成工具
使用大语言模型自动生成对话标题
"""

from langchain.tools import tool, ToolRuntime
from storage.database.db import get_session
from storage.database.conversation_manager import ConversationManager
from coze_coding_utils.runtime_ctx.context import new_context


@tool
def generate_conversation_title(
    conversation_id: int,
    runtime: ToolRuntime = None
) -> str:
    """为对话自动生成标题

    Args:
        conversation_id: 对话ID
        runtime: 工具运行时上下文

    Returns:
        生成的标题
    """
    user_id, _ = (runtime.context if runtime and hasattr(runtime, 'context') else {}).get("configurable", {}).get("user_id"), None

    if not user_id:
        return "错误：无法获取用户信息"

    db = get_session()
    try:
        conv_mgr = ConversationManager()

        # 获取对话信息
        conversation = conv_mgr.get_conversation_by_id(db, conversation_id)
        if not conversation:
            return f"错误：未找到ID为{conversation_id}的对话"

        if conversation.user_id != user_id:
            return "错误：无权访问该对话"

        # 获取对话的前几条消息（最多10条）
        messages = conv_mgr.get_messages(db, conversation_id)
        if not messages:
            return "对话还没有消息，无法生成标题"

        # 取前10条消息用于分析
        sample_messages = messages[:10]

        # 构建消息文本
        message_text = ""
        for msg in sample_messages:
            role_value = getattr(msg, 'role', '')
            role_name = "用户" if role_value == "user" else "助手"
            # 限制每条消息的长度，避免过长
            content_value = getattr(msg, 'content', '')
            content = content_value[:200] if len(content_value) > 200 else content_value
            message_text += f"{role_name}：{content}\n"

        # 使用大语言模型生成标题
        try:
            # 获取 LLM 实例
            from langchain_openai import ChatOpenAI
            from coze_coding_utils.runtime_ctx.context import default_headers
            import os
            import json

            # 读取配置
            workspace_path = os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects")
            config_path = os.path.join(workspace_path, "config/agent_llm_config.json")

            with open(config_path, 'r', encoding='utf-8') as f:
                cfg = json.load(f)

            api_key = os.getenv("COZE_WORKLOAD_IDENTITY_API_KEY")
            base_url = os.getenv("COZE_INTEGRATION_MODEL_BASE_URL")

            llm = ChatOpenAI(
                model=cfg['config'].get("model"),
                api_key=api_key,
                base_url=base_url,
                temperature=0.3,  # 降低温度以获得更确定的标题
                timeout=cfg['config'].get('timeout', 600),
                extra_body={
                    "thinking": {
                        "type": cfg['config'].get('thinking', 'disabled')
                    }
                },
                default_headers=default_headers(runtime.context) if runtime else {}
            )

            # 构建提示词
            prompt = f"""请根据以下对话内容，生成一个简短、准确的对话标题（不超过15个字）。

对话内容：
{message_text}

要求：
1. 标题应该简洁明了，概括对话的主要主题
2. 标题长度不超过15个字
3. 只返回标题，不要添加其他文字
4. 使用中文

请直接输出标题："""

            # 调用 LLM
            response = llm.invoke(prompt)
            # 处理 response.content 可能是列表的情况
            content = response.content if isinstance(response.content, str) else str(response.content)
            title = content.strip()

            # 清理标题（移除可能的引号等）
            title = title.strip('"').strip("'").strip("：").strip()

            # 验证标题长度
            if len(title) > 15:
                title = title[:15]

            # 如果生成的标题为空，使用默认标题
            if not title:
                title = f"对话 - {conversation.created_at.strftime('%m-%d %H:%M')}"

            # 更新对话标题
            updated_conv = conv_mgr.update_title(db, conversation_id, title)

            if updated_conv:
                return f"✅ 标题生成成功！\n\n新标题：{title}\n对话ID：{conversation_id}"
            else:
                return f"标题生成成功，但更新失败。生成的标题：{title}"

        except Exception as llm_error:
            # 如果 LLM 调用失败，使用默认标题
            default_title = f"对话 - {conversation.created_at.strftime('%m-%d %H:%M')}"
            try:
                conv_mgr.update_title(db, conversation_id, default_title)
                return f"⚠️ 标题生成失败，已使用默认标题：{default_title}\n错误：{str(llm_error)}"
            except:
                return f"标题生成失败：{str(llm_error)}"

    except Exception as e:
        return f"生成对话标题失败：{str(e)}"
    finally:
        db.close()


@tool
def generate_title_from_messages(
    first_message: str,
    assistant_response: str = "",
    runtime: ToolRuntime = None
) -> str:
    """根据用户的第一条消息和助手回复生成对话标题

    Args:
        first_message: 用户的第一条消息
        assistant_response: 助手的回复（可选）
        runtime: 工具运行时上下文

    Returns:
        生成的标题
    """
    try:
        # 使用大语言模型生成标题
        from langchain_openai import ChatOpenAI
        from coze_coding_utils.runtime_ctx.context import default_headers
        import os
        import json

        # 读取配置
        workspace_path = os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects")
        config_path = os.path.join(workspace_path, "config/agent_llm_config.json")

        with open(config_path, 'r', encoding='utf-8') as f:
            cfg = json.load(f)

        api_key = os.getenv("COZE_WORKLOAD_IDENTITY_API_KEY")
        base_url = os.getenv("COZE_INTEGRATION_MODEL_BASE_URL")

        llm = ChatOpenAI(
            model=cfg['config'].get("model"),
            api_key=api_key,
            base_url=base_url,
            temperature=0.3,
            timeout=cfg['config'].get('timeout', 600),
            extra_body={
                "thinking": {
                    "type": cfg['config'].get('thinking', 'disabled')
                }
            },
            default_headers=default_headers(runtime.context) if runtime else {}
        )

        # 构建消息文本
        message_text = f"用户：{first_message}"
        if assistant_response:
            message_text += f"\n助手：{assistant_response}"

        # 构建提示词
        prompt = f"""请根据以下对话内容，生成一个简短、准确的对话标题（不超过15个字）。

对话内容：
{message_text}

要求：
1. 标题应该简洁明了，概括对话的主要主题
2. 标题长度不超过15个字
3. 只返回标题，不要添加其他文字
4. 使用中文
5. 适合魔法学校学习助手的场景，可以使用魔法主题的词语

请直接输出标题："""

        # 调用 LLM
        response = llm.invoke(prompt)
        # 处理 response.content 可能是列表的情况
        content = response.content if isinstance(response.content, str) else str(response.content)
        title = content.strip()

        # 清理标题
        title = title.strip('"').strip("'").strip("：").strip()

        # 验证标题长度
        if len(title) > 15:
            title = title[:15]

        # 如果生成的标题为空，使用默认标题
        if not title:
            title = "新对话"

        return f"✅ 生成的标题：{title}"

    except Exception as e:
        return f"⚠️ 标题生成失败，使用默认标题：新对话\n错误：{str(e)}"


@tool
def batch_generate_titles(
    days: int = 7,
    runtime: ToolRuntime = None
) -> str:
    """批量为最近的对话生成标题

    Args:
        days: 最近N天的对话（默认7天）
        runtime: 工具运行时上下文

    Returns:
        批量生成结果
    """
    user_id, _ = (runtime.context if runtime and hasattr(runtime, 'context') else {}).get("configurable", {}).get("user_id"), None

    if not user_id:
        return "错误：无法获取用户信息"

    db = get_session()
    try:
        conv_mgr = ConversationManager()

        # 获取最近的对话
        conversations = conv_mgr.get_recent_conversations(db, user_id, days)

        if not conversations:
            return f"最近{days}天没有对话"

        # 筛选出需要生成标题的对话（标题为默认格式的）
        to_update = []
        for conv in conversations:
            # 检查是否是默认标题（格式：对话 - YYYY-MM-DD HH:MM）
            title_value = getattr(conv, 'title', '')
            if title_value.startswith("对话 -"):
                to_update.append(conv)

        if not to_update:
            return f"✅ 最近{days}天的对话都有自定义标题，无需生成"

        results = []
        success_count = 0

        for conv in to_update:
            # 获取对话消息
            messages = conv_mgr.get_messages(db, conv.id)
            if not messages:
                continue

            # 取前几条消息
            sample_messages = messages[:5]

            # 构建消息文本
            message_text = ""
            for msg in sample_messages:
                role_value = getattr(msg, 'role', '')
                role_name = "用户" if role_value == "user" else "助手"
                content_value = getattr(msg, 'content', '')
                content = content_value[:200] if len(content_value) > 200 else content_value
                message_text += f"{role_name}：{content}\n"

            # 生成标题
            try:
                from langchain_openai import ChatOpenAI
                from coze_coding_utils.runtime_ctx.context import default_headers
                import os
                import json

                workspace_path = os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects")
                config_path = os.path.join(workspace_path, "config/agent_llm_config.json")

                with open(config_path, 'r', encoding='utf-8') as f:
                    cfg = json.load(f)

                api_key = os.getenv("COZE_WORKLOAD_IDENTITY_API_KEY")
                base_url = os.getenv("COZE_INTEGRATION_MODEL_BASE_URL")

                llm = ChatOpenAI(
                    model=cfg['config'].get("model"),
                    api_key=api_key,
                    base_url=base_url,
                    temperature=0.3,
                    timeout=cfg['config'].get('timeout', 600),
                    extra_body={
                        "thinking": {
                            "type": cfg['config'].get('thinking', 'disabled')
                        }
                    },
                    default_headers=default_headers(runtime.context) if runtime else {}
                )

                prompt = f"""请根据以下对话内容，生成一个简短、准确的对话标题（不超过15个字）。

对话内容：
{message_text}

要求：
1. 标题应该简洁明了，概括对话的主要主题
2. 标题长度不超过15个字
3. 只返回标题，不要添加其他文字
4. 使用中文
5. 适合魔法学校学习助手的场景

请直接输出标题："""

                response = llm.invoke(prompt)
                # 处理 response.content 可能是列表的情况
                content = response.content if isinstance(response.content, str) else str(response.content)
                title = content.strip()
                title = title.strip('"').strip("'").strip("：").strip()

                if len(title) > 15:
                    title = title[:15]

                if title:
                    # 更新标题
                    conv_mgr.update_title(db, conv.id, title)
                    success_count += 1
                    results.append(f"✅ {conv.id}: {conv.title} -> {title}")
                else:
                    results.append(f"⚠️ {conv.id}: 生成标题为空")

            except Exception as e:
                results.append(f"❌ {conv.id}: 生成失败 - {str(e)}")

        summary = f"批量生成标题完成！\n\n"
        summary += f"总计：{len(to_update)}个对话\n"
        summary += f"成功：{success_count}个\n"
        summary += f"失败：{len(to_update) - success_count}个\n\n"
        summary += "详细结果：\n\n"

        for result in results:
            summary += result + "\n"

        return summary

    except Exception as e:
        return f"批量生成标题失败：{str(e)}"
    finally:
        db.close()
