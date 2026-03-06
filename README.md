# [cite_start]AI 助教平台 (AI Teaching Platform) [cite: 1]

[cite_start]這是一套整合生成式 AI 與雲端原生架構的智能教學輔助系統 [cite: 1, 2][cite_start]。系統採用多模態 AI 技術處理文字與圖片提問 [cite: 47][cite_start]，並具備完整的後台數據追蹤機制，落實數據驅動管理 [cite: 109, 110]。

## 🔗 Live Demo
* **系統展示：** [點此前往 AI 助教平台](https://ai-accounting-assistant-352853111485.asia-northeast1.run.app/)

## 🏗️ 系統架構總覽 (Architecture)
[cite_start]本系統採用雲端原生 (Cloud-Native) 架構，包含四大核心層 [cite: 4]：
* [cite_start]**🌐 前端介面層 (Frontend)：** 採用 Streamlit 原生多頁面架構 [cite: 22, 36][cite_start]。以 `Home.py` 作為路由中樞進行導航派發 [cite: 23]。
* [cite_start]**☁️ 雲端運算層 (Cloud Computing)：** 部署於 GCP Cloud Run [cite: 14][cite_start]。具備自動水平擴展、零閒置計費的 Serverless 容器化執行環境，確保高峰期自動擴容 [cite: 14, 38, 39, 106]。
* [cite_start]**🧠 AI 引擎層 (AI Engine)：** 整合 Vertex AI 託管的 Gemini 模型 [cite: 45, 46, 94][cite_start]。支援文字與圖片多模態處理，並提供串流回覆 (Streaming) 與模型容錯備援機制 [cite: 47, 48, 49]。
* [cite_start]**🗄️ 資料庫層 (Database)：** 採用 Cloud Firestore (原生模式) [cite: 51, 52][cite_start]。即時儲存解題紀錄與滿意度等數據 [cite: 53, 54, 57]。

## ✨ 核心功能模組 (Core Features)
[cite_start]系統透過多頁面路由，提供不同角色的專屬功能 [cite: 88]：
* [cite_start]**🏠 Dashboard (總覽首頁)：** 系統概況總覽與首頁入口 [cite: 24, 26]。
* [cite_start]**👨‍🏫 AISolver (資訊助教)：** 處理資訊類問題，支援提問、圖片上傳與人工審核 [cite: 27, 29]。
* [cite_start]**🧾 Accounting (會計助教)：** 針對會計科目設計專屬的提示詞 (Prompt) [cite: 30, 32, 50]。
* [cite_start]**📊 Analytics (數據後台)：** 產出互動式圖表，追蹤使用者滿意度與使用趨勢 [cite: 33, 35, 110]。

## 🔄 系統資料流程 (Workflow)
[cite_start]一次完整的 AI 解題流程如下 [cite: 59]：
1. [cite_start]**使用者提問：** 使用者 (學生/助教) 輸入文字或上傳圖片 [cite: 61, 62, 63]。
2. [cite_start]**前端接收：** Streamlit 接收請求，並路由至對應的助教頁面 [cite: 67, 68]。
3. [cite_start]**雲端處理：** Cloud Run 執行 Python 邏輯與業務流程 [cite: 72, 73]。
4. [cite_start]**AI 推論：** Vertex AI 呼叫 Gemini 模型推論，並以串流生成回覆 [cite: 77, 78]。
5. [cite_start]**審核與儲存：** 教師確認最終答案後，將資料寫入 Firestore，供 Analytics 後台讀取與產出報表 [cite: 82, 83, 84]。

## 🛠️ 技術棧總覽 (Tech Stack)
* [cite_start]**Frontend:** Streamlit (Python 原生網頁框架) [cite: 86, 87, 88]
* [cite_start]**Cloud Platform:** Google Cloud Platform (GCP) [cite: 89, 90]
* [cite_start]**Compute:** Cloud Run (Docker 容器化, Serverless 無伺服器) [cite: 91, 100]
* [cite_start]**AI Model:** Vertex AI / Gemini 模型 [cite: 92, 93, 94]
* [cite_start]**Database:** Firestore (原生 NoSQL 模式) [cite: 95, 96, 97]
* [cite_start]**Security & Auth:** IAM 最小權限與 GCP 服務帳號 (Service Account) 資源統一存取 [cite: 101, 102, 103, 111, 112]

---
## 💻 本地端運行指南 (Local Setup)
1. Clone 此專案：`git clone https://github.com/b827262-cell/AI_RAG_001.git`
2. 安裝相依套件：`pip install -r requirements.txt`
3. 執行應用程式：`streamlit run Home.py`
