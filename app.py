import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random

# --- CONFIG ---
st.set_page_config(
    page_title="GLAR REVISION HUB",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- THEME CSS PREMIUM ---
CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@600;700&display=swap');

:root {
  --primary: #064E3B;
  --primary-soft: #10B981;
  --primary-light: #ECFDF5;
  --accent: #D4AF37;
  --accent-soft: #FEF9E7;
  --bg: #F8FAFC;
  --card: #FFFFFF;
  --border: #E2E8F0;
  --text: #0F172A;
  --text-sec: #64748B;
  --shadow: 0 1px 2px rgba(15,23,42,0.04), 0 4px 12px rgba(15,23,42,0.06);
  --shadow-hover: 0 4px 12px rgba(15,23,42,0.08), 0 16px 32px rgba(15,23,42,0.08);
  --radius: 16px;
  --radius-sm: 12px;
}

html, body, [class*="css"] {
  font-family: 'Inter', -apple-system, sans-serif;
}

[data-testid="stAppViewContainer"] {
  background: var(--bg);
}

[data-testid="stSidebar"] {
  background: var(--card) !important;
  border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] > div:first-child {
  padding-top: 1.5rem;
}

.glar-logo {
  display:flex; align-items:center; gap:12px; padding: 0 8px 24px 8px; border-bottom: 1px solid var(--border); margin-bottom: 20px;
}
.glar-logo-mark {
  width:44px; height:44px; background: linear-gradient(135deg, #064E3B 0%, #10B981 100%);
  border-radius: 12px; display:flex; align-items:center; justify-content:center;
  color:white; font-family:'Plus Jakarta Sans'; font-weight:700; font-size:20px; box-shadow: 0 4px 12px rgba(16,185,129,0.3);
}
.glar-logo-text { line-height:1.1 }
.glar-logo-text b { font-family:'Plus Jakarta Sans'; font-size:16px; color:var(--text); letter-spacing:-0.02em }
.glar-logo-text span { font-size:11px; color:var(--text-sec); letter-spacing:0.12em; text-transform:uppercase; font-weight:600 }

.glar-nav-item {
  display:flex; align-items:center; gap:12px; padding:10px 12px; border-radius:10px;
  color: var(--text-sec); font-size:14px; font-weight:500; cursor:pointer; transition: all .18s ease;
  margin-bottom: 4px;
}
.glar-nav-item:hover { background: #F1F5F9; color: var(--text); }
.glar-nav-item.active { background: var(--primary); color: white !important; box-shadow: 0 4px 12px rgba(6,78,59,0.25); }
.glar-nav-item.active svg { stroke: white !important; }

.glar-card {
  background: var(--card); border: 1px solid var(--border); border-radius: var(--radius);
  box-shadow: var(--shadow); padding: 20px; transition: all .2s ease;
}
.glar-card:hover { box-shadow: var(--shadow-hover); transform: translateY(-1px); }
.glar-stat {
  background: var(--card); border: 1px solid var(--border); border-radius: var(--radius);
  padding: 20px; box-shadow: var(--shadow); display:flex; flex-direction:column; gap:12px;
}
.glar-stat-top { display:flex; justify-content:space-between; align-items:flex-start }
.glar-stat-icon { width:40px; height:40px; border-radius:10px; display:flex; align-items:center; justify-content:center; font-size:18px }
.glar-stat-value { font-family:'Plus Jakarta Sans'; font-size:28px; font-weight:700; color:var(--text); letter-spacing:-0.03em; line-height:1 }
.glar-stat-label { font-size:13px; color:var(--text-sec); font-weight:500 }
.glar-stat-trend { font-size:12px; font-weight:600; padding:4px 8px; border-radius:20px; }

.glar-welcome {
  background: linear-gradient(105deg, #064E3B 0%, #0A684F 55%, #10B981 100%);
  border-radius: 20px; padding: 28px 32px; color:white; position:relative; overflow:hidden;
}
.glar-welcome::after {
  content:""; position:absolute; right:-40px; top:-40px; width:200px; height:200px;
  background: radial-gradient(circle, rgba(212,175,55,0.25) 0%, transparent 70%); border-radius:50%;
}
.glar-progress { height:6px; background:#E2E8F0; border-radius:20px; overflow:hidden }
.glar-progress-bar { height:100%; border-radius:20px; background: linear-gradient(90deg, var(--primary), var(--primary-soft)); transition: width .6s ease }

.subject-card {
  background: white; border: 1px solid var(--border); border-radius:16px; padding:18px;
  box-shadow: var(--shadow); transition: .22s ease; height:100%; display:flex; flex-direction:column; gap:12px;
}
.subject-card:hover { box-shadow: var(--shadow-hover); transform: translateY(-2px); border-color: #CBD5E1 }

.quiz-option {
  border: 1.5px solid var(--border); border-radius:12px; padding:14px 16px; background:white;
  cursor:pointer; transition:.15s; display:flex; gap:12px; align-items:center;
}
.quiz-option:hover { border-color: var(--primary-soft); background: #F0FDF4 }
.quiz-option.selected { border-color: var(--primary); background: #ECFDF5; box-shadow: 0 0 0 3px rgba(16,185,129,0.15) }

div[data-testid="stButton"] > button {
  background: var(--primary) !important; color:white !important; border-radius:10px !important;
  font-weight:600 !important; border:none !important; padding:10px 18px !important;
  transition: .18s !important; box-shadow: 0 4px 12px rgba(6,78,59,0.2) !important;
}
div[data-testid="stButton"] > button:hover { transform: translateY(-1px); box-shadow: 0 8px 20px rgba(6,78,59,0.25) !important }

.glar-empty { text-align:center; padding:48px 24px; color:var(--text-sec); background:white; border:1px dashed var(--border); border-radius:16px }

/* Hide default streamlit menu */
#MainMenu, footer {visibility: hidden;}
</style>
"""

st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)

# --- DATA ---
SUBJECTS = [
    {"id":"math","name":"Mathématiques","desc":"Algèbre, analyse et géométrie","chapters":24,"progress":68,"icon":"∑","color":"#ECFDF5","icon_bg":"#D1FAE5"},
    {"id":"phys","name":"Physique-Chimie","desc":"Mécanique, ondes et chimie","chapters":18,"progress":42,"icon":"◐","color":"#EFF6FF","icon_bg":"#DBEAFE"},
    {"id":"svt","name":"SVT","desc":"Vivant, terre et environnement","chapters":16,"progress":81,"icon":"✿","color":"#F0FDF4","icon_bg":"#BBF7D0"},
    {"id":"fr","name":"Français","desc":"Littérature et méthodologie","chapters":14,"progress":55,"icon":"✒","color":"#FEF9E7","icon_bg":"#FDE68A"},
    {"id":"philo","name":"Philosophie","desc":"Concepts et dissertations","chapters":12,"progress":33,"icon":"◑","color":"#F5F3FF","icon_bg":"#DDD6FE"},
    {"id":"hist","name":"Histoire-Géo","desc":"Monde contemporain","chapters":20,"progress":74,"icon":"◎","color":"#FFF7ED","icon_bg":"#FED7AA"},
]

if "page" not in st.session_state: st.session_state.page = "Tableau de bord"
if "quiz_idx" not in st.session_state: st.session_state.quiz_idx = 0
if "quiz_answers" not in st.session_state: st.session_state.quiz_answers = {}
if "quiz_show_result" not in st.session_state: st.session_state.quiz_show_result = False
if "selected_subject" not in st.session_state: st.session_state.selected_subject = None

QUIZ_DATA = [
    {"q":"Quelle est la dérivée de f(x)=x² ?","opts":["2x","x","2x²","0"],"correct":0,"exp":"La dérivée de x^n est n·x^(n-1)."},
    {"q":"En physique, quelle unité mesure la force ?","opts":["Joule","Newton","Watt","Pascal"],"correct":1,"exp":"Le Newton (N) est l'unité de force dans le SI."},
    {"q":"Quelle figure de style : 'Je meurs de faim' ?","opts":["Métaphore","Hyperbole","Oxymore","Anaphore"],"correct":1,"exp":"Exagération volontaire pour insister."},
]

# --- SIDEBAR NAV PREMIUM ---
with st.sidebar:
    st.markdown("""
    <div class="glar-logo">
      <div class="glar-logo-mark">G</div>
      <div class="glar-logo-text"><b>GLAR REVISION</b><br><span>Hub Premium</span></div>
    </div>
    """, unsafe_allow_html=True)

    menu = [
        ("Tableau de bord","◫"),("Mes matières","◎"),("Mes cours","≡"),("Fiches de révision","◰"),
        ("Quiz et QCM","◐"),("Exercices pratiques","◑"),("Flashcards","⧉"),("Planning","◷"),("Statistiques","⟐"),("Paramètres","⚙")
    ]
    for label, icon in menu:
        active = "active" if st.session_state.page==label else ""
        if st.button(f"{icon}  {label}", key=f"nav_{label}", use_container_width=True):
            st.session_state.page = label
            st.rerun()

    st.markdown('<div style="margin-top:24px;padding:16px;background:#F8FAFC;border-radius:12px;border:1px solid #E2E8F0">', unsafe_allow_html=True)
    st.markdown('<div style="font-size:12px;font-weight:600;color:#64748B;margin-bottom:8px">OBJECTIF BAC 2026</div>', unsafe_allow_html=True)
    st.markdown('<div style="display:flex;justify-content:space-between;font-size:13px;margin-bottom:6px"><span style="color:#0F172A;font-weight:600">68% complété</span><span style="color:#64748B">112j</span></div>', unsafe_allow_html=True)
    st.progress(68)
    st.markdown('</div>', unsafe_allow_html=True)

# --- HELPERS ---
def stat_card(icon, bg, label, value, trend, trend_color="#10B981"):
    st.markdown(f"""
    <div class="glar-stat">
      <div class="glar-stat-top">
        <div class="glar-stat-icon" style="background:{bg}">{icon}</div>
        <div class="glar-stat-trend" style="background:{trend_color}15;color:{trend_color}">{trend}</div>
      </div>
      <div>
        <div class="glar-stat-value">{value}</div>
        <div class="glar-stat-label">{label}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

def subject_card_html(s):
    return f"""
    <div class="subject-card">
      <div style="display:flex;justify-content:space-between;align-items:flex-start">
        <div style="width:44px;height:44px;border-radius:12px;background:{s['icon_bg']};display:flex;align-items:center;justify-content:center;font-size:20px">{s['icon']}</div>
        <span style="font-size:11px;font-weight:600;padding:4px 8px;border-radius:20px;background:#F1F5F9;color:#64748B">{s['chapters']} chapitres</span>
      </div>
      <div>
        <div style="font-weight:700;color:#0F172A;font-size:15px;margin-bottom:2px">{s['name']}</div>
        <div style="font-size:13px;color:#64748B">{s['desc']}</div>
      </div>
      <div style="margin-top:auto">
        <div style="display:flex;justify-content:space-between;font-size:12px;margin-bottom:6px"><span style="color:#64748B">Progression</span><span style="font-weight:700;color:#064E3B">{s['progress']}%</span></div>
        <div class="glar-progress"><div class="glar-progress-bar" style="width:{s['progress']}%"></div></div>
      </div>
    </div>
    """

# --- PAGES ---
page = st.session_state.page

if page == "Tableau de bord":
    # Header
    col1, col2 = st.columns([2.2,0.8])
    with col1:
        st.markdown(f"""
        <div style="margin-bottom:18px">
          <h1 style="font-family:'Plus Jakarta Sans';font-size:32px;font-weight:700;letter-spacing:-0.03em;color:#0F172A;margin:0">Bon retour, Alex 👋</h1>
          <p style="color:#64748B;font-size:15px;margin-top:6px">Tu as révisé 4 chapitres cette semaine. On continue sur cette lancée ?</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div style='text-align:right;padding-top:8px'><span style='font-size:12px;color:#64748B'>{datetime.now().strftime('%A %d %B %Y').capitalize()}</span></div>", unsafe_allow_html=True)

    # Welcome objective
    st.markdown("""
    <div class="glar-welcome">
      <div style="position:relative;z-index:2;display:flex;justify-content:space-between;align-items:center;gap:24px;flex-wrap:wrap">
        <div>
          <div style="display:inline-flex;gap:8px;align-items:center;background:rgba(255,255,255,0.15);padding:6px 12px;border-radius:20px;font-size:11px;font-weight:700;letter-spacing:0.08em;margin-bottom:12px">● OBJECTIF DU JOUR</div>
          <h3 style="margin:0;font-family:'Plus Jakarta Sans';font-size:20px;font-weight:700;line-height:1.2">Maîtriser les suites numériques<br>et réussir le QCM Chapitre 8</h3>
          <p style="margin:10px 0 0 0;opacity:0.9;font-size:13px">20 min • Mathématiques • Priorité haute</p>
        </div>
        <div style="background:white;color:#064E3B;padding:10px 18px;border-radius:10px;font-weight:700;font-size:14px;box-shadow:0 4px 12px rgba(0,0,0,0.15)">▶ Reprendre</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.write("")
    # Stats
    c1,c2,c3,c4 = st.columns(4)
    with c1: stat_card("◷","#ECFDF5","Temps de révision","12h 34m","↑ 18%","#10B981")
    with c2: stat_card("⟐","#FEF9E7","Score moyen","76%","↑ 4,2%","#D4AF37")
    with c3: stat_card("✓","#EFF6FF","Quiz réussis","42/56","→ stable","#3B82F6")
    with c4: stat_card("◫","#F5F3FF","Série en cours","7 jours","🔥 meilleur","#8B5CF6")

    st.write("")
    left,right = st.columns([1.6,1])

    with left:
        # Graph modern
        st.markdown('<div class="glar-card">', unsafe_allow_html=True)
        st.markdown('<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px"><h4 style="margin:0;font-size:16px;font-weight:700;color:#0F172A">Évolution des résultats</h4><span style="font-size:12px;color:#64748B;background:#F8FAFC;padding:4px 10px;border-radius:20px;border:1px solid #E2E8F0">30 derniers jours</span></div>', unsafe_allow_html=True)
        dates = [datetime.now()-timedelta(days=i) for i in range(29,-1,-1)]
        vals = [58+ i*0.6 + random.uniform(-4,6) for i in range(30)]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=dates, y=vals, mode='lines', line=dict(color='#064E3B', width=2.5, shape='spline'), fill='tozeroy', fillcolor='rgba(16,185,129,0.08)', hoverinfo='skip'))
        fig.update_layout(height=220, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(showgrid=False, showticklabels=False), yaxis=dict(showgrid=True, gridcolor='#F1F5F9', showticklabels=False), showlegend=False)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar':False})
        st.markdown('</div>', unsafe_allow_html=True)

        st.write("")
        st.markdown('<h4 style="font-size:16px;font-weight:700;color:#0F172A;margin-bottom:12px">Reprendre mes révisions</h4>', unsafe_allow_html=True)
        recents = [
            {"title":"Suites arithmétiques - Exercices","mat":"Mathématiques","time":"il y a 2h","prog":60},
            {"title":"La photosynthèse - Fiche","mat":"SVT","time":"hier","prog":100},
            {"title":"Les Lumières - QCM","mat":"Français","time":"il y a 3j","prog":25},
        ]
        for r in recents:
            st.markdown(f"""
            <div class="glar-card" style="display:flex;justify-content:space-between;align-items:center;padding:16px 20px;margin-bottom:10px">
              <div style="display:flex;gap:14px;align-items:center">
                <div style="width:44px;height:44px;border-radius:10px;background:#F8FAFC;border:1px solid #E2E8F0;display:flex;align-items:center;justify-content:center">▶</div>
                <div><div style="font-weight:600;font-size:14px;color:#0F172A">{r['title']}</div><div style="font-size:12px;color:#64748B">{r['mat']} • {r['time']}</div></div>
              </div>
              <div style="display:flex;gap:12px;align-items:center"><div class="glar-progress" style="width:80px"><div class="glar-progress-bar" style="width:{r['prog']}%"></div></div><span style="font-size:12px;font-weight:700;color:#064E3B">{r['prog']}%</span></div>
            </div>
            """, unsafe_allow_html=True)

    with right:
        st.markdown('<h4 style="font-size:16px;font-weight:700;color:#0F172A;margin-bottom:12px">Objectifs du jour</h4>', unsafe_allow_html=True)
        st.markdown("""
        <div class="glar-card" style="padding:18px">
          <div style="display:flex;justify-content:space-between;margin-bottom:12px"><span style="font-weight:600;font-size:14px">3 tâches</span><span style="font-size:12px;color:#10B981;font-weight:700">2/3 faites</span></div>
          <div class="glar-progress" style="height:8px;margin-bottom:16px"><div class="glar-progress-bar" style="width:66%"></div></div>
          <div style="display:flex;flex-direction:column;gap:10px">
            <div style="display:flex;gap:10px;align-items:center;font-size:13px"><span style="width:20px;height:20px;border-radius:50%;background:#10B981;color:white;display:flex;align-items:center;justify-content:center;font-size:11px">✓</span><span style="color:#0F172A;font-weight:500">Réviser 1 fiche de maths</span></div>
            <div style="display:flex;gap:10px;align-items:center;font-size:13px"><span style="width:20px;height:20px;border-radius:50%;background:#10B981;color:white;display:flex;align-items:center;justify-content:center;font-size:11px">✓</span><span style="color:#0F172A;font-weight:500">Faire le QCM Chapitre 7</span></div>
            <div style="display:flex;gap:10px;align-items:center;font-size:13px"><span style="width:20px;height:20px;border-radius:50%;border:1.5px solid #E2E8F0"></span><span style="color:#64748B">20 min d'exercices SVT</span></div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.write("")
        st.markdown('<h4 style="font-size:16px;font-weight:700;color:#0F172A;margin-bottom:12px">Recommandations</h4>', unsafe_allow_html=True)
        st.markdown("""
        <div style="display:flex;flex-direction:column;gap:10px">
          <div class="glar-card" style="border-left:3px solid #D4AF37"><div style="font-size:12px;font-weight:700;color:#D4AF37;letter-spacing:0.06em;margin-bottom:4px">PRIORITÉ</div><div style="font-weight:600;font-size:13px;color:#0F172A">Renforce la Physique : -12% vs moyenne</div><div style="font-size:12px;color:#64748B;margin-top:4px">Fais 2 quiz ciblés pour remonter.</div></div>
          <div class="glar-card" style="border-left:3px solid #10B981"><div style="font-size:12px;font-weight:700;color:#10B981;letter-spacing:0.06em;margin-bottom:4px">OPPORTUNITÉ</div><div style="font-weight:600;font-size:13px;color:#0F172A">Excellente série en SVT</div><div style="font-size:12px;color:#64748B;margin-top:4px">Continue pour débloquer le badge Expert.</div></div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    st.markdown('<h4 style="font-size:18px;font-weight:700;color:#0F172A;margin:12px 0">Mes matières</h4>', unsafe_allow_html=True)
    cols = st.columns(3)
    for i,s in enumerate(SUBJECTS):
        with cols[i%3]:
            st.markdown(subject_card_html(s), unsafe_allow_html=True)
            if st.button("Ouvrir →", key=f"open_{s['id']}", use_container_width=True):
                st.session_state.page="Mes matières"
                st.session_state.selected_subject=s['id']
                st.rerun()
            st.write("")

elif page == "Mes matières":
    st.markdown("<h1 style=\"font-family:'Plus Jakarta Sans';font-size:28px;font-weight:700;letter-spacing:-0.03em;color:#0F172A\">Mes matières</h1><p style='color:#64748B'>Choisis une matière pour accéder aux cours, fiches et quiz.</p>", unsafe_allow_html=True)
    st.write("")
    cols = st.columns(3)
    for i,s in enumerate(SUBJECTS):
        with cols[i%3]:
            st.markdown(subject_card_html(s), unsafe_allow_html=True)
            c1,c2 = st.columns(2)
            with c1:
                if st.button("Cours", key=f"cours_{s['id']}", use_container_width=True): st.session_state.page="Mes cours"; st.rerun()
            with c2:
                if st.button("Quiz", key=f"quiz_{s['id']}_btn", use_container_width=True): st.session_state.page="Quiz et QCM"; st.rerun()
            st.write("")

elif page == "Quiz et QCM":
    st.markdown("<h1 style=\"font-family:'Plus Jakarta Sans';font-size:28px;font-weight:700;color:#0F172A\">Quiz et QCM</h1>", unsafe_allow_html=True)
    idx = st.session_state.quiz_idx
    total = len(QUIZ_DATA)

    if not st.session_state.quiz_show_result:
        # Progress visual
        pct = int((idx/total)*100) if total else 0
        st.markdown(f"""
        <div class="glar-card" style="margin:16px 0">
          <div style="display:flex;justify-content:space-between;margin-bottom:8px"><span style="font-size:13px;font-weight:600;color:#0F172A">Question {idx+1} sur {total}</span><span style="font-size:12px;color:#64748B">{total-idx} restantes • ⏱ 12:34</span></div>
          <div class="glar-progress" style="height:8px"><div class="glar-progress-bar" style="width:{pct}%"></div></div>
        </div>
        """, unsafe_allow_html=True)

        q = QUIZ_DATA[idx]
        st.markdown(f"<div class='glar-card' style='padding:28px'><h3 style='font-size:18px;font-weight:700;color:#0F172A;margin:0 0 20px 0'>{q['q']}</h3>", unsafe_allow_html=True)
        selected = st.session_state.quiz_answers.get(idx)
        for j,opt in enumerate(q["opts"]):
            is_sel = "selected" if selected==j else ""
            st.markdown(f"<div class='quiz-option {is_sel}' style='margin-bottom:10px'><div style='width:28px;height:28px;border-radius:50%;border:1.5px solid #E2E8F0;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:700;background:white'>{chr(65+j)}</div><div style='font-size:14px;font-weight:500;color:#0F172A'>{opt}</div></div>", unsafe_allow_html=True)
            if st.button(f"Choisir {chr(65+j)}", key=f"q{idx}_{j}", use_container_width=False):
                st.session_state.quiz_answers[idx]=j
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        st.write("")
        c1,c2 = st.columns([1,1])
        with c1:
            if st.button("← Précédent", disabled=(idx==0)):
                st.session_state.quiz_idx = max(0, idx-1); st.rerun()
        with c2:
            if selected is not None:
                if idx < total-1:
                    if st.button("Valider et continuer →", type="primary", use_container_width=True):
                        st.session_state.quiz_idx+=1; st.rerun()
                else:
                    if st.button("Voir mes résultats ✨", type="primary", use_container_width=True):
                        st.session_state.quiz_show_result=True; st.rerun()
    else:
        score = sum(1 for i in range(total) if st.session_state.quiz_answers.get(i)==QUIZ_DATA[i]["correct"])
        pct_score = int(score/total*100)
        st.markdown(f"""
        <div class="glar-card" style="text-align:center;padding:36px;background: linear-gradient(180deg, #FFFFFF 0%, #F8FAFC 100%)">
          <div style="width:80px;height:80px;border-radius:50%;background:linear-gradient(135deg,#064E3B,#10B981);display:flex;align-items:center;justify-content:center;margin:0 auto 16px auto;color:white;font-size:36px">★</div>
          <h2 style="font-family:'Plus Jakarta Sans';font-size:28px;font-weight:700;color:#0F172A;margin:0">Score : {pct_score}%</h2>
          <p style="color:#64748B;margin:8px 0 20px 0">{score} bonnes réponses sur {total} • Temps : 4m 12s</p>
          <div style="display:flex;gap:12px;justify-content:center;flex-wrap:wrap">
            <span style="padding:8px 14px;border-radius:20px;background:#ECFDF5;color:#064E3B;font-weight:600;font-size:13px">+42 XP gagnés</span>
            <span style="padding:8px 14px;border-radius:20px;background:#FEF9E7;color:#92400E;font-weight:600;font-size:13px">Badge : Logique</span>
          </div>
        </div>
        """, unsafe_allow_html=True)
        st.write("")
        for i,q in enumerate(QUIZ_DATA):
            ok = st.session_state.quiz_answers.get(i)==q["correct"]
            st.markdown(f"""
            <div class="glar-card" style="border-left:3px solid {'#10B981' if ok else '#EF4444'};margin-bottom:12px">
              <div style="display:flex;gap:10px;align-items:flex-start"><span style="font-weight:700;color:{'#10B981' if ok else '#EF4444'}">{'✓' if ok else '✗'}</span>
              <div><div style="font-weight:600;font-size:14px;color:#0F172A">{q['q']}</div><div style="font-size:13px;color:#64748B;margin-top:6px">Ta réponse : <b>{q['opts'][st.session_state.quiz_answers.get(i,0)]}</b> • Bonne réponse : <b style='color:#064E3B'>{q['opts'][q['correct']]}</b><br><span style="color:#0F172A;background:#F8FAFC;padding:4px 8px;border-radius:6px;display:inline-block;margin-top:6px">💡 {q['exp']}</span></div></div></div>
            </div>
            """, unsafe_allow_html=True)
        if st.button("Recommencer le quiz", use_container_width=True):
            st.session_state.quiz_idx=0; st.session_state.quiz_answers={}; st.session_state.quiz_show_result=False; st.rerun()

else:
    # Pages génériques premium
    titles = {
        "Mes cours":"Mes cours","Fiches de révision":"Fiches de révision","Exercices pratiques":"Exercices pratiques",
        "Flashcards":"Flashcards","Planning":"Planning","Statistiques":"Statistiques","Paramètres":"Paramètres"
    }
    t = titles.get(page, page)
    st.markdown(f"<h1 style=\"font-family:'Plus Jakarta Sans';font-size:28px;font-weight:700;color:#0F172A\">{t}</h1>", unsafe_allow_html=True)
    st.write("")
    if page=="Mes cours":
        for s in SUBJECTS[:3]:
            st.markdown(f"<div class='glar-card' style='display:flex;justify-content:space-between;align-items:center;margin-bottom:12px'><div style='display:flex;gap:14px;align-items:center'><div style='width:48px;height:48px;border-radius:12px;background:{s['icon_bg']};display:flex;align-items:center;justify-content:center'>{s['icon']}</div><div><div style='font-weight:700'>{s['name']} - Chapitre 8</div><div style='font-size:12px;color:#64748B'>Cours vidéo • 18 min • Complété à {s['progress']}%</div></div></div><div>▶</div></div>", unsafe_allow_html=True)
    elif page=="Statistiques":
        c1,c2 = st.columns(2)
        with c1:
            st.markdown('<div class="glar-card">', unsafe_allow_html=True)
            st.markdown("**Répartition par matière**")
            df = pd.DataFrame({"Matière":[s["name"] for s in SUBJECTS], "Score":[68,42,81,55,33,74]})
            fig = go.Figure(go.Bar(x=df["Score"], y=df["Matière"], orientation='h', marker=dict(color=['#064E3B','#0A684F','#10B981','#34D399','#6EE7B7','#A7F3D0'])))
            fig.update_layout(height=260, margin=dict(l=0,r=0,t=10,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(showgrid=True, gridcolor='#F1F5F9'), yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar':False})
            st.markdown('</div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="glar-card"><b>Badges débloqués</b><div style="display:flex;gap:10px;margin-top:16px;flex-wrap:wrap"><span style="padding:10px 14px;border-radius:12px;background:#FEF9E7;border:1px solid #FDE68A">🏆 Série 7j</span><span style="padding:10px 14px;border-radius:12px;background:#ECFDF5;border:1px solid #A7F3D0">🧠 Expert SVT</span><span style="padding:10px 14px;border-radius:12px;background:#EFF6FF;border:1px solid #BFDBFE">📚 Lecteur</span></div></div>', unsafe_allow_html=True)
    elif page=="Paramètres":
        st.markdown("""
        <div class="glar-card" style="max-width:560px">
          <h4 style="margin:0 0 16px 0">Préférences</h4>
          <div style="display:flex;flex-direction:column;gap:16px">
            <div style="display:flex;justify-content:space-between"><span>Thème sombre</span><span style="color:#64748B">Bientôt</span></div>
            <div style="display:flex;justify-content:space-between"><span>Notifications de révision</span><span style="color:#10B981;font-weight:600">Activées</span></div>
            <div style="display:flex;justify-content:space-between"><span>Objectif quotidien</span><span>30 min</span></div>
          </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='glar-empty'><div style='font-size:36px;margin-bottom:12px'>✦</div><div style='font-weight:600;color:#0F172A;margin-bottom:6px'>{t} - bientôt premium</div><div style='font-size:13px'>Cette section est prête pour ton contenu. Ajoute cours, fiches ou exercices et ils apparaîtront ici avec le même design premium.</div></div>", unsafe_allow_html=True)

# Footer
st.markdown("<div style='margin-top:40px;padding:16px 0;border-top:1px solid #E2E8F0;display:flex;justify-content:space-between;font-size:12px;color:#94A3B8'><span>© 2026 GLAR REVISION HUB • Premium Learning Experience</span><span>Emeraude #064E3B • Or #D4AF37</span></div>", unsafe_allow_html=True)
