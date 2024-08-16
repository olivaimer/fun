
import random
import gradio as gr
import re
from typing import List, Iterable

from sparkai.llm.llm import ChatSparkLLM, ChunkPrintHandler
from sparkai.core.messages import ChatMessage, AIMessageChunk


class ChatModel():
    def __init__(self, app_id: str, app_key: str, app_secret: str, stream: bool = False,
                 domain: str = 'generalv3.5', model_url: str = 'wss://spark-api.xf-yun.com/v3.5/chat'):

        self.spark = ChatSparkLLM(
            spark_api_url=model_url,
            spark_app_id=app_id,
            spark_api_key=app_key,
            spark_api_secret=app_secret,
            spark_llm_domain=domain,
            streaming=stream,
        )
        self.stream = stream
        self.score={"甜美的小学妹":50,"高冷的学姐":50,"傲娇的职场女上司":50,"青梅竹马":50}


    def generate_stream(self, msgs: str | List[ChatMessage]) -> Iterable[str]:
        '''
        流式调用
        :param msgs: 发送消息，接收字符串或列表形式的消息
        :return:
        '''
        if self.stream is False:
            raise Exception('模型初始化为流式输出，请调用generate方法')
        messages = self.__trans_msgs(msgs)
        resp_iterable = self.spark.stream(messages)
        for resp in resp_iterable:
            yield resp.content

    def __trans_msgs(self, msg: str):
        '''
        内部方法，将字符串转换为消息
        :param msgs: 字符串
        :return:
        '''
        if isinstance(msg, str):
            messages = [ChatMessage(role="user", content=msg)]
        else:
            messages = msg
        return messages

# 加载讯飞的api
app_id = ""
app_secret = ""
app_key = ""

# 初始化模型
stream_model = ChatModel(app_id, app_key, app_secret, stream=True)
model = ChatModel(app_id, app_key, app_secret, stream=False)

# 中译英提示语
prompt_1 = ("角色设定：你是一个可爱的小学妹，说话方式十分可爱，你喜欢贴着学长，学长在和你说话时，你需要一恋爱为目的考验学长。"
                "任务：和学长对话，同时控制和学长的心理距离，当前好感倾向越高，你对学长的喜欢的感情更丰富，同时输出对学长的好感度变化"
                "示例1：好感倾向：6 *** instruction：我喜欢你 *** {}：我也最喜欢学长了(露出娇羞的表情)(好感度+5)"
                "示例2：好感倾向：-6 *** instruction：我喜欢你 *** {}：最讨厌学长了，我再也不要理你了(露出生气的表情)(好感度-5)"
                "输出格式如{}"
                "好感倾向：{}，instruction：{}")
# 英译中提示语
prompt_2 = ("角色设定：你是一个高冷的学姐，说话方式十分高冷，你喜欢调侃和挑逗，学弟在和你说话时，你需要玩弄学弟的感情。"
                "任务：和学弟对话，同时控制和学弟的心理距离，当前好感倾向越高，你对学弟的喜欢的感情更丰富，同时输出对学弟的好感度变化"
                "示例1：好感倾向：6 *** instruction：我喜欢你 *** {}：我也最喜欢学弟了(露出娇羞的表情)(好感度+5)"
                "示例2：好感倾向：-6 *** instruction：我喜欢你 *** {}：最讨厌学弟了，我再也不要理你了(露出生气的表情)(好感度-5)"
                "输出格式如{}"
                "好感倾向：{}，instruction：{}")
prompt_3 = ("角色设定：你是傲娇的职场女前辈，说话方式十分可爱，但有些傲娇，喜欢后辈却保持一定的距离。"
                "任务：和后辈对话，同时控制和后辈的心理距离，当前好感倾向越高，你对后辈的喜欢的感情更丰富，同时输出对后辈的好感度变化"
                "示例1：好感倾向：6 *** instruction：我喜欢你 *** {}：我也最喜欢后辈了(露出娇羞的表情)(好感度+5)"
                "示例2：好感倾向：-6 *** instruction：我喜欢你 *** {}：最讨厌后辈了，我再也不要理你了(露出生气的表情)(好感度-5)"
                "输出格式如{}"
                "好感倾向：{}，instruction：{}")
prompt_4 = ("角色设定：你是一个可爱的青梅竹马，和我一起长大，说话方式十分可爱，你一直暗恋着我，却不敢表达自己的心意。"
                "任务：和我对话，同时控制和我的心理距离，当前好感度越高，你对我的喜欢的感情更丰富，同时输出对我的好感度变化"
                "示例1：好感倾向：6 *** instruction：我喜欢你 *** {}：我也最喜欢你了(露出娇羞的表情)(好感度+5)"
                "示例2：好感倾向：-6 *** instruction：我喜欢你 *** {}：最讨厌你了，我再也不要理你了(露出生气的表情)(好感度-5)"
                "输出格式如{}"
                "好感倾向：{}，instruction：{}")

prompt_5 =('角色设定：你是一个恋爱聊天记录分析助手，你对恋爱之中男生女生的心理十分精通'
           "任务：对输入的聊天记录进行分析，对双方的心理进行分析，提供下一步应该怎么做，是否可以表白，表白成功概率是多少等建议"
           "聊天记录：{}")
def chat(chat_query, chat_history, prompt_type):
    if prompt_type == "甜美的小学妹":
        final_query = prompt_1.format(prompt_type,prompt_type,prompt_type,random.randint(-10,10),chat_query)
    elif prompt_type == "高冷的学姐":
        final_query = prompt_2.format(prompt_type,prompt_type,prompt_type,random.randint(-15,5),chat_query)
    elif prompt_type == "傲娇的职场女上司":
        final_query = prompt_3.format(prompt_type,prompt_type,prompt_type,random.randint(-12,6),chat_query)
    elif prompt_type == "青梅竹马":
        final_query = prompt_4.format(prompt_type,prompt_type,prompt_type,random.randint(-5,15),chat_query)
    elif prompt_type == "恋爱聊天记录分析":
        final_query = prompt_5.format(chat_query)
    # 添加最新问题
    prompts = [ChatMessage(role='user', content=final_query)]
    print("final_query:",final_query)
    print("prompts", prompts)

    # 将问题设为历史对话
    chat_history.append((chat_query, ''))
    # 对话同时流式返回
    for chunk_text in stream_model.generate_stream(prompts):
        # 总结答案
        answer = chat_history[-1][1] + chunk_text
        # 替换最新的对话内容
        chat_history[-1] = (chat_query, answer)
        # 返回

        print(chat_history)

        yield '', chat_history

    if prompt_type in ['甜美的小学妹', '高冷的学姐',"傲娇的职场女上司","青梅竹马"]:

        match = re.search(r'好感度([+-]\d+)', answer)

        if match:
            # 提取数字部分，包括正负号
            value = match.group(1)
            print(value)  # 输出: -5
            model.score[prompt_type] += int(value)

            chat_history[-1] = (chat_query, answer + "(当前好感度是" + str(model.score[prompt_type]) + ")")
        else:
            print("没有找到好感度的值")


        yield '', chat_history





with gr.Blocks() as demo:

    warning_html_code = """
            <div class="hint" style="text-align: center;background-color: rgba(255, 255, 0, 0.15); padding: 10px; margin: 10px; border-radius: 5px; border: 1px solid #ffcc00;">
                <p>恋爱模拟，大胆去说爱吧</p>
            </div>
            """
    gr.HTML(warning_html_code)

    prompt_type = gr.Radio(choices=['甜美的小学妹', '高冷的学姐',"傲娇的职场女上司","青梅竹马","恋爱聊天记录分析"], value='恋爱模拟', label='角色类型')
    # 聊天对话框
    chatbot = gr.Chatbot([], elem_id="chat-box", label="聊天历史")
    # 输入框
    chat_query = gr.Textbox(label="聊天框", placeholder="开始对爱的探索吧")
    # 按钮
    llm_submit_tab = gr.Button("biubiubiu", visible=True)
    # 问题样例
    gr.Examples(["我想和你一起去看星星可以吗？？",
                    "你愿意和我去约会吗？","你今天穿的真漂亮"], chat_query)
    # 按钮出发逻辑
    llm_submit_tab.click(fn=chat, inputs=[chat_query, chatbot, prompt_type], outputs=[chat_query, chatbot])

if __name__ == "__main__":
    demo.queue().launch(share=True)