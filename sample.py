import streamlit as st
import pandas as pd
import time
import ssl

# ---------------------------------------------------------
# 🔧 設定・SSL回避
# ---------------------------------------------------------
ssl._create_default_https_context = ssl._create_unverified_context
SHEET_ID = "12xX_33yEzUFTOI6XFFrfsno446o_UbLWx9iKq6QWxn4"

# ---------------------------------------------------------
# 🎭 キャラクター設定
# ---------------------------------------------------------
CHARACTERS = {
    "tanuki": {
        "name": "しがラッキー",
        "icon": "🦝",
        "desc": "【親しみやすさNo.1】\n信楽焼のタヌキ。商売繁盛を関西弁で応援するで！",
        "first_msg": "まいど！商売繁盛させよな！\nあんたにぴったりの補助金、一緒に探したるで〜！🦝"
    },
    "akindo": {
        "name": "近江商人コンシェル",
        "icon": "🧑‍💼",
        "desc": "【信頼感重視】\n三方よしの精神で、堅実な事業計画をサポートします。",
        "first_msg": "こんにちは。近江商人の精神で、\n貴社の事業発展に役立つ補助金をご提案いたします。🧑‍💼"
    },
    "robot": {
        "name": "ビワ湖ボット",
        "icon": "🤖",
        "desc": "【効率重視】\n最新データベースから、条件に合うものを最速で検索。",
        "first_msg": "起動しました。\n条件に合致する補助金をスキャンします。質問に答えてください。🤖"
    }
}

# ---------------------------------------------------------
# 🎨 0. デザインカスタマイズ
# ---------------------------------------------------------
def apply_custom_style():
    st.markdown("""
    <style>
        /* Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=M+PLUS+Rounded+1c:wght@300;400;500;700;800&display=swap');

        /* フォント適用 */
        html, body, [class*="st-"], h1, h2, h3, h4, h5, h6, .stButton, button, input, textarea, div, p, span, a {
            font-family: 'M PLUS Rounded 1c', sans-serif !important;
        }

        /* 1. 全体の背景色 */
        .stApp {
            background-color: #FCE9D7;
        }
        
        /* 2. ヘッダーエリア */
        .header-container {
            background-color: #FCE9D7;
            padding: 20px 10px;
            margin-bottom: 20px;
            border-bottom: 2px solid #FFFFFF;
            text-align: center;
        }
        .header-title {
            color: #57606f;
            font-weight: 800;
            font-size: 1.3rem;
            margin: 0;
            display: inline-block;
        }

        /* 3. ボタンのデザイン */
        .stButton button {
            width: 100%;
            border-radius: 50px;
            background-color: #FFFFFF;
            border: 2px solid #FFFFFF;
            color: #57606f;
            padding: 10px 0px;
            font-weight: 700;
            font-size: 0.95rem;
            box-shadow: 0 4px 0px rgba(0,0,0,0.05);
            transition: all 0.1s;
        }
        .stButton button:hover {
            background-color: #FFF5EB;
            color: #FF9F43;
            transform: translateY(-2px);
            box-shadow: 0 6px 0px rgba(0,0,0,0.05);
        }
        .stButton button:active {
            transform: translateY(2px);
            box-shadow: 0 2px 0px rgba(0,0,0,0.05);
        }

        /* キャラ選択カードのデザイン */
        .char-card {
            background: white;
            padding: 15px;
            border-radius: 15px;
            text-align: center;
            border: 2px solid #fff;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            height: 100%;
        }
        .char-icon { font-size: 40px; display: block; margin-bottom: 10px; }
        .char-name { font-weight: 800; color: #FF9F43; font-size: 1.1em; margin-bottom: 5px; display:block;}
        .char-desc { font-size: 0.8em; color: #7f8c8d; line-height: 1.4; display:block; height: 60px;}
        
    </style>
    """, unsafe_allow_html=True)

# 💬 メッセージ表示関数（動的アイコン対応）
def display_chat_message(role, text, icon, is_card=False):
    if role == "assistant" or role == "result":
        # AI（左側）
        bubble_style = "background: #FFFFFF; padding: 15px 20px; border-radius: 20px 20px 20px 0px; border: 2px solid #FFFFFF;"
        if is_card:
            bubble_style = "background: #FFFFFF; padding: 20px; border-radius: 20px; border: 2px solid #FFFFFF; width: 100%;"

        st.markdown(f"""
        <div style="display: flex; align-items: flex-end; margin-bottom: 24px;">
            <div style="background:#FFFFFF; min-width:45px; height:45px; border-radius:50%; display:flex; justify-content:center; align-items:center; margin-right: 10px; border: 2px solid #FFFFFF; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
                <span style="font-size: 26px;">{icon}</span>
            </div>
            <div style="{bubble_style} box-shadow: 0 4px 10px rgba(0,0,0,0.03); color: #57606f; line-height: 1.6; font-weight: 500;">
                {text}
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # ユーザー（右側）
        st.markdown(f"""
        <div style="display: flex; align-items: flex-end; justify-content: flex-end; margin-bottom: 24px;">
            <div style="background: #FF9F43; padding: 12px 20px; border-radius: 20px 20px 0px 20px; margin-right: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); color: #FFFFFF; line-height: 1.6; font-weight: bold;">
                {text}
            </div>
            <div style="background:#FFFFFF; min-width:40px; height:40px; border-radius:50%; display:flex; justify-content:center; align-items:center;">
                <span style="font-size: 22px;">😊</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 1. データ読み込み関数
# ---------------------------------------------------------
@st.cache_data(ttl=600)
def load_data():
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"
    try:
        df = pd.read_csv(url)
        df = df.fillna("")
        def split_text(text):
            if not text: return []
            text = text.replace("、", ",")
            return [t.strip() for t in text.split(",")]
        df["tags_list"] = df["tags"].apply(split_text)
        df["industries_list"] = df["target_industries"].apply(split_text)
        return df.to_dict("records")
    except Exception as e:
        return []

# ---------------------------------------------------------
# 2. 質問シナリオ
# ---------------------------------------------------------
SCENARIO = [
    {"key": "area", "question": "Q1. お店や事務所はどこにある？", "options": ["草津市", "大津市", "長浜市", "その他（県内）"]},
    {"key": "type", "question": "Q2. 働き方はどれに近い？", "options": ["法人", "個人事業主", "これから創業"]},
    {"key": "industry", "question": "Q3. お仕事のジャンルは？", "options": ["建設・建築", "製造", "飲食・小売", "サービス・宿泊", "医療・福祉", "IT・その他"]},
    {"key": "emp_count", "question": "Q4. スタッフの人数は？", "options": ["0名（ひとり）", "5名以下", "20名以下", "21名以上"]},
    {"key": "need", "question": "Q5. 何に使いたい？", "options": ["売上アップ（広告・販路）", "業務効率化（IT・PC）", "店舗・設備投資", "新事業・創業"]},
    {"key": "budget", "question": "Q6. 予算はどれくらい？", "options": ["50万円未満", "50万〜300万円", "300万〜1000万円", "1000万円以上"]}
]

# ---------------------------------------------------------
# 3. メイン処理
# ---------------------------------------------------------
st.set_page_config(page_title="滋賀県補助金診断", page_icon="🍊", layout="wide")
apply_custom_style()

col1, col2, col3 = st.columns([1, 2, 1]) 

with col2:
    # --- ヘッダーエリア ---
    with st.container():
        st.markdown("""
        <div class="header-container">
            <span class="header-title">チャットボット総合案内</span>
        </div>
        """, unsafe_allow_html=True)

    # --- メインコンテンツ ---
    subsidies_db = load_data()

    # セッション状態の初期化
    if "step" not in st.session_state:
        st.session_state.step = 0
        st.session_state.answers = {}
        st.session_state.chat_history = []
        st.session_state.selected_char = None # まだキャラを選んでいない

    # 🎭 0. キャラ選択画面（まだ選んでいない場合）
    if st.session_state.selected_char is None:
        st.markdown("<h4 style='text-align:center; color:#57606f; margin-bottom:20px;'>担当者を選んでスタート！</h4>", unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns(3)
        
        # タヌキ
        with c1:
            st.markdown(f"""
            <div class="char-card">
                <span class="char-icon">{CHARACTERS['tanuki']['icon']}</span>
                <span class="char-name">{CHARACTERS['tanuki']['name']}</span>
                <span class="char-desc">{CHARACTERS['tanuki']['desc']}</span>
            </div>
            """, unsafe_allow_html=True)
            if st.button("この人にする", key="btn_tanuki"):
                st.session_state.selected_char = "tanuki"
                st.session_state.chat_history.append({"role": "assistant", "content": CHARACTERS["tanuki"]["first_msg"]})
                st.rerun()

        # 近江商人
        with c2:
            st.markdown(f"""
            <div class="char-card">
                <span class="char-icon">{CHARACTERS['akindo']['icon']}</span>
                <span class="char-name">{CHARACTERS['akindo']['name']}</span>
                <span class="char-desc">{CHARACTERS['akindo']['desc']}</span>
            </div>
            """, unsafe_allow_html=True)
            if st.button("この人にする", key="btn_akindo"):
                st.session_state.selected_char = "akindo"
                st.session_state.chat_history.append({"role": "assistant", "content": CHARACTERS["akindo"]["first_msg"]})
                st.rerun()

        # ロボット
        with c3:
            st.markdown(f"""
            <div class="char-card">
                <span class="char-icon">{CHARACTERS['robot']['icon']}</span>
                <span class="char-name">{CHARACTERS['robot']['name']}</span>
                <span class="char-desc">{CHARACTERS['robot']['desc']}</span>
            </div>
            """, unsafe_allow_html=True)
            if st.button("この人にする", key="btn_robot"):
                st.session_state.selected_char = "robot"
                st.session_state.chat_history.append({"role": "assistant", "content": CHARACTERS["robot"]["first_msg"]})
                st.rerun()
        
        st.stop() # ここで処理を止める（チャット画面に行かせない）


    # 🗣 1. チャット画面（キャラ選択後）
    
    # 現在のキャラ情報を取得
    current_char = CHARACTERS[st.session_state.selected_char]
    char_icon = current_char["icon"]

    # 履歴の描画
    for msg in st.session_state.chat_history:
        if "card-container" in str(msg["content"]):
             st.markdown(msg["content"], unsafe_allow_html=True)
        else:
            # 選択したキャラのアイコンを渡す
            display_chat_message(msg["role"], msg["content"], char_icon)

    # 診断進行
    if st.session_state.step < len(SCENARIO):
        current_q = SCENARIO[st.session_state.step]
        last_msg = st.session_state.chat_history[-1]
        if last_msg["role"] != "assistant" or last_msg["content"] != current_q["question"]:
             display_chat_message("assistant", current_q["question"], char_icon)

        st.write("") 
        btn_cols = st.columns(2)
        for i, option in enumerate(current_q["options"]):
            if btn_cols[i % 2].button(option, key=f"btn_{st.session_state.step}_{i}", use_container_width=True):
                st.session_state.chat_history.append({"role": "assistant", "content": current_q["question"]})
                st.session_state.chat_history.append({"role": "user", "content": option})
                st.session_state.answers[current_q["key"]] = option
                st.session_state.step += 1
                st.rerun()

    # 結果表示
    else:
        if st.session_state.chat_history[-1]["role"] != "result":
            with st.spinner("診断中..."):
                time.sleep(1)
            
            u_area = st.session_state.answers.get("area")
            u_industry = st.session_state.answers.get("industry")
            u_need = st.session_state.answers.get("need")
            
            matched_results = []
            for sub in subsidies_db:
                is_match = True
                if "滋賀" not in sub["area"] and sub["area"] != u_area:
                    is_match = False
                if sub["industries_list"]:
                    if u_industry not in sub["industries_list"]:
                        is_match = False
                if u_need not in sub["tags_list"]:
                    is_match = False
                if is_match:
                    matched_results.append(sub)

            result_text = f"診断完了！\n**{len(matched_results)}件** の補助金が見つかったで！" # ここは共通メッセージ
            display_chat_message("assistant", result_text, char_icon)
            st.session_state.chat_history.append({"role": "result", "content": result_text})
            
            if matched_results:
                cards_html = ""
                for item in matched_results:
                    url_html = ""
                    if item.get('url') and str(item['url']).startswith('http'):
                        url_html = f'<div style="margin-top:15px; text-align:center;"><a href="{item["url"]}" target="_blank" class="custom-link-btn">公式サイトを見る 👉</a></div>'
                    
                    card_html = f"""
                    <div class="card-container" style="display: flex; align-items: flex-start; margin-bottom: 20px;">
                        <div style="background:#FFFFFF; min-width:40px; height:40px; border-radius:50%; display:flex; justify-content:center; align-items:center; margin-right: 10px; border: 2px solid #FF9F43;">
                            <span style="font-size: 26px;">{char_icon}</span>
                        </div>
                        <div style="background: #FFFFFF; padding: 20px; border-radius: 20px; border: 2px solid #F0F0F0; width: 100%; box-shadow: 0 4px 15px rgba(255, 159, 67, 0.1); color: #57606f;">
                            <h4 style="margin:0 0 10px 0; color:#FF9F43; font-weight:800; font-size:1.1em;">🌟 {item['name']}</h4>
                            <div style="font-size:0.9em; color:#747d8c; margin-bottom:15px; background:#FFF5EB; display:inline-block; padding:5px 10px; border-radius:10px; font-weight:bold;">
                                📍 {item['area']} | 💰 上限: {item['max_amount']}
                            </div>
                            <p style="margin:0; line-height:1.6;">{item.get('detail', '詳細なし')}</p>
                            {url_html}
                        </div>
                    </div>
                    """
                    st.markdown(card_html, unsafe_allow_html=True)
                    cards_html += card_html

                st.session_state.chat_history.append({"role": "result", "content": cards_html})
            else:
                fail_msg = "ごめんなさい💦 条件に合うものが見つかりませんでした。"
                display_chat_message("assistant", fail_msg, char_icon)
                st.session_state.chat_history.append({"role": "result", "content": fail_msg})

            st.write("")
            if st.button("🔄 もう一回やってみる（キャラ変更）", use_container_width=True):
                st.cache_data.clear()
                st.session_state.step = 0
                st.session_state.answers = {}
                st.session_state.chat_history = []
                st.session_state.selected_char = None # キャラ選択をリセット
                st.rerun()

    # ---------------------------------------------------------
    # 4. フッター
    # ---------------------------------------------------------
    st.write("")
    st.write("") 
    
    st.markdown("""
    <div style="text-align: center; margin-top: 40px; padding-top: 20px; border-top: 1px solid #FFFFFF; color: #57606f; font-size: 0.8em;">
        <p>© 2025 Shiga Subsidy Match AI. All Rights Reserved.</p>
        <p>
            <a href="#" style="color: #57606f; text-decoration: none; margin: 0 10px;">利用規約</a> | 
            <a href="#" style="color: #57606f; text-decoration: none; margin: 0 10px;">プライバシーポリシー</a> | 
            <a href="#" style="color: #57606f; text-decoration: none; margin: 0 10px;">運営会社</a>
        </p>
        <p style="font-size: 0.7em; color: #7f8c8d;">Powered by Streamlit</p>
    </div>
    """, unsafe_allow_html=True)