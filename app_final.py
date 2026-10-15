import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import json, os, base64, time

from database import init_db, fetch_all, fetch_one, execute, get_storage_info
from utils import extract_text_from_pdf, extract_text_from_txt, generate_fiche_auto, calculate_quiz_score, spaced_next_review
from config import APP_NAME, APP_VERSION, SEMESTRES, NIVEAUX_DIFFICULTE, STATUTS_REVISION

st.set_page_config(page_title=APP_NAME, page_icon="🎓", layout="wide", initial_sidebar_state="expanded")

# --- Helpers image ---
def img_to_base64(path):
    try:
        if not os.path.exists(path):
            return ""
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        return ""

# Chemins - supporte assets/ et racine
logo_paths = ["assets/estm_logo.png", "estm_logo.png", "/mnt/data/assets/estm_logo.png", "/mnt/data/estm_logo.png"]
photo_paths = ["assets/Babacar_Mbow.jpg", "Babacar_Mbow.jpg", "/mnt/data/assets/Babacar_Mbow.jpg", "/mnt/data/Babacar_Mbow.jpg"]

def find_existing(paths):
    for p in paths:
        if os.path.exists(p):
            return p
    return paths[0]

logo_path = find_existing(logo_paths)
photo_path = find_existing(photo_paths)
logo_b64 = img_to_base64(logo_path)
photo_b64 = img_to_base64(photo_path)

# --- CSS SPLENDIDE ---
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&family=Plus+Jakarta+Sans:wght@700;800&display=swap');

.stApp {{
    background: 
        radial-gradient(1200px 600px at 10% -10%, #E8F5E9 0%, transparent 60%),
        radial-gradient(1000px 500px at 90% 0%, #FFF8E1 0%, transparent 60%),
        linear-gradient(180deg, #F6F8F3 0%, #FFFFFF 70%);
    font-family: Inter, sans-serif;
}}

/* Sidebar Premium */
section[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, #0A1F15 0%, #12372A 30%, #1B4332 60%, #2D6A4F 100%) !important;
    border-right: 1px solid rgba(212,160,23,0.15);
}}
section[data-testid="stSidebar"] * {{ color: #E8F5E9 !important; }}
section[data-testid="stSidebar"] button {{
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.10) !important;
    border-radius: 14px !important;
    transition: all 0.3s ease !important;
    font-weight: 600 !important;
}}
section[data-testid="stSidebar"] button:hover {{
    background: linear-gradient(135deg, rgba(212,160,23,0.25), rgba(244,211,94,0.15)) !important;
    border-color: #D4A017 !important;
    transform: translateX(4px) scale(1.02);
    box-shadow: 0 6px 20px rgba(212,160,23,0.2);
}}

/* Metrics */
div[data-testid="stMetric"] {{
    background: white !important;
    border-radius: 18px !important;
    border: 1px solid #EDEBE3 !important;
    box-shadow: 0 10px 30px rgba(27,67,50,0.07) !important;
    padding: 18px !important;
    transition: transform 0.2s;
}}
div[data-testid="stMetric"]:hover {{ transform: translateY(-2px); }}

/* Cards */
div[data-testid="stExpander"] {{ border-radius: 16px !important; border: 1px solid #EDEBE3 !important; background: white !important; }}
button[kind="primary"] {{
    background: linear-gradient(135deg, #1B4332 0%, #2D6A4F 100%) !important;
    border-radius: 12px !important;
    box-shadow: 0 8px 20px rgba(27,67,50,0.3) !important;
    font-weight: 700 !important;
}}

/* Badges & Splendide */
.gold-badge {{
    background: linear-gradient(135deg, #D4A017 0%, #F4D35E 50%, #D4A017 100%);
    color: #1B4332;
    padding: 7px 16px;
    border-radius: 24px;
    font-weight: 900;
    font-size: 0.78rem;
    display: inline-block;
    box-shadow: 0 4px 12px rgba(212,160,23,0.3);
    letter-spacing: 0.5px;
    animation: shimmer 3s infinite;
}}
@keyframes shimmer {{ 0%,100% {{ filter: brightness(1); }} 50% {{ filter: brightness(1.15); }} }}

.profile-card-splendide {{
    background: linear-gradient(135deg, #FFFFFF 0%, #F8FFF9 100%);
    border-radius: 20px;
    padding: 20px;
    border: 1.5px solid #E8F5E9;
    box-shadow: 0 12px 32px rgba(27,67,50,0.08), inset 0 1px 0 rgba(255,255,255,0.8);
    display: flex;
    align-items: center;
    gap: 18px;
    position: relative;
    overflow: hidden;
}}
.profile-card-splendide::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 4px;
    background: linear-gradient(90deg, #1B4332, #D4A017, #2D6A4F);
}}
.profile-card-splendide img {{
    width: 88px; height: 88px;
    border-radius: 50%;
    object-fit: cover;
    border: 3px solid #D4A017;
    box-shadow: 0 8px 24px rgba(0,0,0,0.15), 0 0 0 6px rgba(212,160,23,0.12);
}}

/* Watermark permanent */
.watermark-main {{
    position: fixed;
    bottom: 14px;
    right: 18px;
    opacity: 0.85;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 1.1px;
    color: #1B4332;
    z-index: 9999;
    background: rgba(255,255,255,0.92);
    padding: 8px 14px;
    border-radius: 24px;
    border: 1px solid rgba(27,67,50,0.08);
    backdrop-filter: blur(8px);
    box-shadow: 0 6px 20px rgba(0,0,0,0.08);
    display: flex;
    align-items: center;
    gap: 8px;
}}
.watermark-photo-mini {{
    width: 28px; height: 28px;
    border-radius: 50%;
    border: 2px solid #D4A017;
    object-fit: cover;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}}

/* Splash */
.splash-overlay {{
    position: fixed;
    top: 0; left: 0; width: 100vw; height: 100vh;
    background: radial-gradient(1200px 600px at 30% 20%, #2D6A4F 0%, #1B4332 40%, #0F2A1E 100%);
    z-index: 10000;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}}

/* Header logo integration */
.header-with-logo {{
    display: flex;
    align-items: center;
    gap: 14px;
    margin-bottom: 8px;
}}
.header-logo {{
    width: 56px; height: auto;
    filter: drop-shadow(0 4px 12px rgba(27,67,50,0.15));
}}
</style>
""", unsafe_allow_html=True)

init_db()

# Seed si disponible
try:
    from data.seed import seed_all
    seed_all()
except:
    pass

for k,v in [("page","Tableau de bord"),("quiz_answers",{}),("quiz_started",{}),("flash_idx",0),("show_correction",{}),("reveal",False)]:
    if k not in st.session_state:
        st.session_state[k]=v

# === SPLASH SPLENDIDE avec les deux images en base64 ===
if "splash_shown" not in st.session_state:
    st.session_state.splash_shown = False

if not st.session_state.splash_shown:
    splash_placeholder = st.empty()
    with splash_placeholder.container():
        # CSS splash interne avec images intégrées
        st.markdown(f"""
        <style>
        .splash-wrap {{
            position: fixed; top:0; left:0; width:100vw; height:100vh;
            background: linear-gradient(135deg, #0A1F15 0%, #12372A 20%, #1B4332 50%, #2D6A4F 100%);
            z-index: 100000;
            display: flex; flex-direction: column; align-items: center; justify-content: center;
            animation: fadeIn 0.6s ease;
        }}
        .splash-logo-img {{
            width: 160px; filter: brightness(0) invert(1) drop-shadow(0 8px 24px rgba(0,0,0,0.3));
            animation: floatLogo 2.5s ease-in-out infinite;
            margin-bottom: 28px;
        }}
        .splash-photo-wrap {{
            position: relative;
            width: 200px; height: 200px;
        }}
        .splash-photo-img {{
            width: 200px; height: 200px; border-radius: 50%;
            border: 4px solid #D4A017;
            box-shadow: 0 24px 60px rgba(0,0,0,0.45), 0 0 0 10px rgba(212,160,23,0.18), 0 0 40px rgba(212,160,23,0.3);
            object-fit: cover;
            animation: pulsePhoto 2s ease-in-out infinite;
        }}
        .splash-ring {{
            position: absolute; top:-8px; left:-8px; right:-8px; bottom:-8px;
            border: 2px solid rgba(212,160,23,0.3); border-radius: 50%;
            animation: rotateRing 6s linear infinite;
        }}
        @keyframes floatLogo {{ 0%,100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-10px); }} }}
        @keyframes pulsePhoto {{ 0%,100% {{ transform: scale(1); }} 50% {{ transform: scale(1.04); }} }}
        @keyframes rotateRing {{ from {{ transform: rotate(0deg); }} to {{ transform: rotate(360deg); }} }}
        @keyframes fadeIn {{ from {{ opacity:0; }} to {{ opacity:1; }} }}
        </style>
        <div class="splash-wrap">
            <img src="data:image/png;base64,{logo_b64}" class="splash-logo-img" />
            <div class="splash-photo-wrap">
                <div class="splash-ring"></div>
                <img src="data:image/jpeg;base64,{photo_b64}" class="splash-photo-img" />
            </div>
            <h1 style="color:white; font-family:'Plus Jakarta Sans'; font-weight:900; font-size:2.2rem; margin:28px 0 0 0; letter-spacing:1px; text-shadow:0 4px 20px rgba(0,0,0,0.3);">GLAR REVISION HUB</h1>
            <p style="color:#A7D7B0; font-size:1.05rem; margin-top:10px; letter-spacing:0.5px; font-weight:600;">Babacar Mbow • L3 GLAR • ESTM Dakar • 2025-2026</p>
            <div style="background: linear-gradient(135deg, #D4A017 0%, #F4D35E 100%); color:#1B4332; padding:8px 20px; border-radius:24px; font-weight:900; font-size:0.85rem; margin-top:20px; box-shadow:0 8px 24px rgba(212,160,23,0.3);">✨ Chargement de ton cockpit d'excellence...</div>
        </div>
        """, unsafe_allow_html=True)
        time.sleep(2.4)
        st.session_state.splash_shown = True
        splash_placeholder.empty()
        st.rerun()

# === Watermark permanent sur toutes les pages ===
st.markdown(f'''
<div class="watermark-main">
    <img src="data:image/jpeg;base64,{photo_b64}" class="watermark-photo-mini" />
    © BABACAR MBOW • L3 GLAR • ESTM DAKAR • {datetime.now().year} • GLAR HUB v{APP_VERSION}
</div>
''', unsafe_allow_html=True)

# === SIDEBAR SPLENDIDE ===
with st.sidebar:
    # Logo ESTM avec fond blanc arrondi splendide
    if logo_b64:
        st.markdown(f"""
        <div style="background:white; border-radius:18px; padding:12px 14px; display:flex; align-items:center; justify-content:center; box-shadow:0 8px 24px rgba(0,0,0,0.15); margin-bottom:14px; border:1.5px solid rgba(212,160,23,0.2);">
            <img src="data:image/png;base64,{logo_b64}" style="width:110px; height:auto;" />
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("### 🎓 ESTM")
    
    st.markdown(f"""
    <div style="text-align:center; margin-bottom:6px;">
        <div style="font-family:'Plus Jakarta Sans'; font-weight:900; font-size:1.25rem; color:white; letter-spacing:0.5px;">GLAR HUB</div>
        <div style="margin-top:8px;"><span class="gold-badge">✨ L3 GLAR • ESTM DAKAR</span></div>
    </div>
    """, unsafe_allow_html=True)
    st.divider()
    
    pages=["Tableau de bord","Matières","Cours & Documents","Fiches","Quiz & QCM","Exercices","Assistant","Flashcards","Planning","Statistiques"]
    icons=["🏠","📚","📄","📝","❓","💻","🤖","🃏","🗓️","📊"]
    for ic,p in zip(icons,pages):
        if st.button(f"{ic}  {p}", use_container_width=True, key=f"nav_{p}", type="primary" if st.session_state.page==p else "secondary"):
            st.session_state.page=p
            st.rerun()
    st.divider()
    
    # Photo Babacar SPLENDIDE
    if photo_b64:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, rgba(255,255,255,0.08), rgba(255,255,255,0.03)); border-radius:20px; padding:14px; border:1px solid rgba(212,160,23,0.15); backdrop-filter: blur(8px);">
            <div style="position:relative; width:100%; display:flex; justify-content:center;">
                <img src="data:image/jpeg;base64,{photo_b64}" style="width:100%; border-radius:16px; border:2.5px solid #D4A017; box-shadow:0 12px 32px rgba(0,0,0,0.25);" />
                <div style="position:absolute; bottom:-8px; right:12px; background: linear-gradient(135deg, #D4A017, #F4D35E); color:#1B4332; padding:4px 10px; border-radius:12px; font-weight:900; font-size:0.65rem; box-shadow:0 4px 12px rgba(0,0,0,0.2);">ESTM • GLAR</div>
            </div>
            <div style="text-align:center; margin-top:12px;">
                <div style="font-weight:800; font-size:0.95rem; color:white;">Babacar Mbow</div>
                <div style="font-size:0.75rem; color:#A7D7B0; margin-top:2px;">L3 Génie Logiciel &<br/>Admin Réseaux</div>
                <div style="margin-top:10px; display:flex; gap:6px; justify-content:center;">
                    <span style="background:rgba(212,160,23,0.2); border:1px solid rgba(212,160,23,0.3); padding:3px 8px; border-radius:10px; font-size:0.65rem;">💻 Dev</span>
                    <span style="background:rgba(255,255,255,0.08); border:1px solid rgba(255,255,255,0.1); padding:3px 8px; border-radius:10px; font-size:0.65rem;">🌐 Réseaux</span>
                    <span style="background:rgba(255,255,255,0.08); border:1px solid rgba(255,255,255,0.1); padding:3px 8px; border-radius:10px; font-size:0.65rem;">☁️ Cloud</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.caption("Babacar Mbow • L3 GLAR")
    
    try:
        s=get_storage_info()
        st.caption(f"💾 DB {s['size_kb']} KB • ✨ v{APP_VERSION} • Images intégrées")
    except:
        pass

def log_activite(t,d,mid=None,dur=0):
    try:
        execute("INSERT INTO activites(type,description,matiere_id,duree,created_at) VALUES(?,?,?,?,?)",(t,d,mid,dur,datetime.now().isoformat()))
    except:
        pass

page=st.session_state.page

# ==================== PAGES ====================

if page=="Tableau de bord":
    # Header avec logo intégré
    st.markdown(f"""
    <div class="header-with-logo">
        <img src="data:image/png;base64,{logo_b64}" class="header-logo" />
        <div>
            <span class="gold-badge">✨ FINAL SPLENDIDE AVEC TES IMAGES</span>
            <h1 style="margin:6px 0 0 0; font-family:'Plus Jakarta Sans'; font-weight:900; letter-spacing:0.5px;">GLAR REVISION HUB</h1>
            <div style="color:#5A7A6A; font-weight:600; font-size:0.95rem;">Babacar Mbow • L3 Génie Logiciel & Administration Réseaux • ESTM Dakar</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Carte profil SPLENDIDE
    st.markdown(f"""
    <div class="profile-card-splendide" style="margin-top:16px;">
        <img src="data:image/jpeg;base64,{photo_b64}" />
        <div style="flex:1;">
            <div style="display:flex; align-items:center; gap:10px;">
                <h3 style="margin:0; font-weight:900;">👨‍💻 Babacar Mbow</h3>
                <img src="data:image/png;base64,{logo_b64}" style="width:38px; background:white; border-radius:8px; padding:3px; border:1px solid #EDEBE3;" />
                <span class="gold-badge" style="font-size:0.65rem;">L3 GLAR • ESTM</span>
            </div>
            <p style="margin:8px 0 0 0; color:#3A5A4A; line-height:1.5;">
            Étudiant L3 GLAR à l'ESTM Dakar. Passionné par le Génie Logiciel, l'Administration Réseaux et le Cloud. 
            Cette application est ton <b>cockpit personnel d'excellence</b> pour organiser tes cours, générer tes fiches et cartonner aux examens S5/S6.
            </p>
            <div style="margin-top:10px; display:flex; gap:8px;">
                <span style="background:#E8F5E9; color:#1B4332; padding:4px 10px; border-radius:12px; font-weight:700; font-size:0.75rem;">🎯 Objectif : 85% moyenne</span>
                <span style="background:#FFF8E1; color:#8A6A00; padding:4px 10px; border-radius:12px; font-weight:700; font-size:0.75rem;">⚡ Design Vert #1B4332 • Or #D4A017</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    matieres=fetch_all("SELECT * FROM matieres"); chapitres=fetch_all("SELECT * FROM chapitres"); quiz_res=fetch_all("SELECT * FROM quiz_results")
    c1,c2,c3,c4=st.columns(4)
    with c1:
        with st.container(border=True): st.metric("📚 Matières", len(matieres), f"{len([m for m in matieres if m['statut']=='Maîtrisé'])} maîtrisées")
    with c2:
        with st.container(border=True): st.metric("📄 Chapitres", len(chapitres))
    with c3:
        with st.container(border=True): st.metric("❓ Quiz", len(quiz_res))
    with c4:
        with st.container(border=True):
            avg=round(sum([r["pourcentage"] for r in quiz_res])/len(quiz_res),1) if quiz_res else 0
            st.metric("🏆 Réussite", f"{avg}%")

    st.divider()
    colA,colB=st.columns([2,1], gap="large")
    with colA:
        with st.container(border=True):
            st.markdown("### 📈 Progression par matière")
            if quiz_res:
                try:
                    df=pd.DataFrame(fetch_all("SELECT m.nom, qr.pourcentage FROM quiz_results qr JOIN quiz q ON qr.quiz_id=q.id JOIN matieres m ON q.matiere_id=m.id"))
                    if not df.empty:
                        fig=px.bar(df, x="nom", y="pourcentage", color="pourcentage", color_continuous_scale=["#E8F5E9","#2D6A4F","#1B4332"], text_auto=True)
                        fig.update_layout(showlegend=False, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=320, margin=dict(t=20,b=80), xaxis_tickangle=-20)
                        st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.write(e)
            else:
                st.info("Fais ton premier quiz dans Quiz & QCM")
        with st.container(border=True):
            st.markdown("### 📚 Matières prioritaires")
            for m in matieres[:5]:
                st.write(f"**{m['nom']}** — {m['statut']} — Obj {m['objectif']}%")
                st.progress(m['objectif']/100)
    with colB:
        with st.container(border=True):
            st.markdown("### 🎯 Focus")
            obj=st.slider("Minutes / jour", 15, 180, 60, step=15, key="obj")
            st.metric("Aujourd'hui", f"{obj} min"); st.progress(min(obj/120,1.0))
        with st.container(border=True):
            total=sum([a["duree"] for a in fetch_all("SELECT duree FROM activites")])
            st.metric("⏱️ Temps total", f"{total} min")
        with st.container(border=True):
            st.markdown(f'<img src="data:image/png;base64,{logo_b64}" style="width:70px;" />', unsafe_allow_html=True)
            st.caption("ESTM Dakar • École Supérieure de Technologie et de Management")
            st.write("L3 GLAR • 2025-2026 • Avec tes images intégrées ✨")

elif page=="Matières":
    st.title("📚 Matières")
    st.caption("Ajoute, modifie, supprime tes matières ESTM")
    tab1,tab2,tab3=st.tabs(["🖼️ Galerie","➕ Ajouter","✏️ Modifier / Supprimer"])
    matieres_all=fetch_all("SELECT * FROM matieres ORDER BY semestre, nom")
    with tab1:
        cols=st.columns(3)
        for i,m in enumerate(matieres_all):
            with cols[i%3]:
                with st.container(border=True):
                    st.markdown(f"**{m['nom']}**")
                    st.caption(f"{m['semestre']} • {m['difficulte']} • {m['statut']}")
                    st.write(m["description"][:90]+"...")
                    st.progress(m["objectif"]/100, text=f"{m['objectif']}%")
                    c1,c2,c3=st.columns(3)
                    with c1:
                        if st.button("▶️", key=f"m_en_{m['id']}", help="En cours"):
                            execute("UPDATE matieres SET statut='En cours' WHERE id=?", (m["id"],)); st.rerun()
                    with c2:
                        if st.button("✅", key=f"m_ma_{m['id']}", help="Maîtrisé"):
                            execute("UPDATE matieres SET statut='Maîtrisé' WHERE id=?", (m["id"],)); st.rerun()
                    with c3:
                        if st.button("🗑️", key=f"m_del_{m['id']}", help="Supprimer"):
                            execute("DELETE FROM matieres WHERE id=?", (m["id"],))
                            execute("DELETE FROM cours WHERE matiere_id=?", (m["id"],))
                            st.success(f"Supprimée"); st.rerun()
    with tab2:
        with st.container(border=True):
            with st.form("mat_add", clear_on_submit=True, border=False):
                nom=st.text_input("Nom *", placeholder="Ex: Cloud & Docker Avancé")
                desc=st.text_area("Description")
                c1,c2=st.columns(2)
                with c1:
                    sem=st.selectbox("Semestre", SEMESTRES)
                    diff=st.selectbox("Difficulté", NIVEAUX_DIFFICULTE)
                with c2:
                    statut=st.selectbox("Statut", STATUTS_REVISION)
                    obj=st.slider("Objectif %", 50,100,80)
                if st.form_submit_button("✨ Ajouter", type="primary", use_container_width=True):
                    if not nom.strip(): st.error("Nom obligatoire!")
                    else:
                        ex=fetch_one("SELECT id FROM matieres WHERE nom=?", (nom.strip(),))
                        if ex: st.error("Existe déjà!")
                        else:
                            execute("INSERT INTO matieres(nom,description,semestre,difficulte,statut,objectif,created_at) VALUES(?,?,?,?,?,?,?)",(nom.strip(),desc,sem,diff,statut,obj,datetime.now().isoformat()))
                            st.success("Ajoutée!"); st.balloons(); st.rerun()
    with tab3:
        with st.container(border=True):
            if not matieres_all: st.info("Aucune matière")
            else:
                opts={f"{m['id']} - {m['nom']}": m for m in matieres_all}
                sel=st.selectbox("Choisir", list(opts.keys()))
                msel=opts[sel]
                st.write(f"**{msel['nom']}** - {msel['description']}")
                with st.form("mat_edit"):
                    new_nom=st.text_input("Nom", value=msel["nom"])
                    new_desc=st.text_area("Description", value=msel["description"])
                    c1,c2=st.columns(2)
                    with c1:
                        new_sem=st.selectbox("Semestre", SEMESTRES, index=SEMESTRES.index(msel["semestre"]) if msel["semestre"] in SEMESTRES else 0)
                        new_diff=st.selectbox("Difficulté", NIVEAUX_DIFFICULTE, index=NIVEAUX_DIFFICULTE.index(msel["difficulte"]) if msel["difficulte"] in NIVEAUX_DIFFICULTE else 0)
                    with c2:
                        new_stat=st.selectbox("Statut", STATUTS_REVISION, index=STATUTS_REVISION.index(msel["statut"]) if msel["statut"] in STATUTS_REVISION else 0)
                        new_obj=st.slider("Objectif", 50,100,msel["objectif"])
                    cs,cd=st.columns(2)
                    with cs:
                        save=st.form_submit_button("💾 Enregistrer", type="primary", use_container_width=True)
                    with cd:
                        delete=st.form_submit_button("🗑️ Supprimer définitivement", use_container_width=True)
                    if save:
                        execute("UPDATE matieres SET nom=?, description=?, semestre=?, difficulte=?, statut=?, objectif=? WHERE id=?", (new_nom,new_desc,new_sem,new_diff,new_stat,new_obj,msel["id"]))
                        st.success("Modifiée!"); st.rerun()
                    if delete:
                        execute("DELETE FROM matieres WHERE id=?", (msel["id"],)); execute("DELETE FROM cours WHERE matiere_id=?", (msel["id"],)); st.success("Supprimée!"); st.balloons(); st.rerun()

elif page=="Cours & Documents":
    st.title("📄 Cours & Documents")
    matieres=fetch_all("SELECT * FROM matieres"); mat_map={m["nom"]: m["id"] for m in matieres}
    t1,t2,t3=st.tabs(["📤 Importer","📚 Mes cours","🔍 Recherche"])
    with t1:
        with st.container(border=True):
            with st.form("imp", clear_on_submit=True):
                titre=st.text_input("Titre *")
                mat_nom=st.selectbox("Matière", list(mat_map.keys()) if mat_map else ["Aucune"])
                up=st.file_uploader("PDF/TXT/MD", type=["pdf","txt","md"])
                manual=st.text_area("Ou colle le texte", height=150)
                notes=st.text_area("Notes perso")
                if st.form_submit_button("💾 Enregistrer", type="primary", use_container_width=True):
                    if titre:
                        txt=manual
                        fname=None
                        if up:
                            fname=up.name
                            b=up.read()
                            r=extract_text_from_pdf(b) if fname.lower().endswith(".pdf") else extract_text_from_txt(b)
                            if r["success"]: txt=r["text"][:20000]
                        execute("INSERT INTO cours(matiere_id,titre,contenu,fichier_nom,notes,created_at) VALUES(?,?,?,?,?,?)",(mat_map.get(mat_nom),titre,txt,fname,notes,datetime.now().isoformat()))
                        st.success("Enregistré!"); st.balloons()
    with t2:
        cours=fetch_all("SELECT c.*, m.nom as matiere_nom FROM cours c LEFT JOIN matieres m ON c.matiere_id=m.id ORDER BY c.created_at DESC")
        for c in cours:
            with st.container(border=True):
                st.write(f"**{c['titre']}** · {c['matiere_nom'] or ''}")
                st.caption(f"{c['created_at'][:16]}")
                st.text((c["contenu"][:400] if c["contenu"] else "")+"...")
                if st.button("Suppr", key=f"dc_{c['id']}"): execute("DELETE FROM cours WHERE id=?", (c["id"],)); st.rerun()
    with t3:
        q=st.text_input("Recherche")
        if q:
            res=fetch_all("SELECT * FROM cours WHERE contenu LIKE ? OR titre LIKE ?", (f"%{q}%", f"%{q}%"))
            for r in res:
                with st.container(border=True): st.write(f"**{r['titre']}**"); st.caption(r['contenu'][:200])

elif page=="Fiches":
    st.title("📝 Fiches")
    t1,t2,t3=st.tabs(["✨ Auto","✍️ Manuel","📚 Mes fiches"])
    with t1:
        cours=fetch_all("SELECT * FROM cours")
        if not cours: st.info("Importe un cours d'abord")
        else:
            sel=st.selectbox("Cours", [f"{c['id']} - {c['titre']}" for c in cours])
            if st.button("✨ Générer", type="primary", use_container_width=True):
                cid=int(sel.split(" - ")[0]); cobj=fetch_one("SELECT * FROM cours WHERE id=?", (cid,))
                if cobj and cobj["contenu"]:
                    fiche=generate_fiche_auto(cobj["contenu"], cobj["titre"])
                    execute("INSERT INTO fiches(matiere_id,titre,notions,definitions,points_cles,formules,exemples,erreurs,resume,created_at) VALUES(?,?,?,?,?,?,?,?,?,?)",(cobj["matiere_id"],cobj["titre"],fiche["notions"],fiche["definitions"],fiche["points_cles"],fiche["formules"],fiche["exemples"],fiche["erreurs"],fiche["resume"],datetime.now().isoformat()))
                    st.success("Fiche générée!")
    with t2:
        with st.form("fiche_man", clear_on_submit=True):
            titre=st.text_input("Titre"); notions=st.text_area("Notions"); defs=st.text_area("Définitions")
            if st.form_submit_button("Enregistrer", type="primary"):
                if titre:
                    execute("INSERT INTO fiches(titre,notions,definitions,created_at) VALUES(?,?,?,?)",(titre,notions,defs,datetime.now().isoformat()))
                    st.success("Enregistrée")
    with t3:
        fiches=fetch_all("SELECT * FROM fiches ORDER BY created_at DESC")
        for f in fiches:
            with st.expander(f"{f['titre']} - {f['created_at'][:16]}"):
                st.write(f["notions"]); st.write(f["definitions"]); st.write(f["resume"])

elif page=="Quiz & QCM":
    st.title("❓ Quiz & QCM")
    t_quiz,t_create,t_hist=st.tabs(["🎯 Passer","➕ Créer","📊 Historique"])
    with t_create:
        matieres=fetch_all("SELECT * FROM matieres")
        with st.form("quiz_form", clear_on_submit=True, border=True):
            titre=st.text_input("Titre quiz *")
            mat_sel=st.selectbox("Matière", [f"{m['id']} - {m['nom']}" for m in matieres] if matieres else ["0 - Aucune"])
            diff=st.selectbox("Difficulté", NIVEAUX_DIFFICULTE)
            if st.form_submit_button("Créer quiz", type="primary", use_container_width=True):
                if titre:
                    mid=int(mat_sel.split(" - ")[0])
                    execute("INSERT INTO quiz(matiere_id,titre,difficulte,created_at) VALUES(?,?,?,?)",(mid,titre,diff,datetime.now().isoformat()))
                    st.success("Quiz créé!")
        st.divider()
        quizzes=fetch_all("SELECT * FROM quiz ORDER BY created_at DESC")
        if quizzes:
            q_sel2=st.selectbox("Quiz pour ajouter question", [f"{q['id']} - {q['titre']}" for q in quizzes])
            with st.form("q_add", clear_on_submit=True, border=True):
                question=st.text_area("Question *")
                c1,c2=st.columns(2)
                with c1: opt1=st.text_input("Option 1 *"); opt2=st.text_input("Option 2 *")
                with c2: opt3=st.text_input("Option 3"); opt4=st.text_input("Option 4")
                correct_str=st.text_input("Index correct (0,1,2...)", placeholder="0")
                expl=st.text_area("Explication")
                if st.form_submit_button("Ajouter question"):
                    if question and opt1 and opt2 and correct_str:
                        opts=[o for o in [opt1,opt2,opt3,opt4] if o]
                        try:
                            corrects=[int(x.strip()) for x in correct_str.split(",")]
                            qid=int(q_sel2.split(" - ")[0])
                            execute("INSERT INTO questions(quiz_id,question,type,options,reponses_correctes,explication,difficulte) VALUES(?,?,?,?,?,?,?)",(qid,question,"unique",json.dumps(opts),json.dumps(corrects),expl,"Intermédiaire"))
                            st.success("Question ajoutée")
                        except Exception as e: st.error(f"{e}")
    with t_quiz:
        quizzes=fetch_all("SELECT * FROM quiz")
        if not quizzes: st.info("Crée un quiz d'abord")
        else:
            q_sel=st.selectbox("Choisir quiz", [f"{q['id']} - {q['titre']}" for q in quizzes])
            qid=int(q_sel.split(" - ")[0])
            qs=fetch_all("SELECT * FROM questions WHERE quiz_id=?", (qid,))
            if not qs: st.info("Pas de questions")
            else:
                for q in qs:
                    opts=json.loads(q["options"]) if isinstance(q["options"],str) else q["options"]
                    st.write(f"**{q['question']}**")
                    for i,o in enumerate(opts):
                        if st.checkbox(o, key=f"q{q['id']}_{i}"):
                            st.session_state.quiz_answers[q["id"]]=st.session_state.quiz_answers.get(q["id"],[])+[i]
                if st.button("✅ Soumettre", type="primary"):
                    score=calculate_quiz_score(st.session_state.quiz_answers, qs)
                    execute("INSERT INTO quiz_results(quiz_id,score,total,pourcentage,temps_sec,details,created_at) VALUES(?,?,?,?,?,?,?)",(qid,score["score20"],score["total"],score["pct"],0,json.dumps(score["details"]),datetime.now().isoformat()))
                    st.success(f"Score: {score['score20']}/20 - {score['pct']:.1f}%"); st.balloons()
    with t_hist:
        hist=fetch_all("SELECT qr.*, q.titre FROM quiz_results qr JOIN quiz q ON qr.quiz_id=q.id ORDER BY qr.created_at DESC")
        if hist: st.dataframe(pd.DataFrame(hist))
        else: st.info("Pas de résultats")

elif page=="Exercices":
    st.title("💻 Exercices")
    exos=fetch_all("SELECT * FROM exercices ORDER BY created_at DESC")
    for e in exos:
        with st.container(border=True):
            st.markdown(f"### {e['titre']} · `{e['categorie']}` · {e['difficulte']}")
            st.write(e['enonce'])
            st.text_area("Ta réponse", key=f"rep_{e['id']}")
            if st.button("👁️ Voir correction", key=f"cor_{e['id']}"): st.session_state.show_correction[e['id']]=True
            if st.session_state.show_correction.get(e['id']): st.success(e['solution']); st.warning(e['erreurs'])

elif page=="Assistant":
    st.title("🤖 Assistant")
    with st.container(border=True):
        q=st.text_input("Pose ta question", placeholder="Explique-moi la POO...")
        if q:
            cours=fetch_all("SELECT * FROM cours WHERE contenu LIKE ? LIMIT 3", (f"%{q.split()[0]}%",))
            if cours:
                for c in cours:
                    with st.expander(c['titre']): st.text(c['contenu'][:600])
            qlow=q.lower()
            if "poo" in qlow: st.success("POO: Classe = moule, Objet = instance. Encapsulation, Héritage, Polymorphisme.")
            elif "réseau" in qlow: st.success("TCP fiable (handshake), UDP rapide. VLAN sépare broadcast.")
            else: st.write(f"Réponse locale pour '{q}'")

elif page=="Flashcards":
    st.title("🃏 Flashcards")
    t1,t2=st.tabs(["🎯 Réviser","➕ Gérer"])
    with t2:
        with st.form("flash_form", clear_on_submit=True, border=True):
            q=st.text_input("Question *"); r=st.text_area("Réponse *")
            if st.form_submit_button("Ajouter carte", type="primary"):
                if q and r:
                    execute("INSERT INTO flashcards(question,reponse,statut,next_review,created_at) VALUES(?,?,?,?,?)",(q,r,"À revoir",spaced_next_review("À revoir"),datetime.now().isoformat()))
                    st.success("Carte ajoutée!")
    with t1:
        cards=fetch_all("SELECT * FROM flashcards ORDER BY next_review ASC")
        if not cards: st.info("Aucune carte")
        else:
            idx=st.session_state.flash_idx % len(cards); card=cards[idx]
            with st.container(border=True):
                st.markdown(f"### Carte {idx+1}/{len(cards)} — {card['statut']}")
                st.markdown(f"## {card['question']}")
                if st.button("🔍 Révéler", type="primary", use_container_width=True): st.session_state.reveal=True
                if st.session_state.get("reveal"):
                    st.success(card['reponse'])
                    c1,c2,c3=st.columns(3)
                    with c1:
                        if st.button("🔴 À revoir", use_container_width=True):
                            execute("UPDATE flashcards SET statut='À revoir', next_review=? WHERE id=?", (spaced_next_review("À revoir"), card["id"]))
                            st.session_state.flash_idx+=1; st.session_state.reveal=False; st.rerun()
                    with c2:
                        if st.button("🟡 En cours", use_container_width=True):
                            execute("UPDATE flashcards SET statut='En cours d'acquisition', next_review=? WHERE id=?", (spaced_next_review("En cours d'acquisition"), card["id"]))
                            st.session_state.flash_idx+=1; st.session_state.reveal=False; st.rerun()
                    with c3:
                        if st.button("🟢 Maîtrisé", use_container_width=True):
                            execute("UPDATE flashcards SET statut='Maîtrisé', next_review=? WHERE id=?", (spaced_next_review("Maîtrisé"), card["id"]))
                            st.session_state.flash_idx+=1; st.session_state.reveal=False; st.rerun()

elif page=="Planning":
    st.title("🗓️ Planning")
    with st.container(border=True):
        with st.form("plan_form", clear_on_submit=True):
            titre=st.text_input("Titre séance *"); date=st.date_input("Date", datetime.now().date()); duree=st.number_input("Durée min", 15,240,60, step=15); priorite=st.selectbox("Priorité", ["Basse","Moyenne","Haute","Critique"])
            if st.form_submit_button("Ajouter", type="primary", use_container_width=True):
                if titre:
                    execute("INSERT INTO planning(titre,date,duree,priorite,statut,created_at) VALUES(?,?,?,?,?,?)",(titre,date.isoformat(),duree,priorite,"Prévu",datetime.now().isoformat()))
                    st.success("Ajouté!")
    sessions=fetch_all("SELECT * FROM planning ORDER BY date ASC")
    for s in sessions:
        with st.container(border=True):
            c1,c2,c3=st.columns([3,1,1])
            with c1: st.write(f"**{s['titre']}** · {s['date']} · {s['duree']}min · {s['priorite']} · {s['statut']}")
            with c2:
                if st.button("✅", key=f"done_{s['id']}"): execute("UPDATE planning SET statut='Terminée' WHERE id=?", (s["id"],)); st.rerun()
            with c3:
                if st.button("🗑️", key=f"del_{s['id']}"): execute("DELETE FROM planning WHERE id=?", (s["id"],)); st.rerun()

elif page=="Statistiques":
    st.title("📊 Statistiques")
    quiz_res=fetch_all("SELECT qr.*, q.titre FROM quiz_results qr JOIN quiz q ON qr.quiz_id=q.id")
    if not quiz_res: st.info("Fais un quiz pour voir tes stats!")
    else:
        df=pd.DataFrame(quiz_res)
        with st.container(border=True): st.metric("Moyenne /20", round(df["score"].mean(),2))
        st.plotly_chart(px.line(df, x="created_at", y="pourcentage", title="Évolution"), use_container_width=True)

st.divider()
st.markdown(f"""
<div style="display:flex; align-items:center; gap:14px; padding:12px 16px; background:white; border-radius:16px; border:1px solid #EDEBE3; box-shadow:0 8px 20px rgba(0,0,0,0.05);">
    <img src="data:image/png;base64,{logo_b64}" style="width:52px;" />
    <div style="flex:1;">
        <div style="font-weight:900; color:#1B4332;">✨ GLAR Revision Hub • Babacar Mbow • ESTM Dakar</div>
        <div style="font-size:0.8rem; color:#6A8A7A;">Design Vert #1B4332 • Or #D4A017 • Avec tes images intégrées en base64 • v{APP_VERSION}</div>
    </div>
    <img src="data:image/jpeg;base64,{photo_b64}" style="width:42px; height:42px; border-radius:50%; border:2px solid #D4A017;" />
</div>
""", unsafe_allow_html=True)
