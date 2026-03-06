import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
# 🚀 引入 Firestore 雲端資料庫套件
from google.cloud import firestore

# ==========================================
# 1. 樣式與導覽組件 (副程式化)
# ==========================================
def inject_custom_css():
    """集中管理所有響應式與介面優化 CSS"""
    st.markdown("""
    <style>
        /* 1. 隱藏右上角選單列 */
        header[data-testid="stHeader"] { visibility: hidden; height: 0%; }
        
        /* 2. 強制解除固定寬度，改為全螢幕寬度 (完美模擬 layout="wide") */
        .block-container {
            max-width: 95% !important;
            padding-top: 1.0rem; 
        }
        
        /* 3. 當螢幕寬度小於 768px 時的響應式優化 */
        @media (max-width: 768px) {
            h1 { font-size: 2.0em !important; }
            .block-container { max-width: 100% !important; padding: 0.5rem; }
            [data-testid="stMetricValue"] { font-size: 1.8rem !important; }
        }
    </style>
    """, unsafe_allow_html=True)

def render_back_navigation():
    """渲染頂部導覽列：返回主選單按鈕"""
    nav_container = st.container()
    col_nav, _ = nav_container.columns([1, 5])
    with col_nav:
        # 🚀 修正點：取消連結至 Home.py，改為連結至實體內容頁面 pages/0-Dashboard.py
        # 這樣可以避免觸發入口文件的 pg.run() 導致的 RecursionError
        st.page_link("pages/0-Dashboard.py", label="返回主選單", icon="⬅️")
    nav_container.markdown("---")

# ⚡ 執行介面優化與返回導覽
inject_custom_css()
render_back_navigation()

# ==========================================
# 2. 全域常數與標題
# ==========================================
SATISFIED_EMOJI, UNSATISFIED_EMOJI = "👍", "👎"
SATISFIED_LABEL = f"{SATISFIED_EMOJI} 滿意"
UNSATISFIED_LABEL = f"{UNSATISFIED_EMOJI} 不滿意"

st.title("📊 後台數據總覽 (雲端即時版)")

# ==========================================
# 3. 資料庫連線與讀取
# ==========================================
@st.cache_resource
def get_firestore_client():
    """初始化 Firestore 連線"""
    try:
        load_dotenv()
        project_id = os.getenv("PROJECT_ID") or os.getenv("GOOGLE_CLOUD_PROJECT")
        return firestore.Client(project=project_id)
    except Exception as e:
        st.error(f"Firestore 初始化失敗: {e}")
        st.stop()

db = get_firestore_client()

@st.cache_data(ttl=30)
def load_data_from_firestore():
    """從雲端抓取所有解答紀錄"""
    try:
        # 依照時間排序抓取資料
        docs = db.collection('solutions').order_by('timestamp', direction=firestore.Query.DESCENDING).stream()
        data = [dict(doc.to_dict(), doc_id=doc.id) for doc in docs]
        
        if not data: return pd.DataFrame()
        
        df = pd.DataFrame(data)
        # 轉換時間格式以利顯示
        df['timestamp'] = pd.to_datetime(df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
        return df
    except Exception as e:
        st.error(f"雲端讀取錯誤：{e}")
        return pd.DataFrame()

# ==========================================
# 4. UI 渲染組件
# ==========================================
def render_metrics_and_chart(df):
    """渲染核心指標與滿意度圖表"""
    total = len(df)
    if total == 0:
        st.info("符合篩選條件的資料不足，無法顯示指標。")
        return

    satisfied = (df['satisfaction'] == SATISFIED_EMOJI).sum()
    rate = (satisfied / total) * 100

    st.subheader("🎯 核心指標")
    c1, c2 = st.columns(2)
    c1.metric("總解題數", f"{total} 題")
    c2.metric("使用者滿意度", f"{rate:.1f}%", f"{satisfied} / {total} 👍")

    st.subheader("📈 滿意度分佈")
    chart_data = pd.DataFrame({'數量': [satisfied, total - satisfied]}, index=[SATISFIED_LABEL, UNSATISFIED_LABEL])
    st.bar_chart(chart_data, y='數量')

# ==========================================
# 5. 執行主流程
# ==========================================
df_raw = load_data_from_firestore()

if not df_raw.empty:
    # 渲染視覺化指標與圖表
    render_metrics_and_chart(df_raw)
    
    # 顯示詳細資料表格
    st.subheader("📋 詳細問答紀錄")
    st.dataframe(
        df_raw[['timestamp', 'subject', 'teacher_name', 'question', 'final_answer', 'satisfaction']], 
        use_container_width=True
    )
else:
    st.info("☁️ 目前雲端資料庫尚無任何紀錄。")