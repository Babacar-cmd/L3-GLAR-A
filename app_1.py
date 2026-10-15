
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import json, os, base64
from database import init_db, fetch_all, fetch_one, execute, get_storage_info
from utils import extract_text_from_pdf, extract_text_from_txt, generate_fiche_auto, calculate_quiz_score, spaced_next_review
from config import APP_NAME, APP_VERSION, SEMESTRES, NIVEAUX_DIFFICULTE, STATUTS_REVISION

st.set_page_config(page_title=APP_NAME, page_icon="🎓", layout="wide", initial_sidebar_state="expanded")

# Helper to encode image to base64 for CSS background
def img_to_base64(path):
    try:
        if not os.path.exists(path): return ""
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except: return ""

logo_path = "assets/estm_logo.png"
photo_path = "assets/Babacar_Mbow.jpg"
logo_b64 = img_to_base64(logo_path)
photo_b64 = img_to_base64(photo_path)

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@600;700;800&display=swap');
.stApp {{ background: radial-gradient(1200px 600px at 10% -10%, #E8F5E9 0%, transparent 60%), radial-gradient(1000px 500px at 90% 0%, #FFF8E1 0%, transparent 60%), linear-gradient(180deg, #F6F8F3 0%, #FFFFFF 70%); }}
section[data-testid="stSidebar"] {{ background: linear-gradient(180deg, #0F2A1E 0%, #1B4332 50%, #2D6A4F 100%) !important; }}
section[data-testid="stSidebar"] * {{ color: #E8F5E9 !important; }}
section[data-testid="stSidebar"] button {{ background: rgba(255,255,255,0.08) !important; border: 1px solid rgba(255,255,255,0.12) !important; border-radius: 12px !important; }}
section[data-testid="stSidebar"] button:hover {{ background: rgba(212,160,23,0.25) !important; border-color: #D4A017 !important; transform: translateX(3px); }}
div[data-testid="stMetric"] {{ background: white !important; border-radius: 16px !important; border: 1px solid #EDEBE3 !important; box-shadow: 0 8px 20px rgba(27,67,50,0.06) !important; padding: 16px !important; }}
div[data-testid="stExpander"] {{ border-radius: 14px !important; border: 1px solid #EDEBE3 !important; background: white !important; }}
button[data-baseweb="tab"][aria-selected="true"] {{ background: #1B4332 !important; color: white !important; border-radius: 10px !important; }}
button[kind="primary"] {{ background: linear-gradient(135deg, #1B4332 0%, #2D6A4F 100%) !important; border-radius: 12px !important; box-shadow: 0 6px 16px rgba(27,67,50,0.3) !important; }}
.gold-badge {{ background: linear-gradient(135deg, #D4A017 0%, #F4D35E 100%); color: #1B4332; padding: 6px 14px; border-radius: 20px; font-weight: 800; font-size: 0.75rem; display: inline-block; margin-bottom: 10px; }}

.watermark {
    position: fixed;
    bottom: 12px;
    right: 18px;
    opacity: 0.18;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 1.2px;
    color: #1B4332;
    pointer-events: none;
    z-index: 9999;
    background: rgba(255,255,255,0.8);
    padding: 6px 12px;
    border-radius: 20px;
    border: 1px solid rgba(27,67,50,0.1);
    backdrop-filter: blur(4px);
}
.watermark-photo {
    position: fixed;
    bottom: 50px;
    right: 18px;
    width: 38px;
    height: 38px;
    border-radius: 50%;
    opacity: 0.25;
    pointer-events: none;
    z-index: 9998;
    border: 2px solid #D4A017;
    object-fit: cover;
}

.profile-card {{ background: white; border-radius: 16px; padding: 16px; border: 1px solid #EDEBE3; box-shadow: 0 8px 20px rgba(0,0,0,0.06); display: flex; align-items: center; gap: 12px; }}

.watermark {
    position: fixed;
    bottom: 12px;
    right: 18px;
    opacity: 0.18;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 1.2px;
    color: #1B4332;
    pointer-events: none;
    z-index: 9999;
    background: rgba(255,255,255,0.8);
    padding: 6px 12px;
    border-radius: 20px;
    border: 1px solid rgba(27,67,50,0.1);
    backdrop-filter: blur(4px);
}
.watermark-photo {
    position: fixed;
    bottom: 50px;
    right: 18px;
    width: 38px;
    height: 38px;
    border-radius: 50%;
    opacity: 0.25;
    pointer-events: none;
    z-index: 9998;
    border: 2px solid #D4A017;
    object-fit: cover;
}

.profile-card img {{ width: 56px; height: 56px; border-radius: 50%; object-fit: cover; border: 2px solid #D4A017; }}
</style>
""", unsafe_allow_html=True)

init_db()

# Watermark signature sur toutes les pages - Babacar Mbow
st.markdown(f'''
<div class="watermark">© BABACAR MBOW • L3 GLAR • ESTM DAKAR • {datetime.now().year}</div>
''', unsafe_allow_html=True)

# Watermark photo mini en coin si image existe
if os.path.exists(photo_path) and photo_b64:
    st.markdown(f'''
    <style>
    .watermark-photo {{ background: url("data:image/jpeg;base64,{photo_b64}") center/cover; }}
    </style>
    <div class="watermark-photo"></div>
    ''', unsafe_allow_html=True)

try:
    from data.seed import seed_all
    seed_all()
except: pass

for k,v in [("page","Tableau de bord"),("quiz_answers",{}),("quiz_started",{}),("flash_idx",0),("show_correction",{}),("reveal",False)]:
    if k not in st.session_state: st.session_state[k]=v

with st.sidebar:
    # Logo ESTM en haut
    if os.path.exists(logo_path):
        st.image(logo_path, width=110)
    else:
        st.markdown("### 🎓 ESTM")
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
    # Photo Babacar en bas sidebar
    if os.path.exists(photo_path):
        st.image(photo_path, caption="Babacar Mbow • L3 GLAR", use_container_width=True)
    else:
        st.caption("Babacar Mbow • L3 GLAR")
    try:
        s=get_storage_info()
        st.caption(f"DB {s['size_kb']} KB • v{APP_VERSION}")
    except: pass

def log_activite(t,d,mid=None,dur=0):
    try: execute("INSERT INTO activites(type,description,matiere_id,duree,created_at) VALUES(?,?,?,?,?)",(t,d,mid,dur,datetime.now().isoformat()))
    except: pass

page=st.session_state.page

if page=="Tableau de bord":
    col_logo, col_title = st.columns([1,5])
    with col_logo:
        if os.path.exists(logo_path):
            st.image(logo_path, width=80)
    with col_title:
        st.markdown('<span class="gold-badge">✨ FINAL AVEC TES IMAGES</span>', unsafe_allow_html=True)
        st.title("GLAR REVISION HUB")
        st.caption("Babacar Mbow • L3 Génie Logiciel & Administration Réseaux • ESTM Dakar")

    # Carte profil
    with st.container(border=True):
        c1,c2 = st.columns([1,4])
        with c1:
            if os.path.exists(photo_path):
                st.image(photo_path, width=120)
        with c2:
            st.markdown("### 👨‍💻 Babacar Mbow")
            st.write("Étudiant L3 GLAR à l'ESTM Dakar. Passionné par le Génie Logiciel, l'Administration Réseaux et le Cloud. Cette application est ton cockpit personnel pour organiser tes cours, générer tes fiches et cartonner aux examens.")
            st.caption("Design Vert #1B4332 • Or #D4A017 • Photos intégrées")

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
                except: pass
            else: st.info("Fais ton premier quiz dans Quiz & QCM")
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
        # Mini carte ESTM
        with st.container(border=True):
            if os.path.exists(logo_path):
                st.image(logo_path, width=80)
            st.caption("ESTM Dakar • École Supérieure de Technologie et de Management")
            st.write("L3 GLAR • 2025-2026")

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
                    fd=generate_fiche_auto(cobj["contenu"], cobj["titre"])
                    execute("INSERT INTO fiches(matiere_id,titre,notions,definitions,points_cles,resume,created_at) VALUES(?,?,?,?,?,?,?)",(cobj["matiere_id"],f"Fiche - {cobj['titre']}",fd["notions"],fd["definitions"],fd["points_cles"],fd["resume"],datetime.now().isoformat()))
                    st.success("Fiche générée!"); st.balloons()
    with t2:
        with st.form("fiche_man", clear_on_submit=True, border=True):
            titre=st.text_input("Titre fiche *")
            notions=st.text_area("Notions"); definitions=st.text_area("Définitions"); points=st.text_area("Points clés"); resume=st.text_area("Résumé")
            if st.form_submit_button("Enregistrer", type="primary"):
                if titre:
                    execute("INSERT INTO fiches(titre,notions,definitions,points_cles,resume,created_at) VALUES(?,?,?,?,?,?)",(titre,notions,definitions,points,resume,datetime.now().isoformat()))
                    st.success("Enregistrée!")
    with t3:
        fiches=fetch_all("SELECT * FROM fiches ORDER BY created_at DESC")
        for f in fiches:
            with st.container(border=True):
                st.write(f"**{f['titre']}**"); st.caption(f['notions'][:200]); st.write(f['resume'][:300])

elif page=="Quiz & QCM":
    st.title("❓ Quiz & QCM")
    matieres=fetch_all("SELECT * FROM matieres"); mat_map={m["nom"]: m["id"] for m in matieres}
    t_list,t_create,t_hist=st.tabs(["🎯 Passer","➕ Créer","📊 Historique"])
    with t_list:
        quizzes=fetch_all("SELECT q.*, m.nom as mat_nom FROM quiz q LEFT JOIN matieres m ON q.matiere_id=m.id")
        if not quizzes: st.info("Aucun quiz")
        else:
            q_sel=st.selectbox("Choisir quiz", [f"{q['id']} - {q['titre']} ({q['mat_nom']})" for q in quizzes])
            qid=int(q_sel.split(" - ")[0]); questions=fetch_all("SELECT * FROM questions WHERE quiz_id=?", (qid,))
            if questions:
                if st.button("🚀 Démarrer", type="primary", use_container_width=True):
                    st.session_state.quiz_answers={}; st.session_state.quiz_started[qid]=datetime.now(); st.rerun()
                if qid in st.session_state.quiz_started:
                    for q in questions:
                        with st.container(border=True):
                            opts=json.loads(q["options"]); st.write(f"**{q['question']}**")
                            ans=st.radio("Choix", opts, key=f"qr_{q['id']}", index=None)
                            if ans is not None: st.session_state.quiz_answers[q["id"]]=[opts.index(ans)]
                    if st.button("✅ Valider", type="primary", use_container_width=True):
                        res=calculate_quiz_score(st.session_state.quiz_answers, questions)
                        st.metric("Score /20", res["score20"]); st.metric("%", f"{res['pct']:.1f}%")
                        execute("INSERT INTO quiz_results(quiz_id,score,total,pourcentage,created_at) VALUES(?,?,?,?)",(qid,res["score20"],res["total"],res["pct"],datetime.now().isoformat()))
                        st.balloons()
    with t_create:
        with st.form("create_quiz", clear_on_submit=True, border=True):
            titre=st.text_input("Titre quiz *"); diff=st.selectbox("Difficulté", NIVEAUX_DIFFICULTE)
            if st.form_submit_button("Créer", type="primary"):
                if titre:
                    qid=execute("INSERT INTO quiz(titre,difficulte,created_at) VALUES(?,?,?)",(titre,diff,datetime.now().isoformat()))
                    st.success(f"Quiz {qid} créé")
        quizzes=fetch_all("SELECT * FROM quiz ORDER BY id DESC")
        if quizzes:
            q_sel2=st.selectbox("Ajouter question à", [f"{q['id']} - {q['titre']}" for q in quizzes], key="qadd")
            with st.form("add_q", clear_on_submit=True, border=True):
                question=st.text_area("Question *"); opt1=st.text_input("Option 1 *"); opt2=st.text_input("Option 2 *"); opt3=st.text_input("Option 3"); opt4=st.text_input("Option 4")
                correct_str=st.text_input("Indice correct (0) *"); expl=st.text_area("Explication")
                if st.form_submit_button("Ajouter question"):
                    if question and opt1 and opt2 and correct_str:
                        opts=[o for o in [opt1,opt2,opt3,opt4] if o]
                        try:
                            corrects=[int(x.strip()) for x in correct_str.split(",")]
                            qid=int(q_sel2.split(" - ")[0])
                            execute("INSERT INTO questions(quiz_id,question,type,options,reponses_correctes,explication,difficulte) VALUES(?,?,?,?,?,?,?)",(qid,question,"unique",json.dumps(opts),json.dumps(corrects),expl,"Intermédiaire"))
                            st.success("Question ajoutée")
                        except Exception as e: st.error(f"{e}")
    with t_hist:
        hist=fetch_all("SELECT qr.*, q.titre FROM quiz_results qr JOIN quiz q ON qr.quiz_id=q.id ORDER BY qr.created_at DESC")
        if hist: st.dataframe(pd.DataFrame(hist)); 
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
c1,c2=st.columns([1,3])
with c1:
    if os.path.exists(logo_path): st.image(logo_path, width=60)
with c2:
    st.caption("✨ GLAR Revision Hub • Babacar Mbow • ESTM Dakar • Design Vert #1B4332 • Or #D4A017 • Avec tes images intégrées")
