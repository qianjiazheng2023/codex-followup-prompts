#!/usr/bin/env python3
"""为当前 Codex 回合注入稳定的追问建议规则。"""

import json
import sys


def main() -> int:
    # Codex 的钩子协议使用 UTF-8；Windows 下显式开启它，避免中文规则被系统代码页损坏。
    if hasattr(sys.stdin, "reconfigure"):
        sys.stdin.reconfigure(encoding="utf-8")
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    # Codex 通过 stdin 提供钩子事件。这里不需要解析事件内容：模型本身已有完整对话上下文。
    sys.stdin.read()

    instruction = """
本轮最终回复完成后，必须在最末尾附加一个“你可能接着问”小节。这个小节是给用户点击或复制的下一问建议，不是给出的答案的一部分。

生成规则：
1. 始终输出恰好 3 条建议，使用 Markdown 无序列表；每条必须是一句可直接作为用户消息发送的中文追问。
2. 先看本轮用户需求和最近 4 至 8 条对话，再用更早的对话目标消除歧义。建议必须指向当前任务中尚未完成、值得继续推进或需要澄清的内容。
3. 三条分别尽量覆盖：继续执行、关键细节或风险、替代方案或验证。若对话不适合某一类，优先保证相关性，不要为了凑分类而生造问题。
4. 每条不超过 32 个汉字或约 50 个字符；要具体、自包含、可执行。保留当前任务中的关键对象，不要用“这个”“上面”“它”这类脱离上下文的指代。
5. 不要重复用户已经问过或已经完成的事项；不要建议无关闲聊；不要写“如果需要”“要不要”“你可以”等引导语。
6. 当最终回复本身是在等待用户确认或选择时，三条建议应是对应的明确选择或补充信息请求。
7. 只有当用户明确说“不显示追问”“关闭追问建议”或等义指令时，才省略该小节。

严格格式：在答案正文结束后留一空行，然后输出标题“### 你可能接着问”，再输出三条列表。除标题和三条列表外，不要为该小节增加解释。
""".strip()

    output = {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": instruction,
        }
    }
    print(json.dumps(output, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
