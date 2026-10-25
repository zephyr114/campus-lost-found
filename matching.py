# -*- coding: utf-8 -*-
"""
matching.py  AI向量匹配核心模块
用智谱 Embedding 向量 + 余弦相似度，实现失物/拾物语义匹配
"""
from zhipuai import ZhipuAI
import numpy as np
import os
import base64

# ========= 智谱 API Key 读取顺序：config.py（本地）> 环境变量 > Streamlit Cloud secrets =========
try:
    from config import API_KEY          # config.py 已被 .gitignore 排除，不会上传到 GitHub
except ImportError:
    API_KEY = os.environ.get("ZHIPUAI_API_KEY", "")
# Streamlit Cloud 部署：Secrets 通过 st.secrets 注入，不在 os.environ 里
if not API_KEY:
    try:
        import streamlit as st
        API_KEY = st.secrets.get("ZHIPUAI_API_KEY", "")
    except Exception:
        pass

# API Key 未配置时给出明确提示，避免程序崩溃
if API_KEY == "" or "填入" in API_KEY:
    print("[警告] 尚未配置智谱 API_KEY：请复制 config.example.py 为 config.py 并填入你自己的 Key（或设置环境变量 ZHIPUAI_API_KEY）后再运行匹配功能！")
    client = None
else:
    client = ZhipuAI(api_key=API_KEY)

# 简单的 embedding 缓存：同一段文本只调一次接口，批量匹配时能省大量请求
_embedding_cache = {}


# 获取文本embedding向量
def get_embedding(text: str):
    if client is None:
        raise RuntimeError("未配置智谱 API_KEY，请先在 matching.py 中填入你的 Key")

    text = text.strip()
    if not text:
        return np.zeros(1024)

    # 命中缓存直接返回
    if text in _embedding_cache:
        return _embedding_cache[text]

    response = client.embeddings.create(
        model="embedding-2",
        input=text
    )
    vec = np.array(response.data[0].embedding)
    _embedding_cache[text] = vec          # 写入缓存
    return vec


# 用智谱 GLM-4V 视觉模型识别图片，返回物品外观的文字描述
# 思路：不直接做图像向量，而是让多模态模型把"图片"翻译成"文字描述"，再复用文本 embedding 匹配
def describe_image(image_bytes: bytes, content_type: str = "image/jpeg") -> str:
    if client is None:
        raise RuntimeError("未配置智谱 API_KEY，请先在 matching.py 中填入你的 Key")
    b64 = base64.b64encode(image_bytes).decode("utf-8")
    response = client.chat.completions.create(
        model="glm-4v-plus",
        messages=[{
            "role": "user",
            "content": [
                {"type": "text",
                 "text": "请用一句话简洁描述图中物品的外观特征（颜色、品牌、款式、明显标记），20-40字，不要寒暄，不要描述背景。"},
                {"type": "image_url", "image_url": {"url": f"data:{content_type};base64,{b64}"}}
            ]
        }]
    )
    return response.choices[0].message.content.strip()


# 计算余弦相似度
def cosine_similarity(vec1, vec2):
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    if norm1 == 0 or norm2 == 0:
        return 0
    return dot_product / (norm1 * norm2)


# 批量匹配：遍历所有失物、拾物，返回高分匹配对
def match_all(lost_list, found_list, threshold=0.7):
    result = []
    for lost in lost_list:
        # lost: id,item_name,desc,loc,time,contact,create,image_path,image_desc
        lost_text = f"{lost[1]} {lost[2]}"
        if len(lost) > 8 and lost[8]:           # 拼接图片识别出的外观描述
            lost_text += f" 图片特征：{lost[8]}"
        lost_text += f" 丢失地点：{lost[3]}"
        vec_lost = get_embedding(lost_text)
        for found in found_list:
            found_text = f"{found[1]} {found[2]}"
            if len(found) > 8 and found[8]:     # 拼接图片识别出的外观描述
                found_text += f" 图片特征：{found[8]}"
            found_text += f" 捡拾地点：{found[3]}"
            vec_found = get_embedding(found_text)   # 重复文本会命中缓存，不会重复调接口
            score = cosine_similarity(vec_lost, vec_found)
            if score >= threshold:
                result.append({
                    "lost": lost,
                    "found": found,
                    "score": round(float(score), 3)
                })
    # 按分数从高到低排序
    result.sort(key=lambda x: x["score"], reverse=True)
    return result


if __name__ == "__main__":
    # 简单测试：配置了 Key 才会真正调用接口
    t1 = "黑色折叠雨伞，图书馆三楼丢失"
    t2 = "黑折伞，图书馆捡到"
    v1 = get_embedding(t1)
    v2 = get_embedding(t2)
    s = cosine_similarity(v1, v2)
    print(f"相似度分数：{s}")
