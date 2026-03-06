import streamlit as st
import os
from datetime import datetime
from dotenv import load_dotenv
from PIL import Image
from google import genai
from google.cloud import firestore

# ==========================================
# 1. 樣式與導覽副程式 (優化全寬與返回邏輯)
# ==========================================
def inject_custom_css():
    """集中管理所有響應式與全寬介面優化 CSS"""
    st.markdown("""
    <style>
        /* 1. 隱藏右上角選單列 */
        header[data-testid="stHeader"] { visibility: hidden; height: 0%; }
        
        /* 🚀 2. 強制解除固定寬度，改為全螢幕寬度 (完美模擬 layout="wide") */
        .block-container {
            max-width: 95% !important;
            padding-top: 1.5rem;
            padding-bottom: 1rem;
        }
        
        /* 3. 當螢幕寬度小於 768px (平板與手機) 時的響應式優化 */
        @media (max-width: 768px) {
            h1 { font-size: 2.0em !important; }
            h2, h3, .stSubheader { font-size: 1.3em !important; }
            .block-container { max-width: 100% !important; padding: 1rem; }
        }
    </style>
    """, unsafe_allow_html=True)

def render_top_navigation():
    """渲染頂部導覽列：返回主選單按鈕"""
    # 使用較窄的欄位放置返回鍵
    col_nav, _ = st.columns([1, 5])
    with col_nav:
        # 🚀 關鍵修正：取消連結 Home.py (避免遞迴)，改為連結實體內容頁面 0-Dashboard.py
        # 標籤改為「返回主選單」更符合操作邏輯
        st.page_link("pages/0-Dashboard.py", label="返回主選單", icon="⬅️")
    st.markdown("---")

# 執行樣式注入與導覽渲染
inject_custom_css()
render_top_navigation()

# 🌟 載入提示：在連線初始化前給予使用者反饋
loading_placeholder = st.empty()
loading_placeholder.info("⏳ 正在建立與雲端 AI 引擎及資料庫的加密連線，請稍候...")

# ==========================================
# 2. AI 與 Firestore 資料庫初始化函式
# ==========================================
@st.cache_resource
def init_ai_clients():
    load_dotenv()
    project_id = os.getenv("PROJECT_ID") or os.getenv("GOOGLE_CLOUD_PROJECT")
    location = os.getenv("GOOGLE_CLOUD_LOCATION", "global")
    api_key = os.getenv("GEMINI_API_KEY")
    
    try:
        if project_id:
            return genai.Client(vertexai=True, project=project_id, location=location)
        elif api_key:
            return genai.Client(api_key=api_key)
        else:
            raise ValueError("找不到 GEMINI_API_KEY 或 PROJECT_ID！")
    except Exception as e:
        st.error(f"AI Client 初始化失敗: {e}")
        st.stop()

ai_client = init_ai_clients()

try:
    load_dotenv()
    project_id = os.getenv("PROJECT_ID") or os.getenv("GOOGLE_CLOUD_PROJECT")
    db = firestore.Client(project=project_id)
except Exception as e:
    st.error(f"Firestore 初始化失敗: {e}")
    st.stop()

# 🌟 初始化完成，清空載入提示
loading_placeholder.empty()

# ==========================================
# 3. 常數定義與核心邏輯 (會計學專用)
# ==========================================
MODEL_NAMES = ["gemini-3-flash-preview", "gemini-3.0-flash", "gemini-2.5-flash", "gemini-1.5-flash-002"]
SATISFIED_EMOJI, UNSATISFIED_EMOJI = "👍", "👎"

SYSTEM_INSTRUCTION = """
你現在是本教育集團最頂尖的會計類科資深助教。
你的任務是輔助解題，撰寫解答草稿給題庫部主管審核。
請依照以下格式輸出：
1. 【學員盲點分析】：簡述學員可能卡關的會計觀念或準則。
2. 【詳細解答/計算過程】：給出正確答案與詳細步驟 (分錄、計算式等)。
3. 【延伸考點提醒】：補充一個相關的考試重點。
語氣必須專業、嚴謹。
"""

def get_teacher_history(teacher_name: str) -> list:
    if not teacher_name.strip(): return []
    try:
        docs = db.collection('solutions') \
                 .where('teacher_name', '==', teacher_name.strip()) \
                 .where('satisfaction', '==', SATISFIED_EMOJI) \
                 .stream()
        results = [doc.to_dict() for doc in docs]
        results.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        return [(r.get('question', ''), r.get('final_answer', '')) for r in results[:20]]
    except Exception as e:
        return []

def build_prompt(question: str, history: list) -> str:
    prompt = SYSTEM_INSTRUCTION
    if history:
        prompt += "\n\n【參考資料：該老師過去的優良解答範例】\n"
        for idx, (q, a) in enumerate(history):
            prompt += f"\n<歷史題目 {idx+1}>\n{q}\n</歷史題目 {idx+1}>\n<歷史解答 {idx+1}>\n{a}\n</歷史解答 {idx+1}>\n"
    prompt += f"\n\n<學員問題>\n{question}\n</學員問題>"
    return prompt

def generate_content_with_fallback(prompt_parts):
    error_logs = [] 
    for model_name in MODEL_NAMES:
        try:
            response_stream = ai_client.models.generate_content_stream(model=model_name, contents=prompt_parts)
            iterator = iter(response_stream)
            first_chunk = next(iterator)
            def stream_generator():
                yield first_chunk
                yield from iterator
            return stream_generator(), model_name
        except Exception as e:
            error_logs.append(f"❌ {model_name} 失敗: {str(e)}")
            continue 
    raise RuntimeError("所有模型皆無法使用。\n" + "\n".join(error_logs))

def save_solution_to_db(question: str, answer: str, satisfaction: str, subject: str, teacher_name: str):
    try:
        db.collection('solutions').document().set({
            'timestamp': datetime.now().isoformat(),
            'question': question,
            'final_answer': answer,
            'satisfaction': satisfaction,
            'subject': subject,
            'teacher_name': teacher_name.strip()
        })
    except Exception as e:
        st.error(f"儲存失敗 ({e})")

# ==========================================
# 4. 介面與流程控制
# ==========================================
def initialize_session_state(): 
    for key, val in {"draft_content": "", "question_content": "", "last_question": "", "teacher_name": ""}.items():
        if key not in st.session_state: st.session_state[key] = val

def trigger_ai_generation():
    with st.spinner('🧠 AI 會計助教正在編譯與思考中...'):
        try:
            current_teacher = st.session_state.teacher_name
            history = get_teacher_history(current_teacher)
            prompt_parts = [build_prompt(st.session_state.question_content, history)]
            
            if st.session_state.get("uploaded_files"):
                for f in st.session_state.uploaded_files:
                    prompt_parts.append(Image.open(f))
            
            stream, used_model = generate_content_with_fallback(prompt_parts)

            if stream:
                st.session_state.last_question = st.session_state.question_content
                container = st.empty()
                full_text = ""
                for chunk in stream:
                    if chunk.text:
                        full_text += chunk.text
                        container.markdown(full_text + " ▌")
                st.session_state.draft_content = full_text
                st.toast(f"✅ 已使用 {used_model} 生成", icon="🎉")
                container.empty()
                st.rerun()
        except Exception as e:
            st.error(str(e))

def main():
    st.title("🧾 會計類科 AI 解題輔助系統")
    initialize_session_state()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📥 學員提問區")
        st.text_input("👨‍🏫 老師名稱：", key="teacher_name", placeholder="例如：王小明")
        st.text_area("請貼上會計問題內容：", height=200, key="question_content")
        st.file_uploader("上傳題目圖片", type=["png", "jpg", "jpeg"], accept_multiple_files=True, key="uploaded_files")
        
        if st.session_state.get("uploaded_files"):
            st.write("已上傳圖片預覽：")
            p_cols = st.columns(4) 
            for i, f in enumerate(st.session_state.uploaded_files):
                with p_cols[i % 4]: st.image(f, use_container_width=True) #

        is_same = (st.session_state.question_content == st.session_state.last_question)
        if st.button("🚀 呼叫 AI 助教生成草稿", type="primary", disabled=is_same and bool(st.session_state.draft_content)):
            if not st.session_state.question_content.strip(): st.warning("請先輸入內容！")
            else: trigger_ai_generation()

    with col2:
        st.subheader("📝 AI 草稿與助教審核區")
        st.text_area("助教可直接修改 AI 草稿：", height=400, key="draft_content")
        st.markdown("---")
        st.write("請對解答品質進行評分：")
        
        b1, b2, _ = st.columns([1,1,4])
        if b1.button(f"{SATISFIED_EMOJI} 滿意"):
            save_solution_to_db(st.session_state.last_question, st.session_state.draft_content, SATISFIED_EMOJI, "會計學", st.session_state.teacher_name)
            st.toast("已送出滿意評價並存入歷史紀錄", icon="🎉")
            for k in ["draft_content", "question_content", "last_question", "uploaded_files"]: st.session_state.pop(k, None)
            st.rerun()
        if b2.button(f"{UNSATISFIED_EMOJI} 不滿意"):
            save_solution_to_db(st.session_state.last_question, st.session_state.draft_content, UNSATISFIED_EMOJI, "會計學", st.session_state.teacher_name)
            st.toast("回饋已紀錄", icon="⚠️")
            for k in ["draft_content", "question_content", "last_question", "uploaded_files"]: st.session_state.pop(k, None)
            st.rerun()

if __name__ == "__main__":
    main()