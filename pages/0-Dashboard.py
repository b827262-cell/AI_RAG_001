import streamlit as st

# 1. 樣式注入
st.markdown("""
<style>
    header[data-testid="stHeader"] { visibility: hidden; height: 0%; }
    .block-container { padding-top: 2rem; }
</style>
""", unsafe_allow_html=True)

# 2. 儀表板內容
st.title("🤖 AI 助教工具平台", anchor=False)
st.subheader('您最可靠的解題與備考領航導師！')

st.image("https://images.unsplash.com/photo-1516321318423-f06f85e504b3?q=80&w=800&auto=format&fit=crop", use_container_width=True)

# 🚀 三大入口連結
st.markdown("### 🚀 進入系統專區")
c1, c2, c3 = st.columns(3)
c1.page_link("pages/2-AISolver.py", label="👨‍🏫 資訊類科助教",  use_container_width=True)
c2.page_link("pages/3-AccountingSolver.py", label="🧾 會計學 AI 助教",  use_container_width=True)
c3.page_link("pages/1-AnalyticsOverview.py", label="📊 後台數據管理",  use_container_width=True)