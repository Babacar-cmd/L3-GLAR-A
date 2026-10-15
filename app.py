import streamlit as st
import os, sys, traceback, base64, json, time
from datetime import datetime

# --- PAGE CONFIG EN PREMIER, TOUJOURS ---
st.set_page_config(page_title="GLAR REVISION HUB", page_icon="🎓", layout="wide", initial_sidebar_state="expanded")

def img_to_base64(path):
    try:
        if os.path.exists(path):
            with open(path, "rb") as f:
                return base64.b64encode(f.read()).decode()
    except:
        pass
    return ""

# Chemins robustes pour Cloud et local
logo_candidates = ["assets/estm_logo.png", "estm_logo.png", "./assets/estm_logo.png"]
photo_candidates = ["assets/Babacar_Mbow.jpg", "Babacar_Mbow.jpg", "./assets/Babacar_Mbow.jpg"]

logo_path = next((p for p in logo_candidates if os.path.exists(p)), "")
photo_path = next((p for p in photo_candidates if os.path.exists(p)), "")

logo_b64 = img_to_base64(logo_path)
photo_b64 = img_to_base64(photo_path)

# CSS minimal safe
st.markdown("""
<style>
.stApp { background: #F6F8F3; }
section[data-testid="stSidebar"] { background: linear-gradient(180deg, #0F2A1E 0%, #1B4332 50%, #2D6A4F 100%) !important; }
section[data-testid="stSidebar"] * { color: #E8F5E9 !important; }
.gold-badge { background: linear-gradient(135deg, #D4A017 0%, #F4D35E 100%); color: #1B4332; padding: 6px 14px; border-radius: 20px; font-weight: 800; font-size: 0.75rem; display: inline-block; }
.watermark { position: fixed; bottom: 12px; right: 18px; background: rgba(255,255,255,0.9); padding: 6px 12px; border-radius: 20px; font-size: 10px; font-weight: 800; color: #1B4332; z-index: 9999; border: 1px solid #EDEBE3; }
</style>
""", unsafe_allow_html=True)

# Imports avec gestion d'erreur
try:
    from database import init_db, fetch_all, fetch_one, execute, get_storage_info
    from utils import extract_text_from_pdf, extract_text_from_txt, generate_fiche_auto, calculate_quiz_score, spaced_next_review
    from config import APP_NAME, APP_VERSION, SEMESTRES, NIVEAUX_DIFFICULTE, STATUTS_REVISION
    init_db()
except Exception as e:
    st.error(f"Erreur init DB/config: {e}")
    st.code(traceback.format_exc())
    # fallback config minimale pour que l'app démarre quand même
    APP_NAME = "GLAR REVISION HUB"
    APP_VERSION = "3.0 Stable"
    SEMESTRES = ["S5","S6","L3"]
    NIVEAUX_DIFFICULTE = ["Débutant","Intermédiaire","Avancé","Expert"]
    STATUTS_REVISION = ["Non commencé","En cours","Maîtrisé","À revoir"]
    def fetch_all(q,p=()): return []
    def fetch_one(q,p=()): return None
    def execute(q,p=()): return 0
    def get_storage_info(): return {"size_kb":0,"mode":"fallback"}
    def extract_text_from_pdf(b): return {"success":False,"text":"","warning":""}
    def extract_text_from_txt(b): return {"success":True,"text":b.decode('utf-8', errors='ignore')}
    def generate_fiche_auto(c,t="Fiche"): return {"notions":c[:200],"definitions":"- def","points_cles":"- point","formules":"","exemples":"","erreurs":"","resume":c[:300]}
    def calculate_quiz_score(a,q): return {"correct":0,"total":len(q),"pct":0,"score20":0,"details":[]}
    def spaced_next_review(s): return datetime.now().isoformat()

# Seed optionnel
try:
    from data.seed import seed_all
    seed_all()
except:
    pass

# Session
for k,v in [("page","Tableau de bord"),("quiz_answers",{}),("flash_idx",0),("show_correction",{}),("reveal",False),("splash_shown",False)]:
    if k not in st.session_state:
        st.session_state[k]=v

# Splash - version safe sans bloquer trop
if not st.session_state.splash_shown:
    ph = st.empty()
    with ph.container():
        cols = st.columns([1,2,1])
        with cols[1]:
            if logo_b64:
                st.markdown(f'<div style="text-align:center"><img src="data:image/png;base64,{logo_b64}" width="140"/></div>', unsafe_allow_html=True)
            if photo_b64:
                st.markdown(f'<div style="text-align:center; margin-top:12px"><img src="data:image/jpeg;base64,{photo_b64}" style="width:180px; border-radius:50%; border:4px solid #D4A017;"/></div>', unsafe_allow_html=True)
            st.markdown("<h2 style='text-align:center'>GLAR REVISION HUB<br/><small>Babacar Mbow • ESTM Dakar</small></h2>", unsafe_allow_html=True)
            st.markdown('<div style="text-align:center"><span class="gold-badge">✨ Chargement...</span></div>', unsafe_allow_html=True)
    time.sleep(1.2)
    st.session_state.splash_shown = True
    ph.empty()
    st.rerun()

# Watermark
st.markdown(f'<div class="watermark">© BABACAR MBOW • ESTM DAKAR • {datetime.now().year}</div>', unsafe_allow_html=True)

# SIDEBAR
with st.sidebar:
    if logo_b64:
        st.markdown(f'<div style="background:white; border-radius:14px; padding:10px; text-align:center"><img src="data:image/png;base64,{logo_b64}" width="100"/></div>', unsafe_allow_html=True)
    st.markdown("### GLAR HUB")
    st.markdown('<span class="gold-badge">✨ L3 GLAR • ESTM DAKAR</span>', unsafe_allow_html=True)
    st.divider()
    pages=["Tableau de bord","Matières","Cours & Documents","Fiches","Quiz & QCM","Exercices","Assistant","Flashcards","Planning","Statistiques"]
    icons=["🏠","📚","📄","📝","❓","💻","🤖","🃏","🗓️","📊"]
    for ic,p in zip(icons,pages):
        if st.button(f"{ic}  {p}", use_container_width=True, key=f"nav_{p}", type="primary" if st.session_state.page==p else "secondary"):
            st.session_state.page=p
            st.rerun()
    st.divider()
    if photo_b64:
        st.markdown(f'<img src="data:image/jpeg;base64,{photo_b64}" style="width:100%; border-radius:12px; border:2px solid #D4A017;"/>', unsafe_allow_html=True)
    st.caption("Babacar Mbow • L3 GLAR")
    try:
        s=get_storage_info()
        st.caption(f"DB {s['size_kb']} KB • v{APP_VERSION}")
    except:
        pass

page = st.session_state.page

def safe_run(func):
    try:
        func()
    except Exception as e:
        st.error(f"Erreur sur la page {page}: {e}")
        st.code(traceback.format_exc())
        st.info("L'app continue de fonctionner, signale cette erreur si elle persiste.")

# --- PAGES SIMPLIFIEES STABLES ---
if page == "Tableau de bord":
    def render():
        c1,c2 = st.columns([1,5])
        with c1:
            if logo_b64: st.markdown(f'<img src="data:image/png;base64,{logo_b64}" width="70"/>', unsafe_allow_html=True)
        with c2:
            st.title("GLAR REVISION HUB")
            st.caption("Babacar Mbow • L3 GLAR • ESTM Dakar • Version Stable Cloud")

        with st.container(border=True):
            cc1,cc2 = st.columns([1,4])
            with cc1:
                if photo_b64: st.markdown(f'<img src="data:image/jpeg;base64,{photo_b64}" style="width:100px; border-radius:50%; border:3px solid #D4A017;"/>', unsafe_allow_html=True)
            with cc2:
                st.markdown("### 👨‍💻 Babacar Mbow")
                st.write("Cockpit personnel pour organiser tes cours, générer tes fiches et cartonner aux examens S5/S6. Version stable Cloud avec tes images intégrées.")

        matieres = fetch_all("SELECT * FROM matieres")
        quiz_res = fetch_all("SELECT * FROM quiz_results")
        m1,m2,m3,m4 = st.columns(4)
        with m1: st.metric("📚 Matières", len(matieres))
        with m2: st.metric("❓ Quiz résultats", len(quiz_res))
        with m3: 
            avg = round(sum([r["pourcentage"] for r in quiz_res])/len(quiz_res),1) if quiz_res else 0
            st.metric("🏆 Moyenne", f"{avg}%")
        with m4:
            total = sum([a["duree"] for a in fetch_all("SELECT duree FROM activites")]) if matieres else 0
            st.metric("⏱️ Temps", f"{total} min")
        st.success("✅ App stable déployée avec succès sur Streamlit Cloud !")
    safe_run(render)

elif page == "Matières":
    def render():
        import pandas as pd
        st.title("📚 Matières")
        matieres = fetch_all("SELECT * FROM matieres ORDER BY semestre, nom")
        cols = st.columns(3)
        for i,m in enumerate(matieres):
            with cols[i%3]:
                with st.container(border=True):
                    st.markdown(f"**{m['nom']}**")
                    st.caption(f"{m['semestre']} • {m['difficulte']} • {m['statut']}")
                    st.progress(m["objectif"]/100, text=f"{m['objectif']}%")
        st.divider()
        with st.form("mat_add", clear_on_submit=True):
            nom=st.text_input("Nom matière *"); desc=st.text_area("Description")
            c1,c2 = st.columns(2)
            with c1: sem=st.selectbox("Semestre", SEMESTRES); diff=st.selectbox("Difficulté", NIVEAUX_DIFFICULTE)
            with c2: statut=st.selectbox("Statut", STATUTS_REVISION); obj=st.slider("Objectif %", 50,100,80)
            if st.form_submit_button("Ajouter", type="primary"):
                if nom.strip():
                    execute("INSERT INTO matieres(nom,description,semestre,difficulte,statut,objectif,created_at) VALUES(?,?,?,?,?,?,?)",(nom.strip(),desc,sem,diff,statut,obj,datetime.now().isoformat()))
                    st.success("Ajoutée!"); st.rerun()
    safe_run(render)

elif page == "Cours & Documents":
    def render():
        st.title("📄 Cours & Documents")
        matieres=fetch_all("SELECT * FROM matieres"); mat_map={m["nom"]: m["id"] for m in matieres}
        with st.container(border=True):
            with st.form("imp", clear_on_submit=True):
                titre=st.text_input("Titre *"); mat_nom=st.selectbox("Matière", list(mat_map.keys()) if mat_map else ["Aucune"])
                up=st.file_uploader("PDF/TXT", type=["pdf","txt","md"]); manual=st.text_area("Ou colle le texte")
                if st.form_submit_button("Enregistrer", type="primary"):
                    if titre:
                        txt=manual
                        if up:
                            b=up.read()
                            r=extract_text_from_pdf(b) if up.name.lower().endswith(".pdf") else extract_text_from_txt(b)
                            if r.get("success"): txt=r["text"][:20000]
                        execute("INSERT INTO cours(matiere_id,titre,contenu,fichier_nom,created_at) VALUES(?,?,?,?,?)",(mat_map.get(mat_nom),titre,txt,up.name if up else None,datetime.now().isoformat()))
                        st.success("Enregistré!")
        cours=fetch_all("SELECT c.*, m.nom as matiere_nom FROM cours c LEFT JOIN matieres m ON c.matiere_id=m.id ORDER BY c.created_at DESC LIMIT 20")
        for c in cours:
            with st.container(border=True):
                st.write(f"**{c['titre']}** · {c['matiere_nom'] or ''}"); st.caption(c['contenu'][:200] if c['contenu'] else "")
    safe_run(render)

elif page == "Fiches":
    def render():
        st.title("📝 Fiches")
        cours=fetch_all("SELECT * FROM cours")
        if cours:
            sel=st.selectbox("Cours", [f"{c['id']} - {c['titre']}" for c in cours])
            if st.button("✨ Générer fiche auto", type="primary"):
                cid=int(sel.split(" - ")[0]); cobj=fetch_one("SELECT * FROM cours WHERE id=?", (cid,))
                if cobj and cobj["contenu"]:
                    fiche=generate_fiche_auto(cobj["contenu"], cobj["titre"])
                    execute("INSERT INTO fiches(matiere_id,titre,notions,definitions,points_cles,resume,created_at) VALUES(?,?,?,?,?,?,?)",(cobj["matiere_id"],cobj["titre"],fiche["notions"],fiche["definitions"],fiche["points_cles"],fiche["resume"],datetime.now().isoformat()))
                    st.success("Fiche générée!")
        fiches=fetch_all("SELECT * FROM fiches ORDER BY created_at DESC LIMIT 20")
        for f in fiches:
            with st.expander(f"{f['titre']}"): st.write(f.get('resume',''))
    safe_run(render)

elif page == "Quiz & QCM":
    def render():
        st.title("❓ Quiz & QCM")
        quizzes=fetch_all("SELECT * FROM quiz")
        if not quizzes: st.info("Crée un quiz dans l'ancien app.py complet, ou utilise ce module stable.")
        else:
            q_sel=st.selectbox("Quiz", [f"{q['id']} - {q['titre']}" for q in quizzes])
            qid=int(q_sel.split(" - ")[0]); qs=fetch_all("SELECT * FROM questions WHERE quiz_id=?", (qid,))
            for q in qs:
                st.write(f"**{q['question']}**")
                opts=json.loads(q["options"]) if isinstance(q["options"],str) else q["options"]
                for i,o in enumerate(opts):
                    st.checkbox(o, key=f"q{q['id']}_{i}")
            if st.button("Soumettre", type="primary") and qs:
                st.balloons(); st.success("Quiz soumis (mode stable)")
    safe_run(render)

elif page == "Statistiques":
    def render():
        import pandas as pd, plotly.express as px
        st.title("📊 Statistiques")
        quiz_res=fetch_all("SELECT * FROM quiz_results")
        if not quiz_res: st.info("Pas encore de résultats")
        else:
            df=pd.DataFrame(quiz_res); st.metric("Moyenne /20", round(df["score"].mean(),2))
            st.plotly_chart(px.line(df, x="created_at", y="pourcentage", title="Évolution"), use_container_width=True)
    safe_run(render)

else:
    def render():
        st.title(page)
        st.info(f"Page {page} - version stable. Utilise app_final.py en local pour la version complète avec toutes les fonctionnalités splendides. Cette version Cloud est allégée pour éviter les crashs.")
        if photo_b64:
            st.markdown(f'<img src="data:image/jpeg;base64,{photo_b64}" width="200" style="border-radius:50%; border:3px solid #D4A017;"/>', unsafe_allow_html=True)
    safe_run(render)

st.divider()
st.caption(f"✨ GLAR Revision Hub • Babacar Mbow • ESTM Dakar • v{APP_VERSION} • Stable Cloud • Vert #1B4332 Or #D4A017")
