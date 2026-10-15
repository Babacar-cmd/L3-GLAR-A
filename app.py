
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import json
from database import init_db, fetch_all, fetch_one, execute, get_storage_info
from utils import extract_text_from_pdf, extract_text_from_txt, generate_fiche_auto, calculate_quiz_score, spaced_next_review
from config import APP_NAME, APP_VERSION, SEMESTRES, NIVEAUX_DIFFICULTE, STATUTS_REVISION

st.set_page_config(page_title=APP_NAME, page_icon="🎓", layout="wide", initial_sidebar_state="expanded")

st.markdown('''
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@600;700;800&display=swap');
.stApp { background: radial-gradient(1200px 600px at 10% -10%, #E8F5E9 0%, transparent 60%), radial-gradient(1000px 500px at 90% 0%, #FFF8E1 0%, transparent 60%), linear-gradient(180deg, #F6F8F3 0%, #FFFFFF 70%); }
section[data-testid="stSidebar"] { background: linear-gradient(180deg, #0F2A1E 0%, #1B4332 50%, #2D6A4F 100%) !important; }
section[data-testid="stSidebar"] * { color: #E8F5E9 !important; }
section[data-testid="stSidebar"] button { background: rgba(255,255,255,0.08) !important; border: 1px solid rgba(255,255,255,0.12) !important; border-radius: 12px !important; }
section[data-testid="stSidebar"] button:hover { background: rgba(212,160,23,0.25) !important; border-color: #D4A017 !important; transform: translateX(3px); }
div[data-testid="stMetric"] { background: white !important; border-radius: 16px !important; border: 1px solid #EDEBE3 !important; box-shadow: 0 8px 20px rgba(27,67,50,0.06) !important; padding: 16px !important; }
div[data-testid="stExpander"] { border-radius: 14px !important; border: 1px solid #EDEBE3 !important; background: white !important; }
button[kind="primary"] { background: linear-gradient(135deg, #1B4332 0%, #2D6A4F 100%) !important; border-radius: 12px !important; box-shadow: 0 6px 16px rgba(27,67,50,0.3) !important; }
.gold-badge { background: linear-gradient(135deg, #D4A017 0%, #F4D35E 100%); color: #1B4332; padding: 6px 14px; border-radius: 20px; font-weight: 800; font-size: 0.75rem; letter-spacing: 0.5px; display: inline-block; margin-bottom: 10px; }
.hero-title { font-family: Inter; font-weight: 800; font-size: 2.2rem; color: #0F2A1E; margin: 0; }
.hero-sub { color: #5A6D5E; font-size: 1.05rem; margin-top: 6px; }
</style>
''', unsafe_allow_html=True)

init_db()
try:
    from data.seed import seed_all
    seed_all()
except: pass

for k,v in [("page","Tableau de bord"),("quiz_answers",{}),("quiz_started",{}),("flash_idx",0),("show_correction",{}),("reveal",False)]:
    if k not in st.session_state: st.session_state[k]=v

with st.sidebar:
    st.markdown("### 🎓 GLAR HUB")
    st.markdown('<span class="gold-badge">✨ L3 GLAR • ESTM DAKAR • BEAUTIFUL</span>', unsafe_allow_html=True)
    st.divider()
    pages=["Tableau de bord","Matières","Cours & Documents","Fiches","Quiz & QCM","Exercices","Assistant","Flashcards","Planning","Statistiques"]
    icons=["🏠","📚","📄","📝","❓","💻","🤖","🃏","🗓️","📊"]
    for ic,p in zip(icons,pages):
        if st.button(f"{ic}  {p}", use_container_width=True, key=f"nav_{p}", type="primary" if st.session_state.page==p else "secondary"):
            st.session_state.page=p
            st.rerun()
    st.divider()
    try:
        s=get_storage_info()
        st.caption(f"DB {s['size_kb']} KB • v{APP_VERSION}")
    except: pass

def log_activite(t,d,mid=None,dur=0):
    try: execute("INSERT INTO activites(type,description,matiere_id,duree,created_at) VALUES(?,?,?,?,?)",(t,d,mid,dur,datetime.now().isoformat()))
    except: pass

page=st.session_state.page

if page=="Tableau de bord":
    st.markdown('<span class="gold-badge">✨ DESIGN BEAUTIFUL ACTIVÉ</span>', unsafe_allow_html=True)
    st.markdown('<div class="hero-title">GLAR REVISION HUB</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Ton cockpit de révision L3 • Vert ESTM #1B4332 • Or #D4A017 • Cartes blanches • Graphiques doux</div>', unsafe_allow_html=True)
    st.write("")
    matieres=fetch_all("SELECT * FROM matieres"); chapitres=fetch_all("SELECT * FROM chapitres"); quiz_res=fetch_all("SELECT * FROM quiz_results")
    c1,c2,c3,c4=st.columns(4)
    with c1:
        with st.container(border=True):
            st.metric("📚 Matières", len(matieres), f"{len([m for m in matieres if m['statut']=='Maîtrisé'])} maîtrisées")
    with c2:
        with st.container(border=True):
            st.metric("📄 Chapitres", len(chapitres))
    with c3:
        with st.container(border=True):
            st.metric("❓ Quiz", len(quiz_res))
    with c4:
        with st.container(border=True):
            avg=round(sum([r["pourcentage"] for r in quiz_res])/len(quiz_res),1) if quiz_res else 0
            st.metric("🏆 Réussite", f"{avg}%", "Top" if avg>75 else "À booster")
    st.divider()
    colA,colB=st.columns([2,1], gap="large")
    with colA:
        with st.container(border=True):
            st.markdown("### 📈 Ta progression")
            if quiz_res:
                try:
                    df=pd.DataFrame(fetch_all("SELECT m.nom, qr.pourcentage FROM quiz_results qr JOIN quiz q ON qr.quiz_id=q.id JOIN matieres m ON q.matiere_id=m.id"))
                    if not df.empty:
                        fig=px.bar(df, x="nom", y="pourcentage", color="pourcentage", color_continuous_scale=["#E8F5E9","#A7D7B0","#2D6A4F","#1B4332"], text_auto=True)
                        fig.update_layout(showlegend=False, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=340, margin=dict(t=20,b=80))
                        st.plotly_chart(fig, use_container_width=True)
                except: st.info("Fais ton premier quiz!")
            else: st.info("🎯 Fais un quiz pour voir ton graphique ici")
        with st.container(border=True):
            st.markdown("### 📚 Matières")
            for m in matieres[:5]:
                cc1,cc2=st.columns([3,1])
                with cc1: st.write(f"**{m['nom']}** — {m['semestre']} • {m['statut']}")
                with cc2: st.progress(m['objectif']/100)
    with colB:
        with st.container(border=True):
            st.markdown("### 🎯 Focus")
            obj=st.slider("Minutes / jour", 15, 180, 60, step=15, key="obj")
            st.metric("Aujourd'hui", f"{obj} min")
            st.progress(min(obj/120,1.0))
        with st.container(border=True):
            total=sum([a["duree"] for a in fetch_all("SELECT duree FROM activites")])
            st.metric("⏱️ Temps total", f"{total} min", f"{total//60}h")
            st.caption("Tu es sur la bonne voie!")

elif page=="Matières":
    st.title("📚 Matières")
    tab1,tab2=st.tabs(["Galerie","Ajouter"])
    with tab1:
        matieres=fetch_all("SELECT * FROM matieres ORDER BY semestre, nom")
        cols=st.columns(3)
        for i,m in enumerate(matieres):
            with cols[i%3]:
                with st.container(border=True):
                    st.markdown(f"**{m['nom']}**")
                    st.caption(f"{m['semestre']} • {m['difficulte']} • {m['statut']}")
                    st.write(m["description"][:90]+"...")
                    st.progress(m["objectif"]/100)
                    if st.button("✨ Gérer", key=f"m_{m['id']}", use_container_width=True):
                        execute("UPDATE matieres SET statut='En cours' WHERE id=?", (m["id"],))
                        st.toast(f"{m['nom']} en cours")
    with tab2:
        with st.form("mat", clear_on_submit=True, border=True):
            nom=st.text_input("Nom *", placeholder="Cloud & Docker")
            desc=st.text_area("Description")
            c1,c2=st.columns(2)
            with c1:
                sem=st.selectbox("Semestre", SEMESTRES)
                diff=st.selectbox("Difficulté", NIVEAUX_DIFFICULTE)
            with c2:
                statut=st.selectbox("Statut", STATUTS_REVISION)
                obj=st.slider("Objectif %", 50,100,80)
            if st.form_submit_button("Créer", type="primary", use_container_width=True):
                if nom:
                    ex=fetch_one("SELECT id FROM matieres WHERE nom=?", (nom,))
                    if ex: execute("UPDATE matieres SET description=?, semestre=?, difficulte=?, statut=?, objectif=? WHERE nom=?", (desc,sem,diff,statut,obj,nom))
                    else: execute("INSERT INTO matieres(nom,description,semestre,difficulte,statut,objectif,created_at) VALUES(?,?,?,?,?,?,?)",(nom,desc,sem,diff,statut,obj,datetime.now().isoformat()))
                    st.success("Créée!"); st.balloons()

elif page=="Cours & Documents":
    st.title("📄 Cours")
    matieres=fetch_all("SELECT * FROM matieres"); mat_map={m["nom"]: m["id"] for m in matieres}
    t1,t2=st.tabs(["📤 Importer","📚 Mes cours"])
    with t1:
        with st.container(border=True):
            with st.form("imp", clear_on_submit=True):
                titre=st.text_input("Titre *", placeholder="VLAN Inter-VLAN")
                mat_nom=st.selectbox("Matière", list(mat_map.keys()) if mat_map else ["Aucune"])
                up=st.file_uploader("PDF/TXT/MD (15 Mo max)", type=["pdf","txt","md"])
                manual=st.text_area("Ou colle le texte", height=120)
                notes=st.text_area("Notes")
                if st.form_submit_button("💾 Enregistrer", type="primary", use_container_width=True):
                    if titre:
                        txt=manual
                        fname=None
                        if up:
                            fname=up.name
                            b=up.read()
                            r=extract_text_from_pdf(b) if fname.lower().endswith(".pdf") else extract_text_from_txt(b)
                            if r["success"]: txt=r["text"][:20000]; st.success(f"{len(txt)} caractères")
                            else: st.warning(r["warning"])
                        execute("INSERT INTO cours(matiere_id,titre,contenu,fichier_nom,notes,created_at) VALUES(?,?,?,?,?,?)",(mat_map.get(mat_nom),titre,txt,fname,notes,datetime.now().isoformat()))
                        st.success("Enregistré!"); st.balloons()
    with t2:
        cours=fetch_all("SELECT c.*, m.nom as matiere_nom FROM cours c LEFT JOIN matieres m ON c.matiere_id=m.id ORDER BY c.created_at DESC")
        for c in cours:
            with st.container(border=True):
                st.write(f"**{c['titre']}** · {c['matiere_nom'] or ''}")
                st.caption(f"{c['created_at'][:16]} • {c['fichier_nom'] or 'Manuel'}")
                st.text((c["contenu"][:250] if c["contenu"] else "")+"...")
                if st.button("Suppr", key=f"dc_{c['id']}"): execute("DELETE FROM cours WHERE id=?", (c["id"],)); st.rerun()

else:
    # Pages génériques belles mais fonctionnelles
    st.title(page)
    if page=="Fiches":
        cours=fetch_all("SELECT * FROM cours")
        if not cours: st.info("Importe un cours d'abord")
        else:
            sel=st.selectbox("Cours", [f"{c['id']} - {c['titre']}" for c in cours])
            if st.button("✨ Générer fiche auto", type="primary"):
                cid=int(sel.split(" - ")[0]); cobj=fetch_one("SELECT * FROM cours WHERE id=?", (cid,))
                if cobj and cobj["contenu"]:
                    fd=generate_fiche_auto(cobj["contenu"], cobj["titre"])
                    execute("INSERT INTO fiches(matiere_id,titre,notions,definitions,points_cles,resume,created_at) VALUES(?,?,?,?,?,?,?)",(cobj["matiere_id"],f"Fiche - {cobj['titre']}",fd["notions"],fd["definitions"],fd["points_cles"],fd["resume"],datetime.now().isoformat()))
                    st.success("Fiche générée!"); st.balloons()
        fiches=fetch_all("SELECT * FROM fiches ORDER BY created_at DESC")
        for f in fiches:
            with st.container(border=True): st.write(f"**{f['titre']}**"); st.caption(f['notions'][:200])

    elif page=="Quiz & QCM":
        quizzes=fetch_all("SELECT * FROM quiz")
        if quizzes:
            qsel=st.selectbox("Quiz", [f"{q['id']} - {q['titre']}" for q in quizzes])
            qid=int(qsel.split(" - ")[0]); qs=fetch_all("SELECT * FROM questions WHERE quiz_id=?", (qid,))
            if qs:
                if st.button("🚀 Démarrer", type="primary", use_container_width=True):
                    st.session_state.quiz_answers={}; st.session_state.quiz_started[qid]=datetime.now(); st.rerun()
                if qid in st.session_state.quiz_started:
                    for q in qs:
                        with st.container(border=True):
                            opts=json.loads(q["options"]); st.write(f"**{q['question']}**")
                            ans=st.radio("Choix", opts, key=f"qr_{q['id']}", index=None)
                            if ans is not None: st.session_state.quiz_answers[q["id"]]=[opts.index(ans)]
                    if st.button("✅ Valider", type="primary", use_container_width=True):
                        res=calculate_quiz_score(st.session_state.quiz_answers, qs)
                        st.metric("Score /20", res["score20"]); st.metric("%", f"{res['pct']:.1f}%")
                        execute("INSERT INTO quiz_results(quiz_id,score,total,pourcentage,created_at) VALUES(?,?,?,?)",(qid,res["score20"],res["total"],res["pct"],datetime.now().isoformat()))
                        st.balloons()
        else: st.info("Crée un quiz dans l'ancien fichier complet si besoin")

    elif page=="Statistiques":
        qr=fetch_all("SELECT qr.*, q.titre FROM quiz_results qr JOIN quiz q ON qr.quiz_id=q.id")
        if qr:
            df=pd.DataFrame(qr); st.dataframe(df); st.plotly_chart(px.line(df, x="created_at", y="pourcentage", title="Évolution"), use_container_width=True)
        else: st.info("Fais un quiz pour voir tes stats")

    else:
        with st.container(border=True):
            st.info(f"Module {page} - version beautiful ultra-light. Toutes les fonctions sont dans la version complète, le design est déjà actif ici.")

st.divider()
st.caption("✨ GLAR Revision Hub • Beautiful Edition • Vert #1B4332 • Or #D4A017 • Design sans bug React")
