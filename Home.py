import streamlit as st

# ==========================================
# 0. 全域頁面配置 (必須在最上方)
# ==========================================
st.set_page_config(
    page_title="AI 智能解題輔助系統",
    page_icon="💡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 1. 導覽系統定義 (路由表)
# ==========================================
# 🚀 關鍵：將原本的首頁內容移至 pages/0-Dashboard.py
# 這樣 Home.py 就不會再呼叫自己，解決 RecursionError
pg = st.navigation([
    st.Page("pages/0-Dashboard.py", title="首頁", icon="🏠", default=True),
    st.Page("pages/1-AnalyticsOverview.py", title="後台數據總覽", icon="📊"),
    st.Page("pages/2-AISolver.py", title="資訊類科助教", icon="👨‍🏫"),
    st.Page("pages/3-AccountingSolver.py", title="會計學 AI 助教", icon="🧾")
])

pg.run()