import streamlit as st
import pandas as pd
import numpy as np

# --- PAGE CONFIG ---
st.set_page_config(page_title="Players Dashboard", layout="wide", initial_sidebar_state="expanded")

# --- CUSTOM CSS ---
st.markdown("""
<style>
    .block-container { padding-top: 1.5rem; }
    /* Top Metrics Styling */
    .metric-box { text-align: center; background-color: #F8F9FA; padding: 15px; border-radius: 8px; border: 1px solid #E9ECEF; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .metric-val { font-size: 2rem; font-weight: bold; color: #1E3A8A; margin-bottom: -5px; }
    .metric-title { font-size: 0.8rem; color: #6C757D; text-transform: uppercase; letter-spacing: 1px; font-weight: 600; }
    
    /* Coach Actions Styling */
    .good-action { background-color: #E8F5E9; padding: 12px; border-left: 5px solid #2E7D32; margin-bottom: 10px; border-radius: 4px; color: #1B5E20; }
    .bad-action { background-color: #FFEBEE; padding: 12px; border-left: 5px solid #C62828; margin-bottom: 10px; border-radius: 4px; color: #B71C1C; }
    .section-title { font-size: 0.9rem; color: #495057; text-transform: uppercase; margin-bottom: 12px; margin-top: 20px; font-weight: 700; border-left: 3px solid #1E3A8A; padding-left: 10px; }
    
    /* Benchmark Bar Styling */
    .bench-container { width: 100%; background-color: #E9ECEF; border-radius: 5px; height: 12px; position: relative; margin-bottom: 25px; }
    .bench-fill { background-color: #3B82F6; height: 12px; border-radius: 5px; }
    .bench-marker { position: absolute; top: -4px; height: 20px; width: 3px; background-color: #000000; border-radius: 1px; }
</style>
""", unsafe_allow_html=True)

# --- DATA LOADING AND PREPARATION ---
@st.cache_data
def load_data():
    # Reading the comprehensive file
    df = pd.read_excel('master_v2_2026.xlsx')


    
    def extract_float(val):
        if isinstance(val, str): return float(val.replace('%', '').strip())
        return float(val) if not pd.isna(val) else 0.0

    # Preparing numerical columns for standard traits
    cols_to_fix = [
        'Big 5: Extraversion %', 'Big 5: Agreeableness %', 'Big 5: Conscientiousness %', 
        'Big 5: Openness %', 'Big 5: Emotional Stability %', '4C: Control %', 
        '4C: Commitment %', '4C: Challenge %', '4C: Confidence %',
        'תומך %', 'משימתי %', 'מנתח %', 'מקדם %'
    ]
    for col in cols_to_fix:
        if col in df.columns:
            df[f"{col}_num"] = df[col].apply(extract_float)

   # Backup calculation for derived metrics (if they are missing from excel)
    if 'Score: IMP' not in df.columns:
        df['Score: IMP'] = np.round((df.get('משימתי %_num', 0) * 0.4 + df.get('מקדם %_num', 0) * 0.3 + df.get('4C: Commitment %_num', 0) * 0.3), 1)
    if 'Score: MTI' not in df.columns:
        df['Score: MTI'] = np.round(((df.get('4C: Control %_num', 0) + df.get('4C: Commitment %_num', 0) + df.get('4C: Challenge %_num', 0) + df.get('4C: Confidence %_num', 0)) / 4), 1)
    if 'Score: PPS' not in df.columns:
        df['Score: PPS'] = np.round((df.get('Big 5: Openness %_num', 0) * 0.35 + df.get('Big 5: Conscientiousness %_num', 0) * 0.35 + df.get('4C: Challenge %_num', 0) * 0.3), 1)

    # Translation and cleaning of style names
    style_map = {'משימתי': 'Task-Oriented', 'מקדם': 'Promoter', 'מנתח': 'Analyzer', 'תומך': 'Supporter'}
    def translate_style(s):
        if not isinstance(s, str): return 'Unknown'
        for heb, eng in style_map.items():
            if heb in s: return eng
        return s.split('(')[0].strip()
        
    if 'מודל: ראשי' in df.columns:
        df['Primary_EN'] = df['מודל: ראשי'].apply(translate_style)
    else:
        df['Primary_EN'] = 'Unknown'
        
    return df

df = load_data()

# --- TOOLTIPS & HELPERS ---
tooltips = {
    "IMP": "Impact Score: Measures the player's actual influence on the game by combining Task-Orientation, Promoting ability, and Commitment.",
    "MTI": "Mental Toughness Index: A measure of mental resilience based on the average of the 4C model (Control, Commitment, Challenge, Confidence).",
    "PPS": "Performance Potential Score: Predicts the potential for improvement based on Openness to learning, Conscientiousness, and Challenge-seeking."
}

def metric_with_help(label, value, help_text):
    html = f"""
    <div class='metric-box' title="{help_text}">
        <div class='metric-val'>{value}</div>
        <div class='metric-title' style="display: flex; justify-content: center; align-items: center; gap: 5px;">
            {label} <span style="cursor:help; font-size:12px; color:#3B82F6; border: 1px solid #3B82F6; border-radius: 50%; width: 15px; height: 15px; display: flex; justify-content: center; align-items: center;">?</span>
        </div>
    </div>
    """
    return html

# --- COACHING CONTENT ---
COACHING_GUIDE = {
    'Supporter': {
        'summary': "Supportive-Relational players bring loyalty, calmness, and team cohesion. They perform best when they feel trusted, respected, and emotionally safe",
        'how_in_team': "A Supportive-Relational player is usually a strong team connector. They help create calm, trust, and emotional stability inside the group. They are loyal, cooperative, sensitive to teammates, and usually prefer harmony over conflict. They may not be the loudest leader, but they often become an important stabilizing presence in the team.",
        'team_value': "Builds trust and positive relationships.\n Supports teammates emotionally.\n Helps reduce tension and conflict.\n Works well in shared responsibility. Brings calmness under pressure. Strengthens team cohesion",
        'watch_out': "May avoid direct conflict. \n May hide frustration to keep harmony.\n May agree outwardly even when they disagree internally. \nCan lose confidence or energy under aggressive criticism",
        'recommended_action': "Have a short personal conversation. \n Reinforce their importance to the team, give one clear responsibility, and explain how it helps the group succeed.",
        'what_to_say': "I trust you. Your role is important for the team. I need you to help us keep stability, responsibility, and calm in this situation.",
        'dos': [
            "[הכנס Do 1: עשה ראשון]", 
            "[הכנס Do 2: עשה שני]"
        ],
        'donts': [
            "[הכנס Dont 1: אל תעשה ראשון]", 
            "[הכנס Dont 2: אל תעשה שני]"
        ]
    },
    'Promoter': {
        'summary': "Promoter performs best when inspired, recognized, and given room to express ideas. In the team, they bring energy, optimism, creativity, and social momentum.",
        'how_in_team': "A Promoter player is usually the energy source of the team.\n They bring enthusiasm, optimism, creativity, and confidence into the group.\n They often influence others through emotion, stories, humor, and personal connection.\n They can lift the team atmosphere, create belief, and help others feel that something is possible even when the situation is difficult.\n They are usually easy to connect with, socially open, and comfortable being visible.\n At their best, they create momentum, inspire teammates, and bring positive energy to the group.\n Under pressure, they may become impulsive, jump between ideas, take risks without checking details, or struggle to finish tasks all the way through.",
        'team_value': "Brings energy and enthusiasm.\nCreates optimism and belief.\nInspires teammates to act.\nBuilds strong personal connections.\nHelps lift team morale.\nBrings creativity and fresh ideas.\nCan influence others through confidence and emotion.\n Helps the group move forward when motivation drops",
        'watch_out': "May jump too quickly between ideas.\n May talk a lot and lose focus.\nMay avoid routine tasks or small details.\nMay act impulsively under pressure.\nMay overpromise and under-deliver.\nMay take risks without checking enough information.\nMay need external recognition to stay fully engaged.\n May struggle when isolated or left alone too much.",
        'recommended_action': "Give them a motivating challenge connected to team energy, visibility, and impact.\n Let them feel that their enthusiasm matters, but give them one clear task and a simple follow-up point.\n Do not overload them with too many details.\n Keep the message energetic, positive, and clear.",
        'what_to_say': "I need your energy today. Help us lift the group, create momentum, and bring confidence into the game. Focus on one clear action and make sure we complete it.",
        'dos': ["Be enthusiastic, positive, and engaging",
"Give recognition and personal appreciation",
"Use examples, stories, and clear images",
"Connect the task to inspiration and team momentum",
"Give them space to express ideas",
"Help them prioritize what matters most",
"Keep the atmosphere positive and alive",
"Follow up clearly on who does what",
"Praise them publicly when appropriate",
"Bring them back gently when they lose focus"],
        'donts': ["Do not criticize them publicly",
"Do not speak in a cold or overly authoritative tone",
"Do not overload them with boring details",
"Do not shut down their ideas too quickly",
"Do not isolate them for too long",
"Do not use only routine tasks without inspiration",
"Do not say only “you must” or “you have to”",
"Do not point aggressively or create public embarrassment",
"Do not let them leave the conversation without clear next steps",
"Do not assume enthusiasm means execution is already secured"]
    },
    'Analyzer': {
        'summary': "Analyzer performs best with clear information, structure, logic, and time to think. In the team, they bring accuracy, stability, problem-solving, and thoughtful decision-making.",
        'how_in_team': "An Analyzer player is usually one of the most thoughtful and reliable players in the group.\n They observe carefully, ask questions, analyze situations, and prefer to understand the full picture before acting.\n They may not always be the first to speak or lead from the front, but teammates often rely on them for stability, detail, and clear thinking.\n They help the team avoid mistakes, make better decisions, and solve complex situations.\n Under pressure, they may overthink, hesitate, avoid risk, or become stuck when information is missing or unclear.",
        'team_value': "Brings structure and stability.\nNotices details others may miss.\nHelps the team avoid unnecessary mistakes.\nThinks before acting.\nSolves complex problems calmly.\nGives reliable and thoughtful input.\nSupports better decision-making.\n Can become a trusted advisor inside the team",
        'watch_out': "May overthink and delay action .\n May avoid taking risks .\n May hesitate when information is incomplete .\n May become stressed by sudden changes .\n May appear distant or overly critical .\n May prefer working alone over group pressure .\n May avoid speaking unless directly asked.\n May get stuck when there is too much noise or uncertainty",
        'recommended_action': "Give them clear information, explain the logic, and allow them time to process..\n Before demanding immediate action, make sure they understand:.\n what the goal is.\n why it matters. \n what information supports the decision.\nwhat exact role they need to perform.\n Keep the conversation calm, structured, and factual.",
        'what_to_say': "I want your analysis here. Look at the situation, focus on the key details, and help us make the right decision. The goal is clear, and I trust your judgment.",
        'dos': ["Be calm, logical, and structured",
"Give clear facts and useful data",
"Explain the reason behind the task",
"Allow time to think before answering",
"Ask for their opinion directly",
"Put important instructions in writing",
"Be precise and avoid vague messages",
"Keep promises and follow agreed steps",
"Give feedback privately and respectfully",
"Build a clear framework for execution"],
        'donts': ["Do not rush them without context",
"Do not interrupt them while thinking",
"Do not raise your voice",
"Do not criticize them publicly",
"Do not surprise them with sudden changes",
"Do not give vague or emotional instructions",
"Do not push them into unnecessary risk",
"Do not dismiss their questions",
"Do not overload them with noise or chaos",
"Do not expect instant decisions without information"]
    },
    'Task-Oriented': {
        'summary': "Task-Oriented performs best with challenge, control, clear goals, and responsibility. In the team, they bring drive, decisiveness, and a strong focus on results.",
        'how_in_team': "A Task-Oriented player is usually a strong driver inside the team. \n They push the group toward action, results, and clear execution. \nThey are goal-focused, decisive, competitive, and often comfortable taking responsibility in demanding situations.\n They may naturally step forward when others hesitate, but under pressure they can become impatient, too direct, or less sensitive to teammates.\n They are often most valuable when the team needs urgency, leadership, and execution.",
        'team_value': "Drives action and progress.\n Brings strong goal focus. \n Takes responsibility under pressure. \n Pushes the team toward results.\n Makes quick decisions. \n Can lead when others hesitate",
        'watch_out': "May become impatient with slower teammates.\n May sound too direct or aggressive.\n May resist close control or micromanagement.\n May lose energy with routine tasks.\n May focus on results and miss emotional signals.\n May try to control the situation too much",
        'recommended_action': "Give them one clear challenge, define the outcome, and give them responsibility to execute.\n Keep the conversation short, direct, and focused on what needs to happen.",
        'what_to_say': "I need you to take responsibility here. The goal is clear: lead this action, keep the team focused, and make sure we execute.",
        'dos': ["Be direct, clear, and practical",
"Get to the point quickly",
"Give clear goals and success measures",
"Offer responsibility and ownership",
"Show how the task helps the team win",
"Recognize results openly",
"Give them room to act in their own way"],
        'donts': ["Waste their time",
"Be late or unclear",
"Micromanage every detail",
"Give long emotional explanations before the task",
"Take away their sense of control",
"Focus only on process without showing the outcome",
"Publicly challenge their competence without facts"]
    }
}
# --- KEY INSIGHTS (COMBINED STYLES) ---
KEY_INSIGHTS = {
    # שילובים כשהמשימתי הוא הראשי
    'Task-Oriented_Promoter': "This player drives action and results, with added energy and influence. Give them a clear challenge, responsibility, and room to lead, while helping them use their energy to lift others.",
    'Task-Oriented_Analyzer': "This player brings urgency, execution, and structured decision-making. The coach’s job is to combine challenge and ownership with clear reasoning, so intensity turns into focused action and smart follow-through.",
    'Task-Oriented_Supporter': "This player drives action and results, but also needs trust and respectful communication. Give them clear responsibility and freedom to execute, while connecting their role to team stability and cohesion.",
    
    # שילובים כשהמקדם הוא הראשי
    'Promoter_Task-Oriented': "This player brings energy, influence, and momentum to the team. The coach’s job is to channel that energy into clear goals, ownership, and follow-through.",
    'Promoter_Analyzer': "This player brings creativity, energy, and ideas, but needs structure to turn inspiration into smart decisions. Give them space to express ideas, then help them organize, prioritize, and execute.",
    'Promoter_Supporter': "This player brings energy, connection, and positive team atmosphere. The coach’s job is to recognize their enthusiasm while creating emotional safety, trust, and clear next steps.",
    
    # שילובים כשהמנתח הוא הראשי
    'Analyzer_Task-Oriented': "This player brings logic, precision, and execution focus. The coach’s job is to give them facts, define the outcome, and help them act decisively without getting stuck in over-analysis",
    'Analyzer_Promoter': "This player brings structure, accuracy, and thoughtful decision-making, with added creativity and communication energy. Give them clear information, then invite ideas and help them move from analysis to action.",
    'Analyzer_Supporter': "This player brings careful thinking, emotional sensitivity, and team stability. Give them clear information, patience, and trust, then ask for their input in a calm and respectful way.",
    
    # שילובים כשהתומך הוא הראשי
    'Supporter_Task-Oriented': "This player brings loyalty, calmness, and responsibility. The coach’s job is to create emotional safety, then give them one clear task that connects their contribution to team success.",
    'Supporter_Promoter': "This player brings emotional stability, connection, and positive energy to the team. Build trust first, then use recognition and enthusiasm to help them contribute more openly.",
    'Supporter_Analyzer': "This player brings trust, stability, patience, and careful judgment. Give them a calm environment, clear structure, and enough time to process, then connect their role to supporting the group."
}

# --- SIDEBAR ---
# בתוך קובץ app.py - החלפת ה-SIDEBAR

with st.sidebar:
    st.title("🏆 Scouting System 25/26")
    st.markdown("---")
    
    # 1. חיפוש חופשי (תמיד זמין)
    search_query = st.text_input("🔍 Quick Search (Name):", "")

    # 2. בחירת ליגה
    if 'League' in df.columns:
        leagues = sorted(df['League'].dropna().unique().tolist())
        selected_league = st.selectbox("📍 Select League:", ["All Leagues"] + leagues)
    else:
        selected_league = "All Leagues"

    # סינון ראשוני לפי ליגה
    if selected_league != "All Leagues":
        league_df = df[df['League'] == selected_league]
    else:
        league_df = df

    # 3. בחירת קבוצה (מסונן לפי הליגה שנבחרה)
    if 'Team' in league_df.columns:
        teams = sorted(league_df['Team'].dropna().unique().tolist())
        selected_team = st.selectbox("⚽ Select Team:", ["All Teams"] + [f"🛡️ {t}" for t in teams])
    else:
        selected_team = "All Teams"

    # סינון שני לפי קבוצה
    if selected_team != "All Teams":
        team_name = selected_team.replace("🛡️ ", "")
        final_filtered_df = league_df[league_df['Team'] == team_name]
    else:
        final_filtered_df = league_df

    # סינון שלישי לפי חיפוש טקסטואלי
    if search_query:
        final_filtered_df = final_filtered_df[final_filtered_df['Player'].str.contains(search_query, case=False, na=False)]

    st.markdown("---")

    # 4. בחירת השחקן הסופי
    if not final_filtered_df.empty:
        player_list = sorted(final_filtered_df['Player'].unique().tolist())
        selected_player = st.selectbox("👤 Choose Player:", player_list)
    else:
        st.warning("No players found matching these criteria.")
        selected_player = None

# הגדרת נתוני השחקן להמשך האתר
if selected_player:
    player_data = df[df['Player'] == selected_player].iloc[0]
else:
    player_data = pd.Series()

# --- TOP HEADER ---
if not player_data.empty:
    c_img, c_info, c_imp, c_mti, c_pps = st.columns([1, 4, 1.5, 1.5, 1.5])

    with c_img: 
        st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=80)

    with c_info:
        st.header(player_data.get('Player', 'Unknown'))
        st.write(f"**{player_data.get('Team', 'Unknown')}** • {player_data.get('Position', 'Unknown')}")

    with c_imp: 
        st.markdown(metric_with_help("IMP", player_data.get('Score: IMP', 0), tooltips["IMP"]), unsafe_allow_html=True)
    with c_mti: 
        st.markdown(metric_with_help("MTI", player_data.get('Score: MTI', 0), tooltips["MTI"]), unsafe_allow_html=True)
    with c_pps: 
        st.markdown(metric_with_help("PPS", player_data.get('Score: PPS', 0), tooltips["PPS"]), unsafe_allow_html=True)

    st.markdown("---")
    t_coach, t_persona, t_detailed, t_report = st.tabs(["Coach Actions", "Player Persona", "Detailed Traits", "Report"])

   # ==========================================
    # TAB 1: COACH ACTIONS
    # ==========================================
    with t_coach:
        # חילוץ הסגנונות לפי הסדר
        styles_map = {'Task-Oriented': player_data.get('משימתי %_num', 0), 'Promoter': player_data.get('מקדם %_num', 0), 
                      'Analyzer': player_data.get('מנתח %_num', 0), 'Supporter': player_data.get('תומך %_num', 0)}
        sorted_s = sorted(styles_map.items(), key=lambda x: x[1], reverse=True)
        
        primary_style_name = sorted_s[0][0]
        secondary_style_name = sorted_s[1][0]
        
        # 1. תיבת הסיכום העליונה (תמיד מציגה את הסיכום של הסגנון הראשי)
        guide_primary = COACHING_GUIDE.get(primary_style_name, COACHING_GUIDE['Task-Oriented'])
        st.markdown("<div class='section-title'>COMMUNICATION SUMMARY</div>", unsafe_allow_html=True)
        st.info(f"**{primary_style_name} Profile:** {guide_primary['summary']}")
        
        col_l, col_r = st.columns([1, 1.5])
        
        with col_l:
            st.markdown("<div class='section-title'>COMMUNICATION STYLE FIT</div>", unsafe_allow_html=True)
            
            # הצגת 4 הסגנונות בצבעים שונים
            for idx, (s_name, s_val) in enumerate(sorted_s):
                if idx == 0:
                    label = "Primary"
                    bg_color = "#DBEAFE" # כחול מודגש
                    border = "#2563EB"
                    text_c = "#1E3A8A"
                elif idx == 1:
                    label = "Secondary"
                    bg_color = "#EFF6FF" # כחול בהיר
                    border = "#60A5FA"
                    text_c = "#1E3A8A"
                else:
                    label = "Optional"
                    bg_color = "#F8F9FA" # אפור
                    border = "#DEE2E6"
                    text_c = "#6C757D"
                
                card = f"""
                <div style="border: 1px solid {border}; background-color: {bg_color}; border-radius: 8px; padding: 12px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center;">
                    <div><span style="background-color: {border}; color: white; font-size: 10px; padding: 2px 6px; border-radius: 3px; margin-right: 10px;">{label}</span>
                    <span style="color: {text_c}; font-weight: 600;">{s_name}</span></div>
                    <div style="color: {text_c}; font-weight: bold;">{int(s_val)}</div>
                </div>"""
                st.markdown(card, unsafe_allow_html=True)

            # תיבת ה-Key Insight הצהובה
            # מרכיב את המפתח לחציית הסגנונות (למשל: "Task-Oriented_Promoter")
            insight_key = f"{primary_style_name}_{secondary_style_name}"
            # שולף את הטקסט, אם אין שילוב מדויק ייתן הודעת ברירת מחדל
            insight_text = KEY_INSIGHTS.get(insight_key, "Combination insight not available.")
            
            st.markdown(f"""
            <div style='background-color:#FFFBEB; border-left:4px solid #F59E0B; padding:15px; border-radius:4px; font-size:14px; color:#495057; margin-top:20px; margin-bottom:15px; box-shadow: 0 1px 2px rgba(0,0,0,0.05);'>
                <strong style='color:#B45309; text-transform:uppercase; font-size:12px; letter-spacing:0.5px;'>💡 Key Insight: {primary_style_name} + {secondary_style_name}</strong><br>
                <div style='margin-top:5px;'>{insight_text}</div>
            </div>
            """, unsafe_allow_html=True)

            # כפתורי בחירה אינטראקטיביים כדי לראות את שאר המידע על כל סגנון בנפרד
            st.markdown("<div style='font-size:14px; font-weight:bold; color:#495057; margin-bottom:5px; margin-top:20px;'>Explore Style Details:</div>", unsafe_allow_html=True)
            selected_style_to_view = st.radio(
                "Select style to view details:",
                [primary_style_name, secondary_style_name],
                horizontal=True,
                label_visibility="collapsed"
            )

            # מגדיר את view_guide (שאר התיבות ישתמשו בו בצד ימין)
            view_guide = COACHING_GUIDE.get(selected_style_to_view, COACHING_GUIDE['Task-Oriented'])

        with col_r:
            st.markdown(f"<div class='section-title'>{selected_style_to_view.upper()} STYLE GUIDE</div>", unsafe_allow_html=True)
            
            # 4 התיבות הריבועיות ב-2 עמודות פנימיות
            b1, b2 = st.columns(2)
            with b1:
                st.markdown(f"""
                <div style='background-color:#FFFFFF; border:1px solid #DEE2E6; padding:12px; border-radius:6px; margin-bottom:10px; box-shadow: 0 1px 2px rgba(0,0,0,0.02);'>
                    <div style='font-size:11px; font-weight:bold; color:#6C757D; text-transform:uppercase;'>How they are in a team</div>
                    <div style='font-size:14px; color:#212529; margin-top:4px;'>{view_guide['how_in_team']}</div>
                </div>
                """, unsafe_allow_html=True)
                st.markdown(f"""
                <div style='background-color:#FFFFFF; border:1px solid #DEE2E6; padding:12px; border-radius:6px; margin-bottom:10px; box-shadow: 0 1px 2px rgba(0,0,0,0.02);'>
                    <div style='font-size:11px; font-weight:bold; color:#6C757D; text-transform:uppercase;'>Watch out for</div>
                    <div style='font-size:14px; color:#212529; margin-top:4px;'>{view_guide['watch_out']}</div>
                </div>
                """, unsafe_allow_html=True)

            with b2:
                st.markdown(f"""
                <div style='background-color:#FFFFFF; border:1px solid #DEE2E6; padding:12px; border-radius:6px; margin-bottom:10px; box-shadow: 0 1px 2px rgba(0,0,0,0.02);'>
                    <div style='font-size:11px; font-weight:bold; color:#6C757D; text-transform:uppercase;'>Team value</div>
                    <div style='font-size:14px; color:#212529; margin-top:4px;'>{view_guide['team_value']}</div>
                </div>
                """, unsafe_allow_html=True)
                st.markdown(f"""
                <div style='background-color:#FFFFFF; border:1px solid #DEE2E6; padding:12px; border-radius:6px; margin-bottom:10px; box-shadow: 0 1px 2px rgba(0,0,0,0.02);'>
                    <div style='font-size:11px; font-weight:bold; color:#6C757D; text-transform:uppercase;'>Recommended coach action</div>
                    <div style='font-size:14px; color:#212529; margin-top:4px;'>{view_guide['recommended_action']}</div>
                </div>
                """, unsafe_allow_html=True)

            # תיבת ה"מה להגיד" פרוסה לכל הרוחב
            st.markdown(f"""
            <div style='background-color:#F0F8FF; border:1px solid #BAE6FD; padding:12px; border-radius:6px; margin-bottom:20px;'>
                <div style='font-size:11px; font-weight:bold; color:#0284C7; text-transform:uppercase;'>What to say</div>
                <div style='font-size:15px; color:#0C4A6E; margin-top:4px; font-style:italic;'>"{view_guide['what_to_say']}"</div>
            </div>
            """, unsafe_allow_html=True)

            # ה-Dos וה-Donts
            d1, d2 = st.columns(2)
            with d1:
                st.markdown("<div style='font-size:13px; font-weight:bold; color:#1B5E20; margin-bottom:5px; border-bottom:1px solid #C8E6C9; padding-bottom:5px;'>👍 How to communicate (Do)</div>", unsafe_allow_html=True)
                for d in view_guide['dos']:
                    st.markdown(f"<div class='good-action' style='padding:8px; font-size:13px;'>{d}</div>", unsafe_allow_html=True)
            with d2:
                st.markdown("<div style='font-size:13px; font-weight:bold; color:#B71C1C; margin-bottom:5px; border-bottom:1px solid #FFCDD2; padding-bottom:5px;'>⚠️ Communication pitfalls (Don't)</div>", unsafe_allow_html=True)
                for d in view_guide['donts']:
                    st.markdown(f"<div class='bad-action' style='padding:8px; font-size:13px;'>{d}</div>", unsafe_allow_html=True)
   # ==========================================
    # TAB 2: PLAYER PERSONA
    # ==========================================
    with t_persona:
        col_bench, col_stats = st.columns([1.5, 1])
        # ==========================================
    # TAB 2: PLAYER PERSONA
    # ==========================================
    with t_persona:
        col_bench, col_stats = st.columns([1.5, 1])
        with col_bench:
            # שיניתי את הכותרת שתבהיר שמדובר בממוצע קבוצתי
            st.markdown("<div class='section-title'>BENCHMARK VS TEAM (Black line = Team Average)</div>", unsafe_allow_html=True)
            b5_traits = ['Emotional Stability', 'Extraversion', 'Openness', 'Agreeableness', 'Conscientiousness']
            c4_traits = ['Control', 'Commitment', 'Challenge', 'Confidence']
            
            # --- הלוגיקה החדשה לחילוץ נתוני הקבוצה הספציפית ---
            player_team = player_data.get('Team', None)
            if player_team:
                team_df = df[df['Team'] == player_team]
            else:
                team_df = df  # למקרה שאין קבוצה מוגדרת, יחזור לכלל המאגר
            
            st.markdown("#### BIG FIVE PERSONALITY")
            for t in b5_traits:
                full_col = f"Big 5: {t} %_num"
                if full_col in player_data:
                    p_val = player_data[full_col]
                    # חישוב הממוצע מתבצע כעת על team_df במקום על df
                    a_val = team_df[full_col].mean()
                    
                    bar_html = f"""
                    <div style='margin-bottom: 15px;'>
                        <div style='font-weight: 600; font-size: 14px; margin-bottom: 4px; color: #343A40;'>{t}</div>
                        <div style='display: flex; align-items: center; gap: 10px;'>
                            <div class='bench-container' style='margin-bottom: 0; flex-grow: 1;'>
                                <div class='bench-fill' style='width:{p_val}%'></div>
                                <div class='bench-marker' style='left:{a_val}%'></div>
                            </div>
                            <div style='font-weight: bold; color: #1E3A8A; min-width: 45px; text-align: right;'>{p_val:.1f}</div>
                        </div>
                    </div>
                    """
                    st.markdown(bar_html, unsafe_allow_html=True)
                
            st.markdown("#### MENTAL TOUGHNESS - 4Cs")
            for t in c4_traits:
                full_col = f"4C: {t} %_num"
                if full_col in player_data:
                    p_val = player_data[full_col]
                    # חישוב הממוצע מתבצע כעת על team_df במקום על df
                    a_val = team_df[full_col].mean()
                    
                    bar_html = f"""
                    <div style='margin-bottom: 15px;'>
                        <div style='font-weight: 600; font-size: 14px; margin-bottom: 4px; color: #343A40;'>{t}</div>
                        <div style='display: flex; align-items: center; gap: 10px;'>
                            <div class='bench-container' style='margin-bottom: 0; flex-grow: 1;'>
                                <div class='bench-fill' style='width:{p_val}%'></div>
                                <div class='bench-marker' style='left:{a_val}%'></div>
                            </div>
                            <div style='font-weight: bold; color: #1E3A8A; min-width: 45px; text-align: right;'>{p_val:.1f}</div>
                        </div>
                    </div>
                    """
                    st.markdown(bar_html, unsafe_allow_html=True)

        with col_stats:
            # Fetching Top 3 Strengths and Bottom 3 Traits
            all_t_cols = {t: f"Big 5: {t} %_num" for t in b5_traits}
            all_t_cols.update({t: f"4C: {t} %_num" for t in c4_traits})
            
            trait_scores = {name: player_data.get(col, 0) for name, col in all_t_cols.items()}
            sorted_traits = sorted(trait_scores.items(), key=lambda x: x[1], reverse=True)
            
            st.markdown("<div class='section-title'>TOP STRENGTHS</div>", unsafe_allow_html=True)
            for t, s in sorted_traits[:3]: st.success(f"**{t}**: {s:.1f}")
            
            st.markdown("<div class='section-title'>DEVELOPMENT PRIORITIES</div>", unsafe_allow_html=True)
            for t, s in sorted_traits[-3:]: st.error(f"**{t}**: {s:.1f}")

   # ==========================================
    # TAB 3: DETAILED TRAITS (FACETS)
    # ==========================================
    with t_detailed:
        st.markdown("<div class='section-title'>EXPERT VIEW - DEEP TRAIT ANALYSIS</div>", unsafe_allow_html=True)
        
        st.markdown("""
<div style='display:flex; gap:15px; margin-bottom:20px; font-size:14px;'>
    <div style='display:flex; align-items:center; gap:5px;'><div style='width:12px; height:12px; background-color:#10B981; border-radius:3px;'></div> <span>Strength (> 65)</span></div>
    <div style='display:flex; align-items:center; gap:5px;'><div style='width:12px; height:12px; background-color:#3B82F6; border-radius:3px;'></div> <span>Average (40 - 65)</span></div>
    <div style='display:flex; align-items:center; gap:5px;'><div style='width:12px; height:12px; background-color:#EF4444; border-radius:3px;'></div> <span>Needs Attention (< 40)</span></div>
</div>
""", unsafe_allow_html=True)
        
        def get_clean_float(col_name):
            if col_name in player_data:
                val = player_data[col_name]
                if isinstance(val, str):
                    return float(val.replace('%', '').strip())
                return float(val) if not pd.isna(val) else 0.0
            return 0.0

        facets_data = {
            'Emotional Stability': {
                'Anxiety': get_clean_float('Facet: Anxiety %'),
                'Angry Hostility': get_clean_float('Facet: Angry Hostility %'),
                'Depression': get_clean_float('Facet: Depression %'),
                'Self-consciousness': get_clean_float('Facet: Self-consciousness %'),
                'Impulsiveness': get_clean_float('Facet: Impulsiveness %'),
                'Vulnerability': get_clean_float('Facet: Vulnerability %')
            },
            'Extraversion': {
                'Warmth': get_clean_float('Facet: Warmth %'),
                'Gregariousness': get_clean_float('Facet: Gregariousness %'),
                'Assertiveness': get_clean_float('Facet: Assertiveness %'),
                'Activity': get_clean_float('Facet: Activity %'),
                'Excitement-seeking': get_clean_float('Facet: Excitement-seeking %'),
                'Positive emotions': get_clean_float('Facet: Positive emotions %')
            },
            'Openness': {
                'Imagination': get_clean_float('Facet: Imagination %'),
                'Game vision': get_clean_float('Facet: Game vision %'),
                'Feelings awareness': get_clean_float('Facet: Feelings awareness %'),
                'Actions / flexibility': get_clean_float('Facet: Actions / flexibility %'),
                'Ideas': get_clean_float('Facet: Ideas %'),
                'Values / learning': get_clean_float('Facet: Values / learning openness %')
            },
            'Agreeableness': {
                'Trust': get_clean_float('Facet: Trust %'),
                'Straightforwardness': get_clean_float('Facet: Straightforwardness %'),
                'Altruism': get_clean_float('Facet: Altruism %'),
                'Compliance': get_clean_float('Facet: Compliance %'),
                'Modesty': get_clean_float('Facet: Modesty %'),
                'Tender-mindedness': get_clean_float('Facet: Tender-mindedness %')
            },
            'Conscientiousness': {
                'Competence': get_clean_float('Facet: Competence %'),
                'Order': get_clean_float('Facet: Order %'),
                'Dutifulness': get_clean_float('Facet: Dutifulness %'),
                'Achievement striving': get_clean_float('Facet: Achievement striving %'),
                'Self-discipline': get_clean_float('Facet: Self-discipline %'),
                'Deliberation': get_clean_float('Facet: Deliberation %')
            }
        }

        valid_facets = []
        for f_dict in facets_data.values():
            for f_name, f_val in f_dict.items():
                if f_val > 0.0:
                    valid_facets.append({'name': f_name, 'val': f_val})
                
        sorted_all_facets = sorted(valid_facets, key=lambda x: x['val'], reverse=True)
        
        col_top, col_bot = st.columns(2)
        with col_top:
            top_html = "<div style='background-color:#E8F5E9; border:1px solid #C8E6C9; border-radius:8px; padding:15px; height:100%;'>"
            top_html += "<h5 style='color:#2E7D32; margin-top:0;'>Top 5 Traits</h5>"
            if sorted_all_facets:
                for f in sorted_all_facets[:5]:
                    top_html += f"<div style='display:flex; justify-content:space-between; margin-bottom:5px; color:#1B5E20;'><span>{f['name']}</span> <strong>{f['val']:.1f}</strong></div>"
            top_html += "</div>"
            st.markdown(top_html, unsafe_allow_html=True)
            
        with col_bot:
            bot_html = "<div style='background-color:#FFEBEE; border:1px solid #FFCDD2; border-radius:8px; padding:15px; height:100%;'>"
            bot_html += "<h5 style='color:#C62828; margin-top:0;'>Lowest Traits</h5>"
            if sorted_all_facets:
                for f in sorted_all_facets[-5:]: 
                    bot_html += f"<div style='display:flex; justify-content:space-between; margin-bottom:5px; color:#B71C1C;'><span>{f['name']}</span> <strong>{f['val']:.1f}</strong></div>"
            bot_html += "</div><br>"
            st.markdown(bot_html, unsafe_allow_html=True)

        # פונקציית סרגל מנוקה מרווחים עודפים!
        def draw_colored_bar(val):
            color = "#10B981" if val >= 65 else "#EF4444" if val < 40 else "#3B82F6"
            return f"""<div style="width: 100%; background-color: #E9ECEF; border-radius: 4px; height: 16px; position: relative; margin-top: 5px;">
<div style="width: {val}%; background-color: {color}; height: 16px; border-radius: 4px;"></div>
<div style="position: absolute; left: 50%; top: -2px; height: 20px; width: 2px; background-color: #ADB5BD; border-radius: 1px; z-index: 10;"></div>
</div>"""

        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        categories = list(facets_data.keys())
        
        for i, category in enumerate(categories):
            col_dest = c1 if i % 2 == 0 else c2
            with col_dest:
                cat_html = f"<div style='border:1px solid #DEE2E6; padding:15px; border-radius:8px; margin-bottom:15px;'>"
                cat_html += f"<h5 style='color:#495057; text-transform:uppercase; margin-top:0;'>{category}</h5>"
                
                for f_name, f_val in facets_data[category].items():
                    if f_val > 0.0:  
                        # ה-HTML מנוקה מרווחים כדי לא להפוך ל-Markdown Code Block
                        cat_html += f"""<div style='margin-bottom: 12px;'>
<div style='display:flex; justify-content:space-between; font-size:14px; font-weight:600; color:#343A40;'>
<span>{f_name}</span><span>{f_val:.1f}</span>
</div>
{draw_colored_bar(f_val)}
</div>"""
                
                cat_html += "</div>"
                st.markdown(cat_html, unsafe_allow_html=True)


   # ==========================================
    # TAB 4: REPORT (ROLE VIEWS)
    # ==========================================

    with t_report:
        # --- הגדרת מילון הטיפים לשחקן ---
        PLAYER_TIPS = {
            'Anxiety': "Establish a pre-match routine to build certainty and reduce nerves.",
            'Angry Hostility': "Channel frustration into aggressive defending rather than arguing with refs.",
            'Depression': "Focus on the next positive action immediately after a mistake.",
            'Self-consciousness': "Play simple early in the game to build rhythm before taking risks.",
            'Impulsiveness': "Take an extra split-second to scan before executing a high-risk pass.",
            'Vulnerability': "Use mental visualization techniques to prepare for high-pressure scenarios.",
            'Warmth': "Communicate more actively and encourage teammates during dead balls.",
            'Gregariousness': "Demand the ball more often to stay continuously engaged in the flow.",
            'Assertiveness': "Take the initiative to dictate the tempo; don't wait for the game to come to you.",
            'Activity': "Increase off-the-ball movement to create passing lanes for teammates.",
            'Excitement-seeking': "Look to take on defenders 1v1 in the final third to break defensive lines.",
            'Positive emotions': "Maintain high energy and body language, even when trailing.",
            'Imagination': "Don't be afraid to try the unexpected pass when the standard option is blocked.",
            'Game vision': "Scan the far side of the pitch before receiving to spot switching opportunities.",
            'Feelings awareness': "Pay attention to the momentum of the game and slow down play when needed.",
            'Actions / flexibility': "Adapt quicker to tactical shifts or opponent formation changes during play.",
            'Ideas': "Experiment with different types of crosses and deliveries into the box.",
            'Values / learning': "Watch video analysis of top players in your position to absorb new habits.",
            'Trust': "Anticipate your teammates' runs rather than waiting for them to arrive.",
            'Straightforwardness': "Keep your passing game simple and reliable in the defensive and middle thirds.",
            'Altruism': "Look for the cut-back or better-positioned player instead of forcing a low-percentage shot.",
            'Compliance': "Maintain strict tactical discipline, especially during defensive transitions.",
            'Modesty': "Prioritize team shape over individual pressing runs that leave gaps.",
            'Tender-mindedness': "Support teammates immediately when they make a mistake to maintain team cohesion.",
            'Competence': "Focus on mastering basic technical executions (first touch) under pressure.",
            'Order': "Maintain exact positional discipline and distances relative to your defensive line.",
            'Dutifulness': "Commit to tracking back and recovering your defensive position after every attack.",
            'Achievement striving': "Increase urgency inside the penalty box; be hungry to finish chances.",
            'Self-discipline': "Maintain high intensity in your pressing, even late in the game.",
            'Deliberation': "Evaluate the risk-reward before committing to a slide tackle or tight dribble."
        }

        # --- מציאת ה-Big 5 עבור החולשה המרכזית ---
        # מילון עזר כדי לדעת איזה Facet שייך לאיזה Big 5
        facet_to_big5_map = {
            'Anxiety': 'Emotional Stability', 'Angry Hostility': 'Emotional Stability', 'Depression': 'Emotional Stability', 
            'Self-consciousness': 'Emotional Stability', 'Impulsiveness': 'Emotional Stability', 'Vulnerability': 'Emotional Stability',
            'Warmth': 'Extraversion', 'Gregariousness': 'Extraversion', 'Assertiveness': 'Extraversion', 
            'Activity': 'Extraversion', 'Excitement-seeking': 'Extraversion', 'Positive emotions': 'Extraversion',
            'Imagination': 'Openness', 'Game vision': 'Openness', 'Feelings awareness': 'Openness', 
            'Actions / flexibility': 'Openness', 'Ideas': 'Openness', 'Values / learning': 'Openness',
            'Trust': 'Agreeableness', 'Straightforwardness': 'Agreeableness', 'Altruism': 'Agreeableness', 
            'Compliance': 'Agreeableness', 'Modesty': 'Agreeableness', 'Tender-mindedness': 'Agreeableness',
            'Competence': 'Conscientiousness', 'Order': 'Conscientiousness', 'Dutifulness': 'Conscientiousness', 
            'Achievement striving': 'Conscientiousness', 'Self-discipline': 'Conscientiousness', 'Deliberation': 'Conscientiousness'
        }

        # שליפת השמות של החוזקה והחולשה מתוך הרשימה הממוינת שעשינו בלשונית הקודמת
        top_facet_name = sorted_all_facets[0]['name'] if sorted_all_facets else "Unknown"
        top_facet_val = sorted_all_facets[0]['val'] if sorted_all_facets else 0
        lowest_facet_name = sorted_all_facets[-1]['name'] if sorted_all_facets else "Unknown"
        lowest_facet_val = sorted_all_facets[-1]['val'] if sorted_all_facets else 0

        # מציאת קטגוריית ה-Big 5 של החולשה המרכזית והציון שלה
        parent_big5_name = facet_to_big5_map.get(lowest_facet_name, "Unknown Trait")
        parent_big5_val = player_data.get(f'Big 5: {parent_big5_name} %_num', 0)

        # הרכבת המחרוזת החדשה של ה-Risk
        # לדוגמה: "Emotional Stability (49) - Trust (25)"
        risk_display_text = f"{parent_big5_name} ({int(parent_big5_val)}) - {lowest_facet_name}"


        # --- הכנת שאר הנתונים לדיווח ---
        es_base = player_data.get('Big 5: Emotional Stability %_num', 50)
        anger_ctrl = get_clean_float('Facet: Anger Control %')
        impulse_ctrl = get_clean_float('Facet: Impulse Control %')
        composure_score = int((es_base + anger_ctrl + impulse_ctrl) / 3) if anger_ctrl > 0 else int(es_base)

        comm_style = player_data.get('Primary_EN', 'Task-Oriented')
        recommended_action = COACHING_GUIDE.get(comm_style, COACHING_GUIDE['Task-Oriented'])['dos'][0]

        mti_score = player_data.get('Score: MTI', 0)
        if mti_score >= 65 and composure_score >= 60:
            pressure_fit = "<span style='color:#10B981; font-weight:bold;'>Strong</span>"
        elif mti_score < 50 or composure_score < 50:
            pressure_fit = "<span style='color:#EF4444; font-weight:bold;'>Needs Support</span>"
        else:
            pressure_fit = "<span style='color:#3B82F6; font-weight:bold;'>Moderate</span>"

        

        role_suitability = "Versatile / Utility Player"
        if 'Activity' in top_facet_name or 'Dutifulness' in top_facet_name:
            role_suitability = "LDM / RDM (Defensive Midfielder)"
        elif 'Assertiveness' in top_facet_name or 'Achievement striving' in top_facet_name:
            role_suitability = "CF (Center Forward / Striker)"
        elif 'Game vision' in top_facet_name or 'Imagination' in top_facet_name:
            role_suitability = "LAM (Attacking Midfielder / Winger)"
        elif 'Order' in top_facet_name or 'Compliance' in top_facet_name:
            role_suitability = "LCB / RCB (Center Back)"

        consistency_val = player_data.get('Passes accurate, %', 0)
        if isinstance(consistency_val, str):
            consistency_val = float(consistency_val.replace('%', '').strip())
        if consistency_val > 0 and consistency_val <= 1.0:
            consistency_val *= 100
        
        total_actions = sum([
            pd.to_numeric(player_data.get('Passes', 0), errors='coerce'),
            pd.to_numeric(player_data.get('Ball recoveries', 0), errors='coerce'),
            pd.to_numeric(player_data.get('Defensive challenges', 0), errors='coerce')
        ])
        total_actions = total_actions if not pd.isna(total_actions) else 0

        st.markdown("<br>", unsafe_allow_html=True)
        r1_col1, r1_col2 = st.columns(2)
        r2_col1, r2_col2 = st.columns(2)

        # --- COACH VIEW ---
        with r1_col1:
            st.markdown(f"""<div style='background-color:#F8F9FA; border:1px solid #DEE2E6; border-radius:8px; padding:20px; height:100%;'>
<h4 style='color:#1E3A8A; margin-top:0; border-bottom:2px solid #1E3A8A; padding-bottom:10px;'>👔 Coach View</h4>
<div style='margin-bottom:15px;'>
<span style='font-size:12px; color:#6C757D; text-transform:uppercase; font-weight:bold;'>Today Status</span><br>
<span style='font-size:16px; color:#343A40;'><strong>Composure:</strong> 
<span style='background-color:#E9ECEF; padding:2px 8px; border-radius:12px; font-weight:bold;'>{composure_score}/100</span>
</span>
</div>
<div style='margin-bottom:15px; padding:10px; background-color:#FFF3CD; border-left:4px solid #FFC107; border-radius:4px;'>
<span style='font-size:12px; color:#856404; text-transform:uppercase; font-weight:bold;'>Main Risk</span><br>
<span style='color:#856404;'><strong>{risk_display_text}</strong></span>
</div>
<div style='margin-bottom:10px;'>
<span style='font-size:12px; color:#6C757D; text-transform:uppercase; font-weight:bold;'>Communication Approach</span><br>
<span style='font-size:15px; font-weight:bold; color:#1E3A8A;'>{comm_style}</span>
</div>
<div>
<span style='font-size:12px; color:#6C757D; text-transform:uppercase; font-weight:bold;'>Recommended Action</span><br>
<span style='font-size:14px; color:#2E7D32;'>✔️ {recommended_action}</span>
</div>
</div>""", unsafe_allow_html=True)

        # --- SCOUT VIEW ---
        with r1_col2:
            st.markdown(f"""<div style='background-color:#F8F9FA; border:1px solid #DEE2E6; border-radius:8px; padding:20px; height:100%;'>
<h4 style='color:#1E3A8A; margin-top:0; border-bottom:2px solid #1E3A8A; padding-bottom:10px;'>🔍 Scout View</h4>
<div style='display:flex; justify-content:space-between; margin-bottom:15px; border-bottom:1px solid #E9ECEF; padding-bottom:10px;'>
<div><span style='font-size:12px; color:#6C757D; text-transform:uppercase; font-weight:bold;'>Pressure Fit</span><br>{pressure_fit}</div>
<div style='text-align:right;'><span style='font-size:12px; color:#6C757D; text-transform:uppercase; font-weight:bold;'>Consistency (Pass Acc)</span><br><span style='font-weight:bold; font-size:16px;'>{consistency_val:.1f}%</span></div>
</div>
<div style='margin-bottom:15px;'>
<span style='font-size:12px; color:#6C757D; text-transform:uppercase; font-weight:bold;'>Risk Profile (Mental Load)</span><br>
<div style='display:flex; gap:10px; margin-top:5px;'>
<span style='background-color:#EBF5FF; color:#1E3A8A; padding:4px 8px; border-radius:4px; font-size:12px;'><strong>IMP:</strong> {player_data.get('Score: IMP', 0)}</span>
<span style='background-color:#EBF5FF; color:#1E3A8A; padding:4px 8px; border-radius:4px; font-size:12px;'><strong>MTI:</strong> {mti_score}</span>
<span style='background-color:#EBF5FF; color:#1E3A8A; padding:4px 8px; border-radius:4px; font-size:12px;'><strong>PPS:</strong> {player_data.get('Score: PPS', 0)}</span>
</div>
</div>
<div style='margin-bottom:15px;'>
<span style='font-size:12px; color:#6C757D; text-transform:uppercase; font-weight:bold;'>Role Suitability Indicator</span><br>
<span style='font-size:15px; font-weight:bold; color:#495057;'>{role_suitability}</span>
</div>
<div style='padding:10px; background-color:#E8F5E9; border-left:4px solid #2E7D32; border-radius:4px;'>
<span style='font-size:12px; color:#1B5E20; text-transform:uppercase; font-weight:bold;'>Key Strength</span><br>
<span style='color:#1B5E20;'><strong>{top_facet_name} ({top_facet_val:.1f})</strong></span>
</div>
</div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True) 

        # --- PLAYER VIEW ---
        with r2_col1:
            player_tip = PLAYER_TIPS.get(lowest_facet_name, "Focus on consistent effort and communicating with the coaching staff.")
            st.markdown(f"""<div style='background-color:#F8F9FA; border:1px solid #DEE2E6; border-radius:8px; padding:20px; height:100%;'>
<h4 style='color:#1E3A8A; margin-top:0; border-bottom:2px solid #1E3A8A; padding-bottom:10px;'>👤 Player View</h4>
<div style='margin-bottom:15px;'>
<span style='font-size:12px; color:#6C757D; text-transform:uppercase; font-weight:bold;'>Your Top Strength</span><br>
<span style='font-size:16px; color:#10B981; font-weight:bold;'>{top_facet_name} ({top_facet_val:.1f})</span>
</div>
<div style='margin-bottom:15px;'>
<span style='font-size:12px; color:#6C757D; text-transform:uppercase; font-weight:bold;'>One Improvement Focus</span><br>
<span style='font-size:16px; color:#EF4444; font-weight:bold;'>{lowest_facet_name} ({lowest_facet_val:.1f})</span>
</div>
<div style='padding:15px; background-color:#F8F9FA; border:1px solid #CED4DA; border-radius:6px; font-style:italic; color:#495057;'>
<span style='font-size:11px; color:#ADB5BD; text-transform:uppercase; font-weight:bold; display:block; margin-bottom:5px; font-style:normal;'>💡 What helps performance (Tip):</span>
"{player_tip}"
</div>
</div>""", unsafe_allow_html=True)

        # --- ANALYST VIEW ---
        with r2_col2:
            st.markdown(f"""<div style='background-color:#F8F9FA; border:1px solid #DEE2E6; border-radius:8px; padding:20px; height:100%;'>
<h4 style='color:#1E3A8A; margin-top:0; border-bottom:2px solid #1E3A8A; padding-bottom:10px;'>📊 Analyst View</h4>
<div style='margin-bottom:20px;'>
<span style='font-size:12px; color:#6C757D; text-transform:uppercase; font-weight:bold;'>Model Confidence Baseline</span><br>
<div style='margin-top:5px;'>
<span style='font-size:24px; font-weight:bold; color:#343A40;'>High</span>
<span style='font-size:14px; color:#6C757D; margin-left:10px;'>(Based on Machine Learning output)</span>
</div>
</div>
<div style='margin-bottom:15px;'>
<span style='font-size:12px; color:#6C757D; text-transform:uppercase; font-weight:bold;'>Database Reference</span><br>
<span style='font-size:16px; color:#1E3A8A; font-weight:bold;'>{len(df)} Squad Members Analyzed</span>
</div>
<div>
<span style='font-size:12px; color:#6C757D; text-transform:uppercase; font-weight:bold;'>Sample Size (Actions Logged)</span><br>
<span style='font-size:16px; color:#495057; font-weight:bold;'>~{int(total_actions) if total_actions > 0 else "N/A"} key technical events</span>
</div>
</div>""", unsafe_allow_html=True)



