from typing import Optional, List

from pydantic import BaseModel, Field

from app.core.enums import SessionType

class AnswerRequest(BaseModel):
    session_id: int = Field(description="会话ID")
    text: str = Field(description="用户回答文本", default="")
    files: list = Field(description="用户回答文本相关材料出处", default=[])
    audio: str = Field(description="用户回答音频 base64 编码", default="")
    chat_history: List[dict] = Field(description="对话历史", default_factory=list)



class SendDbinfo(BaseModel):
    db_info: int = Field(description='获取数据库标签',default=0)

class SearchDB(BaseModel):
    db_info: str = Field(description='搜索相关数据库',default='')

class KnowledgeInfo(BaseModel):
    name: str = Field(description='知识库名称')
    id: int = Field(description='知识库id')
    
class DBtier1(BaseModel):
    title: List[KnowledgeInfo] = Field(description='一级标签列表')
    
class DBtier2(BaseModel):
    content: List[KnowledgeInfo] = Field(description='知识库信息')
class SendMessageRequest(AnswerRequest):
    user_id: int = Field(description='用户id')
    selected_dbs: Optional[list[int]] = Field(description='选择的数据库',default=[])
class UserLogin(BaseModel):
    user_id: int = Field(description='用户id')
class TaskInitSessionRequest(BaseModel):
    task_id: int = Field(description="任务ID")
    session_type: SessionType = Field(description="会话类型", default=SessionType.TASK_EXERCISE)
