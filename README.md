# AI Learning Platform
## 主要功能
1. AI陪练

2. AI知识库

 ## 算法相关的代码
改retrieval的逻辑 以及 判断是否需要retrieval的prompt在：
app/core/service/knowledge.py
大部分情况下只涉及query_and_rerank和is_need_rag

改多轮问答 以及 陪练打分的相关功能的prompt在：
app/config/v3.py
get_model_and_request_message_for_question 是模拟顾客提问题的
get_model_and_request_message_for_single_score 是根据当前轮次的顾客/销售的问答来给出分数的
get_model_and_request_message_for_score 是根据一轮训练的整体对话来打分的
get_model_and_request_message_for_chat 是智能问答的prompt
