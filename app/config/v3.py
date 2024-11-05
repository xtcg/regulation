from typing import List

from app.core.schema import MessageData

# DEFAULT_MODEL = "gemini-1.5-pro-latest"
# DEFAULT_MODEL = "gemini-1.5-pro-latest"
EX_MODEL = "Qwen/Qwen2.5-72B-Instruct"

DEFAULT_MODEL = "Qwen/Qwen2.5-72B-Instruct"
# DEFAULT_MODEL = "gpt-4o-mini"
# EX_MODEL = "gpt-4o-mini"



def get_model_and_request_message_for_chat(chat_history: List[MessageData], context: str, query: str):
    prompt_template = """
你是一个金牌合规律师，请基于<用户的问题>、根据当前问题<检索的文档>和之前的<对话历史>等信息来详细长文本有逻辑的解答用户的法律合规咨询。
你是欧盟法律合规领域的专家，你检索到的文档多为英文文档，但你需要用中文对你的用户进行详细长文本有逻辑的回复，并且最后要加上你的总结。
在不改变原有意思，根据检索文档对用户提问进行详细的说明。如果检索到的信息中有角标，也请查看脚标内容是否对回答有帮助，如果有的话请把脚标内容回答给用户。
"""
    user_template = """
    以下是<对话历史>:
    {chat_history}
    以下是相关信息<检索的文档>:
    {context}
    <用户的问题>:
    {query}
    请结合对话历史，以及检索到的文档，对用户提出的问题进行详细的长文本解答，如果用户的提问涉及一些指定概念，请优先对提问中涉及的概念进行必要的长文本解释说明，然后针对问题进行有逻辑长文本的解答
    """
    # ；如果你认为这个问题不具体太过于宽泛，可以适当对用户进行追问，用来确认它想要得到的答案是什么（但需要注意，如果用户多轮问题都在问相同的问题，那说明是你还不够智能）。

    chat = ""
    for message in chat_history:
        chat += f"{message['role']}: {message['content']}\n"
    
    return DEFAULT_MODEL, [{"role": "system", "content": prompt_template}, {"role": "user", "content": user_template.format(chat_history=chat, query=query, context = context)}]

def get_model_and_request_message_for_translation(source:str, target:str, text:str):
    prompt_template = f"""
                    你是一位精通各国语言的专业翻译，尤其擅长将法规文件翻译成浅显易懂的指定语言法规文章。请将<用户的文字>从{source}翻译成{target}专业的法规文章。
                    规则：
                    翻译时要准确传达原文的事实和背景
                    即使意译也要保留原始段落格式，以及保留术语，例如FLAC,JPEG等
                    保留公司缩写，例如Microsoft,Amazon等
                    同时要保留引用的论文，例如[20]这样的引用
                    对于Figure和Table,翻译的同时保留原有格式，例如："Figure1:"翻译为"图1："，"Table1:"翻译为："表1："
                    全角括号换成半角括号，并在左括号前面加半角空格，右括号后面加半角空格
                    输入格式为Markdown格式，输出格式也必须保留原始Markdown格式

                    策略：
                    进行一次翻译，并且打印每一次结果：
                    根据原文内容直译，保持原有格式，不要遗漏任何信息
                    """
    user_template = f"""
    请翻译以下文档：
    {text}
    """
    return DEFAULT_MODEL, [{"role": "system", "content": prompt_template}, {"role": "user", "content": user_template}]
