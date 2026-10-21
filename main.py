"""
astrbot_plugin_custom_reply - 未知指令兜底插件

当用户发送以 / 开头的消息，且没有其他插件响应时，输出兜底文本。
支持在配置中直接换行或使用 \n 进行换行。
"""

from astrbot.api import logger
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star
from astrbot.core import AstrBotConfig


class CustomReplyPlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.config = config

    async def initialize(self):
        logger.info("[CustomReply] 未知指令兜底插件已加载")

    async def terminate(self):
        logger.info("[CustomReply] 未知指令兜底插件已卸载")

    # 关键：设置 priority=999，确保在所有正常指令插件之后执行
    @filter.regex(r"^/([^\s]+)", priority=999)
    async def on_unknown_command(self, event: AstrMessageEvent):
        # 1. 检查开关
        if not self.config.get("enable", True):
            return
            
        # 2. 走到这里，说明没有任何插件认领这个 / 指令
        # 拦截事件，防止触发 AI 或其他后续逻辑
        event.stop_event()
        
        # 3. 获取配置文本并处理换行
        fallback_text = self.config.get("fallback_text", "🤔 没有找到这个功能哦，请检查指令是否输入正确~")
        
        # 把用户可能在 WebUI 输入的 \n 转换为真实的换行符
        # 如果用户直接在 WebUI 文本框里按了回车（真实换行），这里也能保留
        fallback_text = str(fallback_text).replace("\\n", "\n")
        
        # 4. 发送兜底回复
        yield event.plain_result(fallback_text)