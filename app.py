import streamlit as st
import streamlit.components.v1 as components
import random
import re
import time
from gtts import gTTS
from io import BytesIO

# --- 0. 系統配置 ---
st.set_page_config(
    page_title="第 10 課(進階) - 捕魚 Mifoting", 
    page_icon="🚣", 
    layout="centered"
)

# --- 1. 資料庫 (海洋活動 第 10 課進階) ---
VOCAB_MAP = {
    "mararid": "常常", "talariyar": "去海邊", "mifoting": "捕魚",
    "ko": "主格", "mifotingay": "漁夫", "ano": "即使/如果",
    "tata'ata'ang": "越來越大", "fali": "風", "takarakaraw": "很高",
    "tapelik": "海浪", "caay": "不", "ka": "否定連接詞", "talaw": "害怕",
    "cangra": "他們", "kaeca": "不(強調)", "matomes": "裝滿",
    "tamina": "船", "nangra": "他們的", "to": "受格", "foting": "魚",
    "ato": "和", "'afar": "蝦"
}

VOCABULARY = [
    {"amis": "mifoting", "zh": "捕魚", "emoji": "🐟", "root": "foting", "root_zh": "魚", "type": "verb"},
    {"amis": "mifotingay", "zh": "漁夫", "emoji": "🎣", "root": "foting", "root_zh": "魚", "type": "noun"},
    {"amis": "mararid", "zh": "常常", "emoji": "🔄", "root": "rarid", "root_zh": "常", "type": "adv"},
    {"amis": "tata'ata'ang", "zh": "巨大/漸強", "emoji": "🌬️", "root": "ta'ang", "root_zh": "大", "type": "adj_red"},
    {"amis": "takarakaraw", "zh": "很高(浪)", "emoji": "🌊", "root": "karaw", "root_zh": "高", "type": "adj_red"},
    {"amis": "caay kaeca", "zh": "總是/必定", "emoji": "💯", "root": "caay/eca", "root_zh": "不/否", "type": "phrase"},
    {"amis": "matomes", "zh": "充滿", "emoji": "🈵", "root": "tomes", "root_zh": "滿", "type": "adj"},
    {"amis": "'afar", "zh": "蝦(小)", "emoji": "🦐", "root": "'afar", "root_zh": "蝦", "type": "noun"},
]

SENTENCES = [
    {
        "amis": "Mararid talariyar mifoting ko mifotingay.", 
        "zh": "捕魚的人常常去海邊捕魚。", 
        "note": """
        <br><b>Mararid</b>：常常 (頻率副詞)。
        <br><b>Mifoting-ay</b>：捕魚的人 (名詞化)。
        <br>連動結構：常常 -> 去海邊 -> 捕魚。"""
    },
    {
        "amis": "Ano tata'ata'ang ko fali.", 
        "zh": "即使風越來越大。", 
        "note": """
        <br><b>Tata'ata'ang</b>：非常大/越來越大。
        <br><b>疊字 (Reduplication)</b>：
        <br>Ta'ang (大) → Tata'ata'ang (巨大/連續的大)。"""
    },
    {
        "amis": "Takarakaraw ko tapelik.", 
        "zh": "海浪很高。", 
        "note": """
        <br><b>Takarakaraw</b>：非常高/層層疊疊的高。
        <br>Takaraw (高) 的疊字變化，形容海浪一波波。"""
    },
    {
        "amis": "Caay ka talaw cangra.", 
        "zh": "他們也不害怕。", 
        "note": """
        <br><b>Caay ka...</b>：不... (否定句)。
        <br><b>Talaw</b>：害怕。
        <br>展現阿美族漁夫的勇氣。"""
    },
    {
        "amis": "Caay kaeca matomes ko tamina nangra to foting ato 'afar.", 
        "zh": "他們的船總是裝滿了魚和蝦。", 
        "note": """
        <br><b>Caay kaeca</b>：總是/必定 (雙重否定=肯定)。
        <br>直譯：不會不裝滿。
        <br><b>Matomes</b>：充滿。"""
    }
]

STORY_DATA = [
    {"amis": "Mararid talariyar mifoting ko mifotingay.", "zh": "捕魚的人常常去海邊捕魚。"},
    {"amis": "Ano tata'ata'ang ko fali.", "zh": "即使風越來越大。"},
    {"amis": "Takarakaraw ko tapelik.", "zh": "海浪很高。"},
    {"amis": "Caay ka talaw cangra.", "zh": "他們也不害怕。"},
    {"amis": "Caay kaeca matomes ko tamina nangra.", "zh": "他們的船總是裝滿了魚獲。"}
]

# --- 2. 視覺系統 (CSS 注入 - 風格：深海軍藍與豐收金) ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Black+Ops+One&family=Noto+Sans+TC:wght@400;700&display=swap');

/* 全局背景：深海軍藍 */
.stApp { 
    background: linear-gradient(180deg, #0D47A1 0%, #1565C0 100%); 
    color: #FFD700; /* 豐收金 */
    font-family: 'Noto Sans TC', sans-serif; 
}

/* Tab 樣式：金屬質感 */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background-color: rgba(0,0,0,0.3);
    padding: 8px;
    border-radius: 5px;
    border: 1px solid #FFD700;
}
.stTabs [data-baseweb="tab"] {
    height: 45px;
    border-radius: 3px;
    background-color: transparent;
    color: #90CAF9;
    font-weight: 700;
    border: none !important;
}
.stTabs [aria-selected="true"] {
    background-color: #FFD700 !important;
    color: #0D47A1 !important;
    box-shadow: 0 0 10px #FFD700;
}

/* 按鈕樣式：金色榮耀 */
.stButton>button { 
    background: linear-gradient(180deg, #FFD700, #FFC107) !important; 
    color: #0D47A1 !important; 
    border: 2px solid #FFF !important; 
    border-radius: 50px !important; 
    font-size: 18px !important; 
    font-weight: 900 !important; 
    box-shadow: 0 4px 15px rgba(255, 215, 0, 0.4) !important;
    transition: all 0.2s ease !important;
    text-transform: uppercase;
}
.stButton>button:hover { 
    transform: scale(1.05);
    box-shadow: 0 6px 20px rgba(255, 215, 0, 0.6) !important;
}

/* 測驗卡片：深藍底金字 */
.quiz-card { 
    background: rgba(13, 71, 161, 0.9); 
    border: 2px solid #FFD700; 
    padding: 25px; 
    border-radius: 15px; 
    margin-bottom: 20px; 
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
    color: #FFFFFF;
    text-align: center;
}
.quiz-tag { 
    background: #FFD700; 
    color: #0D47A1; 
    padding: 5px 15px; 
    border-radius: 20px; 
    font-weight: 900; 
    font-size: 14px; 
    display: inline-block;
    margin-bottom: 15px;
    text-transform: uppercase;
}

/* 翻譯區塊：航海日誌風格 */
.zh-translation-block { 
    background: #FFF8E1; 
    border-left: 5px solid #FF6F00;
    border-radius: 5px;
    padding: 20px; 
    color: #3E2723; 
    font-size: 16px; 
    line-height: 1.8; 
    font-family: 'Noto Sans TC', serif; 
    box-shadow: inset 0 0 10px rgba(0,0,0,0.1);
}
</style>
""", unsafe_allow_html=True)

# --- 3. 核心技術：沙盒渲染引擎 (強化疊字顯示) ---
def get_html_card(item, type="word"):
    pt = "80px" if type == "full_amis_block" else "60px"
    mt = "-20px" if type == "full_amis_block" else "-10px" 
    
    # 根據單字類型決定樣式
    border_color = "#FFD700" 
    bg_color = "#1565C0"
    text_color = "#FFFFFF"
    
    if isinstance(item, dict) and item.get('type') == 'adj_red': # 疊字特別樣式
        border_color = "#FF5252" # 紅色強調疊字

    style_block = f"""<style>
        @import url('https://fonts.googleapis.com/css2?family=Black+Ops+One&family=Noto+Sans+TC:wght@400;700&display=swap');
        body {{ background-color: transparent; color: #FFFFFF; font-family: 'Noto Sans TC', sans-serif; margin: 0; padding: 10px; padding-top: {pt}; overflow-x: hidden; }}
        
        /* 互動單字 */
        .interactive-word {{ 
            position: relative; 
            display: inline-block; 
            border-bottom: 2px dashed #FFD700;
            cursor: pointer; 
            margin: 0 4px; 
            color: #90CAF9; 
            transition: 0.3s; 
            font-size: 20px; 
            font-weight: 700; 
            font-family: 'Black Ops One', sans-serif;
            letter-spacing: 1px;
        }}
        .interactive-word:hover {{ color: #FFD700; border-bottom-color: #FFD700; text-shadow: 0 0 10px #FFD700; }}
        
        /* Tooltip */
        .interactive-word .tooltip-text {{ 
            visibility: hidden; 
            min-width: 80px; 
            background-color: #FFD700; 
            color: #0D47A1; 
            text-align: center; 
            border-radius: 4px; 
            padding: 8px; 
            position: absolute; 
            z-index: 100; 
            bottom: 140%; 
            left: 50%; 
            transform: translateX(-50%); 
            opacity: 0; 
            transition: opacity 0.3s; 
            font-size: 14px; 
            white-space: nowrap; 
            box-shadow: 0 4px 10px rgba(0,0,0,0.5); 
            font-weight: bold;
        }}
        .interactive-word:hover .tooltip-text {{ visibility: visible; opacity: 1; }}
        
        /* 播放按鈕 */
        .play-btn-inline {{ background: #FFD700; border: none; color: #0D47A1; border-radius: 50%; width: 28px; height: 28px; cursor: pointer; margin-left: 8px; display: inline-flex; align-items: center; justify-content: center; font-size: 14px; transition: 0.3s; vertical-align: middle; }}
        .play-btn-inline:hover {{ background: #FFF; transform: scale(1.1); }}
        
        /* 單字卡 - 深藍金字 */
        .word-card-static {{ 
            background: #1565C0; 
            border-radius: 10px; 
            padding: 15px; 
            display: flex; 
            justify-content: space-between; 
            align-items: center; 
            margin-top: {mt}; 
            height: 100px; 
            box-sizing: border-box; 
            box-shadow: 0 5px 15px rgba(0,0,0,0.3); 
            border: 2px solid {border_color};
        }}
        .wc-root-tag {{ font-size: 12px; background: #0D47A1; color: #90CAF9; padding: 3px 8px; border-radius: 4px; font-weight: bold; margin-right: 5px; border: 1px solid #42A5F5; }}
        .wc-amis {{ color: #FFD700; font-size: 24px; font-weight: 700; margin: 2px 0; font-family: 'Black Ops One', sans-serif; letter-spacing: 1px; }}
        .wc-zh {{ color: #E3F2FD; font-size: 16px; font-weight: 500; }}
        
        .play-btn-large {{ background: #0D47A1; border: 2px solid #FFD700; color: #FFD700; border-radius: 50%; width: 42px; height: 42px; cursor: pointer; font-size: 20px; transition: 0.2s; }}
        .play-btn-large:hover {{ background: #FFD700; color: #0D47A1; }}
        
        .amis-full-block {{ line-height: 2.4; font-size: 18px; margin-top: {mt}; text-align: left; padding: 0 5px; }}
        .sentence-row {{ margin-bottom: 12px; display: block; border-bottom: 1px dashed #42A5F5; padding-bottom: 8px; }}
        .sentence-row:last-child {{ border-bottom: none; }}
    </style>
    <script>
        function speak(text) {{ window.speechSynthesis.cancel(); var msg = new SpeechSynthesisUtterance(); msg.text = text; msg.lang = 'id-ID'; msg.rate = 0.9; window.speechSynthesis.speak(msg); }}
    </script>"""

    header = f"<!DOCTYPE html><html><head>{style_block}</head><body>"
    body = ""
    
    if type == "word":
        v = item
        body = f"""<div class="word-card-static">
            <div>
                <div style="margin-bottom:5px;"><span class="wc-root-tag">ROOT: {v['root']}</span> <span style="font-size:12px; color:#BBDEFB;">({v['root_zh']})</span></div>
                <div class="wc-amis">{v['emoji']} {v['amis']}</div>
                <div class="wc-zh">{v['zh']}</div>
            </div>
            <button class="play-btn-large" onclick="speak('{v['amis'].replace("'", "\\'")}')">🔊</button>
        </div>"""

    elif type == "full_amis_block": 
        all_sentences_html = []
        for sentence_data in item:
            s_amis = sentence_data['amis']
            words = s_amis.split()
            parts = []
            for w in words:
                clean_word = re.sub(r"[^\w']", "", w).lower()
                translation = VOCAB_MAP.get(clean_word, "")
                js_word = clean_word.replace("'", "\\'") 
                
                if translation:
                    chunk = f'<span class="interactive-word" onclick="speak(\'{js_word}\')">{w}<span class="tooltip-text">{translation}</span></span>'
                else:
                    chunk = f'<span class="interactive-word" onclick="speak(\'{js_word}\')">{w}</span>'
                parts.append(chunk)
            
            full_amis_js = s_amis.replace("'", "\\'")
            sentence_html = f"""
            <div class="sentence-row">
                {' '.join(parts)}
                <button class="play-btn-inline" onclick="speak('{full_amis_js}')" title="播放此句">🔊</button>
            </div>
            """
            all_sentences_html.append(sentence_html)
            
        body = f"""<div class="amis-full-block">{''.join(all_sentences_html)}</div>"""
    
    elif type == "sentence": 
        s = item
        words = s['amis'].split()
        parts = []
        for w in words:
            clean_word = re.sub(r"[^\w']", "", w).lower()
            translation = VOCAB_MAP.get(clean_word, "")
            js_word = clean_word.replace("'", "\\'") 
            
            if translation:
                chunk = f'<span class="interactive-word" onclick="speak(\'{js_word}\')">{w}<span class="tooltip-text">{translation}</span></span>'
            else:
                chunk = f'<span class="interactive-word" onclick="speak(\'{js_word}\')">{w}</span>'
            parts.append(chunk)
            
        full_js = s['amis'].replace("'", "\\'")
        body = f'<div style="font-size: 18px; line-height: 1.8; margin-top: {mt};">{" ".join(parts)}</div><button style="margin-top:10px; background:#FFD700; border:none; color:#0D47A1; padding:6px 15px; border-radius:4px; cursor:pointer; font-family:Black Ops One; font-weight:700; box-shadow: 0 2px 4px rgba(0,0,0,0.5);" onclick="speak(`{full_js}`)">▶ PLAY AUDIO</button>'

    return header + body + "</body></html>"

# --- 4. 測驗生成引擎 ---
def generate_quiz():
    questions = []
    
    # 1. 聽音辨義
    q1 = random.choice(VOCABULARY)
    q1_opts = [q1['amis']] + [v['amis'] for v in random.sample([x for x in VOCABULARY if x != q1], 2)]
    random.shuffle(q1_opts)
    questions.append({"type": "listen", "tag": "🎧 聽音辨義", "text": "請聽語音，選擇正確的單字", "audio": q1['amis'], "correct": q1['amis'], "options": q1_opts})
    
    # 2. 中翻阿
    q2 = random.choice(VOCABULARY)
    q2_opts = [q2['amis']] + [v['amis'] for v in random.sample([x for x in VOCABULARY if x != q2], 2)]
    random.shuffle(q2_opts)
    questions.append({"type": "trans", "tag": "🧩 中翻阿", "text": f"請選擇「<span style='color:#FFD700'>{q2['zh']}</span>」的阿美語", "correct": q2['amis'], "options": q2_opts})
    
    # 3. 語法題 (疊字)
    q3_data = {"text": "形容風「越來越大」要用哪個字？", "ans": "tata'ata'ang", "note": "Tata'ata'ang = 疊字表示程度加深"}
    questions.append({"type": "grammar", "tag": "🔥 疊字特訓", "text": f"{q3_data['text']}", "correct": "tata'ata'ang", "options": ["tata'ata'ang", "ta'ang", "tata'ang"], "note": q3_data['note']})

    # 4. 語法題 (雙重否定)
    q4_data = {"text": "Caay kaeca matomes. (意思是什麼？)", "ans": "總是裝滿", "note": "Caay kaeca = 總是/必定 (雙重否定)"}
    questions.append({"type": "grammar", "tag": "⚓ 雙重否定", "text": f"{q4_data['text']}", "correct": "總是裝滿", "options": ["總是裝滿", "沒有裝滿", "不常裝滿"], "note": q4_data['note']})

    # 5. 句型翻譯
    q6 = random.choice(STORY_DATA)
    q6_opts = [q6['amis']] + [s['amis'] for s in random.sample([x for x in STORY_DATA if x != q6], 2)]
    random.shuffle(q6_opts)
    questions.append({"type": "sent_trans", "tag": "📝 句型翻譯", "text": f"請選擇中文「<span style='color:#FFD700'>{q6['zh']}</span>」對應的阿美語", "correct": q6['amis'], "options": q6_opts})

    random.shuffle(questions)
    return questions[:5]

def play_audio_backend(text):
    try:
        tts = gTTS(text=text, lang='id'); fp = BytesIO(); tts.write_to_fp(fp); st.audio(fp, format='audio/mp3')
    except: pass

# --- 5. UI 呈現層 (使用 components.html 隔離渲染標題) ---
# 主題：深海軍藍與豐收金 (Navy Blue & Harvest Gold)
header_html = """
<!DOCTYPE html>
<html>
<head>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Black+Ops+One&family=Noto+Sans+TC:wght@700&display=swap');
        body { margin: 0; padding: 0; background-color: transparent; font-family: 'Noto Sans TC', sans-serif; text-align: center; }
        .container {
            background: rgba(0,0,0,0.2);
            border-radius: 15px;
            padding: 20px;
            color: #FFD700;
            border: 2px solid #FFD700;
            box-shadow: 0 0 20px rgba(255, 215, 0, 0.2);
        }
        h1 {
            font-family: 'Black Ops One', cursive;
            color: #FFD700;
            font-size: 48px;
            margin: 0 0 5px 0;
            text-shadow: 0 2px 5px #000;
            letter-spacing: 2px;
        }
        .subtitle {
            color: #90CAF9;
            background: #0D47A1;
            border-radius: 5px;
            padding: 5px 20px;
            display: inline-block;
            font-weight: bold;
            font-size: 16px;
            border: 1px solid #42A5F5;
        }
        .footer {
            margin-top: 10px;
            font-size: 12px;
            color: #BBDEFB;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Mifoting</h1>
        <div class="subtitle">第 10 課(進階)：捕魚 (勇氣與豐收)</div>
        <div class="footer">Theme: Navy Blue & Harvest Gold ⚓</div>
    </div>
</body>
</html>
"""

components.html(header_html, height=200)

tab1, tab2, tab3, tab4 = st.tabs([
    "🚣 勇者故事", 
    "🐟 核心單字", 
    "⚓ 語法解析", 
    "🏆 實戰測驗"
])

with tab1:
    st.markdown("### // 乘風破浪")
    st.caption("👆 點擊單字可聽發音並查看翻譯")
    
    # 使用深藍背景容器
    st.markdown("""<div style="background:#1565C0; padding:15px; border-radius:10px; border: 2px solid #42A5F5; box-shadow: 0 5px 15px rgba(0,0,0,0.3);">""", unsafe_allow_html=True)
    components.html(get_html_card(STORY_DATA, type="full_amis_block"), height=400, scrolling=True)
    st.markdown("</div>", unsafe_allow_html=True)

    zh_content = "<br>".join([item['zh'] for item in STORY_DATA])
    st.markdown(f"""
    <div class="zh-translation-block">
        {zh_content}
    </div>
    """, unsafe_allow_html=True)

with tab2:
    st.markdown("### // 單字與疊字")
    col1, col2 = st.columns(2)
    for i, v in enumerate(VOCABULARY):
        with col1 if i % 2 == 0 else col2:
            components.html(get_html_card(v, type="word"), height=130)

with tab3:
    st.markdown("### // 結構分析")
    for s in SENTENCES:
        st.markdown("""<div style="background:#0D47A1; padding:20px; border-radius: 10px; margin-bottom:20px; box-shadow: 0 5px 15px rgba(0,0,0,0.3); border: 1px solid #FFD700;">""", unsafe_allow_html=True)
        components.html(get_html_card(s, type="sentence"), height=160)
        st.markdown(f"""
        <div style="color:#FFD700; font-size:16px; margin-bottom:10px; border-top:1px solid #42A5F5; padding-top:10px; font-weight:bold;">{s['zh']}</div>
        <div style="color:#E3F2FD; font-size:14px; line-height:1.8; background:#1976D2; padding:10px; border-radius:6px;">
            <span style="color:#FFD700; font-weight:bold;">💡 NOTE:</span> {s.get('note', '')}
        </div>
        </div>
        """, unsafe_allow_html=True)

with tab4:
    if 'quiz_questions' not in st.session_state:
        st.session_state.quiz_questions = generate_quiz()
        st.session_state.quiz_step = 0; st.session_state.quiz_score = 0
    
    if st.session_state.quiz_step < len(st.session_state.quiz_questions):
        q = st.session_state.quiz_questions[st.session_state.quiz_step]
        st.markdown(f"""<div class="quiz-card">
            <span class="quiz-tag">{q['tag']}</span>
            <div style="font-size:20px; color:#FFFFFF; margin-bottom:20px; font-weight:bold;">{q['text']}</div>
        </div>""", unsafe_allow_html=True)
        
        if 'audio' in q: play_audio_backend(q['audio'])
        
        opts = q['options']; cols = st.columns(min(len(opts), 3))
        for i, opt in enumerate(opts):
            with cols[i % 3]:
                if st.button(opt, key=f"q_{st.session_state.quiz_step}_{i}"):
                    if opt.lower() == q['correct'].lower():
                        st.success("✅ Fangcal! (Correct)"); st.session_state.quiz_score += 1
                    else:
                        st.error(f"❌ Caay ka matira... 正解: {q['correct']}"); 
                        if 'note' in q: st.info(q['note'])
                    time.sleep(1.5); st.session_state.quiz_step += 1; st.rerun()
    else:
        st.markdown(f"""<div style="text-align:center; padding:40px; border-radius:10px; background:#0D47A1; border: 2px solid #FFD700;">
            <h1 style="color:#FFD700; font-family:Black Ops One;">Matomes To!</h1>
            <p style="font-size:22px; color:#90CAF9;">得分: {st.session_state.quiz_score} / {len(st.session_state.quiz_questions)}</p>
            <p style="color:#BBDEFB;">滿載而歸！(Full Harvest!)</p>
        </div>""", unsafe_allow_html=True)
        if st.button("🔄 再次出海 (Replay)"): del st.session_state.quiz_questions; st.rerun()

st.markdown("---")
st.caption("Powered by Code-CRF v7.3 | Theme: Navy Blue & Gold ⚓")
