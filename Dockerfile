# 使用輕量級的 Python 3.11 作為基礎環境
FROM python:3.11-slim

# 設定工作目錄
WORKDIR /app

# 將套件清單複製進去並安裝
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 將你寫好的所有程式碼（包含 pages 資料夾）複製進去
COPY . ./

# Cloud Run 會動態分配 Port，我們要讓 Streamlit 去聽那個 Port
CMD streamlit run Home.py --server.port=${PORT:-8080} --server.address=0.0.0.0