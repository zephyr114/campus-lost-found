# 🎓 校园 AI 失物招领智能匹配系统

基于 **Streamlit + SQLite + 智谱 AI Embedding** 的校园失物招领语义匹配演示项目。
用户登记失物/拾物信息后，系统自动用文本向量计算相似度，把语义相近的失主与拾物记录智能配对。

## ✨ 功能

- 📥 失物登记 / 📤 拾物登记（物品名、描述、地点、时间、联系方式）
- 🤖 AI 语义匹配：基于智谱 `embedding-2` 向量 + 余弦相似度，支持阈值调节
- 🗑️ 记录撤回（带二次确认）
- 💾 SQLite 本地数据库，零配置启动

## 🛠 技术栈

| 模块 | 技术 |
|---|---|
| 网页界面 | Streamlit |
| 数据库 | SQLite（Python 内置） |
| 向量模型 | 智谱 AI Embedding-2 |
| 相似度 | NumPy 余弦相似度 |

## 🚀 本地运行

1. 安装依赖（Python 3.8+）：

```bash
pip install streamlit zhipuai numpy
```

2. 复制配置模板并填入你的智谱 API Key（[智谱开放平台](https://open.bigmodel.cn) 免费获取）：

```bash
cp config.example.py config.py
# 编辑 config.py，填入你的 API_KEY
```

3. 启动：

```bash
streamlit run app.py
```

浏览器自动打开 http://localhost:8501 即可使用。

## 📁 项目结构

```
├── app.py              # Streamlit 网页主程序
├── database.py         # SQLite 建表、增删查
├── matching.py         # 智谱 Embedding 向量 + 余弦相似度匹配
├── config.example.py   # API Key 配置模板
└── config.py           # 本地配置（已被 .gitignore 排除，勿提交）
```

## 🧪 测试用例

| 失物 | 拾物 |
|---|---|
| 黑色折叠雨伞 / 黑颜色折叠雨伞，伞柄白色 / 图书馆三楼 | 黑折伞 / 黑色折叠雨伞，白色手柄 / 图书馆 |

两组描述的向量相似度约 **0.85**，超过 0.7 阈值即可被匹配成功。
