
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import json
from database import init_db, fetch_all, fetch_one, execute, get_storage_info
from utils import extract_text_from_pdf, extract_text_from_txt, generate_fiche_auto, calculate_quiz_score, spaced_next_review
from config import APP_NAME, APP_VERSION, SEMESTRES, NIVEAUX_DIFFICULTE, STATUTS_REVISION

st.set_page_config(page_title=APP_NAME, page_icon="🎓", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@600;700;800&display=swap');
.stApp { background: radial-gradient(1200px 600px at 10% -10%, #E8F5E9 0%, transparent 60%), radial-gradient(1000px 500px at 90% 0%, #FFF8E1 0%, transparent 60%), linear-gradient(180deg, #F6F8F3 0%, #FFFFFF 70%); }
section[data-testid="stSidebar"] { background: linear-gradient(180deg, #0F2A1E 0%, #1B4332 50%, #2D6A4F 100%) !important; }
section[data-testid="stSidebar"] * { color: #E8F5E9 !important; }
section[data-testid="stSidebar"] button { background: rgba(255,255,255,0.08) !important; border: 1px solid rgba(255,255,255,0.12) !important; border-radius: 12px !important; }
section[data-testid="stSidebar"] button:hover { background: rgba(212,160,23,0.25) !important; border-color: #D4A017 !important; transform: translateX(3px); }
div[data-testid="stMetric"] { background: white !important; border-radius: 16px !important; border: 1px solid #EDEBE3 !important; box-shadow: 0 8px 20px rgba(27,67,50,0.06) !important; padding: 16px !important; }
div[data-testid="stExpander"] { border-radius: 14px !important; border: 1px solid #EDEBE3 !important; background: white !important; }
button[data-baseweb="tab"][aria-selected="true"] { background: #1B4332 !important; color: white !important; border-radius: 10px !important; }
button[kind="primary"] { background: linear-gradient(135deg, #1B4332 0%, #2D6A4F 100%) !important; border-radius: 12px !important; box-shadow: 0 6px 16px rgba(27,67,50,0.3) !important; }
.gold-badge { background: linear-gradient(135deg, #D4A017 0%, #F4D35E 100%); color: #1B4332; padding: 6px 14px; border-radius: 20px; font-weight: 800; font-size: 0.75rem; display: inline-block; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

init_db()
try:
    from data.seed import seed_all
    seed_all()
except: pass

for k,v in [("page","Tableau de bord"),("quiz_answers",{}),("quiz_started",{}),("flash_idx",0),("show_correction",{}),("reveal",False)]:
    if k not in st.session_state: st.session_state[k]=v

with st.sidebar:
    st.markdown("### 🎓 GLAR HUB")
    st.markdown('<span class="gold-badge">✨ L3 GLAR • ESTM DAKAR • FINAL</span>', unsafe_allow_html=True)
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
    st.markdown('<span class="gold-badge">✨ FINAL BEAUTIFUL + COMPLET</span>', unsafe_allow_html=True)
    st.title("GLAR REVISION HUB")
    st.caption("Assistant personnel L3 Génie Logiciel & Réseaux • Design Vert #1B4332 • Or #D4A017")
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


elif page=="Matières":
    st.title("📚 Matières")
    st.caption("Ajoute tes matières ESTM, modifie-les, supprime celles qui ne sont plus au programme")
    tab1,tab2,tab3=st.tabs(["🖼️ Galerie (Gérer)","➕ Ajouter","✏️ Modifier / Supprimer"])
    matieres_all=fetch_all("SELECT * FROM matieres ORDER BY semestre, nom")
    with tab1:
        if not matieres_all:
            with st.container(border=True):
                st.info("Aucune matière - va dans Ajouter")
        else:
            cols=st.columns(3)
            for i,m in enumerate(matieres_all):
                with cols[i%3]:
                    with st.container(border=True):
                        st.markdown(f"**{m['nom']}**")
                        st.caption(f"{m['semestre']} • {m['difficulte']} • {m['statut']}")
                        st.write(m["description"][:90]+"...")
                        st.progress(m["objectif"]/100, text=f"Objectif {m['objectif']}%")
                        c1,c2,c3=st.columns(3)
                        with c1:
                            if st.button("▶️", key=f"m_en_{m['id']}", help="Passer en cours"):
                                execute("UPDATE matieres SET statut='En cours' WHERE id=?", (m["id"],))
                                st.toast(f"{m['nom']} → En cours"); st.rerun()
                        with c2:
                            if st.button("✅", key=f"m_ma_{m['id']}", help="Maîtrisé"):
                                execute("UPDATE matieres SET statut='Maîtrisé' WHERE id=?", (m["id"],))
                                st.toast(f"{m['nom']} → Maîtrisé"); st.rerun()
                        with c3:
                            if st.button("🗑️", key=f"m_del_{m['id']}", help="Supprimer cette matière"):
                                # Vérif si des cours liés
                                cours_lies=fetch_all("SELECT COUNT(*) as c FROM cours WHERE matiere_id=?", (m["id"],))
                                if cours_lies and cours_lies[0]["c"]>0:
                                    st.warning(f"{cours_lies[0]['c']} cours liés seront aussi supprimés!")
                                execute("DELETE FROM matieres WHERE id=?", (m["id"],))
                                st.success(f"{m['nom']} supprimée"); st.balloons(); st.rerun()
    with tab2:
        with st.container(border=True):
            st.markdown("### ➕ Ajouter une nouvelle matière")
            with st.form("mat_add", clear_on_submit=True, border=False):
                nom=st.text_input("Nom de la matière *", placeholder="Ex: Cloud & Docker Avancé")
                desc=st.text_area("Description", placeholder="Ce que tu dois maîtriser pour l'examen...")
                c1,c2=st.columns(2)
                with c1:
                    sem=st.selectbox("Semestre", SEMESTRES)
                    diff=st.selectbox("Difficulté", NIVEAUX_DIFFICULTE)
                with c2:
                    statut=st.selectbox("Statut initial", STATUTS_REVISION)
                    obj=st.slider("Objectif %", 50,100,80)
                submitted=st.form_submit_button("✨ Ajouter la matière", type="primary", use_container_width=True)
                if submitted:
                    if not nom.strip():
                        st.error("❌ Le nom est obligatoire!")
                    else:
                        existing=fetch_one("SELECT id FROM matieres WHERE nom=?", (nom.strip(),))
                        if existing:
                            st.error(f"❌ Une matière nommée '{nom}' existe déjà!")
                        else:
                            execute("INSERT INTO matieres(nom,description,semestre,difficulte,statut,objectif,created_at) VALUES(?,?,?,?,?,?,?)",(nom.strip(),desc,sem,diff,statut,obj,datetime.now().isoformat()))
                            st.success(f"✅ Matière '{nom}' ajoutée!"); log_activite("matiere", f"Ajout {nom}"); st.balloons(); st.rerun()
    with tab3:
        with st.container(border=True):
            st.markdown("### ✏️ Modifier ou Supprimer définitivement")
            if not matieres_all:
                st.info("Aucune matière à modifier")
            else:
                mat_options={f"{m['id']} - {m['nom']} ({m['semestre']})": m for m in matieres_all}
                selected_label=st.selectbox("Choisir la matière à gérer", list(mat_options.keys()))
                m_selected=mat_options[selected_label]
                st.divider()
                st.write(f"**Actuel:** {m_selected['nom']} | {m_selected['semestre']} | {m_selected['difficulte']} | {m_selected['statut']} | {m_selected['objectif']}%")
                st.write(f"Description: {m_selected['description']}")
                # Stats liées
                nb_cours=fetch_all("SELECT COUNT(*) as c FROM cours WHERE matiere_id=?", (m_selected["id"],))
                nb_fiches=fetch_all("SELECT COUNT(*) as c FROM fiches WHERE matiere_id=?", (m_selected["id"],))
                nb_quiz=fetch_all("SELECT COUNT(*) as c FROM quiz WHERE matiere_id=?", (m_selected["id"],))
                st.caption(f"📄 {nb_cours[0]['c'] if nb_cours else 0} cours | 📝 {nb_fiches[0]['c'] if nb_fiches else 0} fiches | ❓ {nb_quiz[0]['c'] if nb_quiz else 0} quiz liés")
                st.divider()
                with st.form("mat_edit_form"):
                    new_nom=st.text_input("Nom", value=m_selected["nom"])
                    new_desc=st.text_area("Description", value=m_selected["description"])
                    c1,c2=st.columns(2)
                    with c1:
                        new_sem=st.selectbox("Semestre", SEMESTRES, index=SEMESTRES.index(m_selected["semestre"]) if m_selected["semestre"] in SEMESTRES else 0)
                        new_diff=st.selectbox("Difficulté", NIVEAUX_DIFFICULTE, index=NIVEAUX_DIFFICULTE.index(m_selected["difficulte"]) if m_selected["difficulte"] in NIVEAUX_DIFFICULTE else 0)
                    with c2:
                        new_statut=st.selectbox("Statut", STATUTS_REVISION, index=STATUTS_REVISION.index(m_selected["statut"]) if m_selected["statut"] in STATUTS_REVISION else 0)
                        new_obj=st.slider("Objectif %", 50,100,m_selected["objectif"])
                    c_save,c_del=st.columns(2)
                    with c_save:
                        save=st.form_submit_button("💾 Enregistrer modifications", type="primary", use_container_width=True)
                    with c_del:
                        delete=st.form_submit_button("🗑️ Supprimer DÉFINITIVEMENT", type="secondary", use_container_width=True)
                    if save:
                        if not new_nom.strip():
                            st.error("Nom obligatoire!")
                        else:
                            execute("UPDATE matieres SET nom=?, description=?, semestre=?, difficulte=?, statut=?, objectif=? WHERE id=?", (new_nom.strip(),new_desc,new_sem,new_diff,new_statut,new_obj,m_selected["id"]))
                            st.success(f"✅ '{new_nom}' modifiée!"); st.rerun()
                    if delete:
                        # Double confirmation via checkbox outside form would be better, but we do it here
                        execute("DELETE FROM matieres WHERE id=?", (m_selected["id"],))
                        # Cascade manually for safety (SQLite foreign key may not be enforced)
                        execute("DELETE FROM chapitres WHERE matiere_id=?", (m_selected["id"],))
                        execute("DELETE FROM cours WHERE matiere_id=?", (m_selected["id"],))
                        execute("DELETE FROM fiches WHERE matiere_id=?", (m_selected["id"],))
                        execute("DELETE FROM quiz WHERE matiere_id=?", (m_selected["id"],))
                        st.success(f"🗑️ Matière '{m_selected['nom']}' et tout son contenu supprimés!"); st.balloons(); st.rerun()


elif page=="Cours & Documents":
    st.title("📄 Cours & Documents")
    matieres=fetch_all("SELECT * FROM matieres"); mat_map={m["nom"]: m["id"] for m in matieres}
    t1,t2,t3=st.tabs(["📤 Importer","📚 Mes cours","🔍 Recherche"])
    with t1:
        with st.container(border=True):
            with st.form("imp", clear_on_submit=True):
                titre=st.text_input("Titre *", placeholder="Chapitre 3 - VLAN")
                mat_nom=st.selectbox("Matière", list(mat_map.keys()) if mat_map else ["Aucune"])
                chapitres=fetch_all("SELECT * FROM chapitres WHERE matiere_id=?", (mat_map.get(mat_nom,0),)) if mat_map else []
                chap_map={c["titre"]: c["id"] for c in chapitres}
                chap_sel=st.selectbox("Chapitre (optionnel)", ["Aucun"]+list(chap_map.keys()))
                up=st.file_uploader("PDF/TXT/MD (15 Mo max)", type=["pdf","txt","md"])
                manual=st.text_area("Ou colle le texte ici", height=150, placeholder="Colle ton cours si PDF scanné...")
                notes=st.text_area("📝 Notes perso")
                if st.form_submit_button("💾 Enregistrer", type="primary", use_container_width=True):
                    if titre:
                        txt=manual
                        fname=None
                        if up:
                            fname=up.name
                            b=up.read()
                            r=extract_text_from_pdf(b) if fname.lower().endswith(".pdf") else extract_text_from_txt(b)
                            if r["success"]: txt=r["text"][:20000]; st.success(f"✅ {len(txt)} caractères extraits")
                            else: st.warning(r["warning"]); txt=manual
                        execute("INSERT INTO cours(matiere_id,chapitre_id,titre,contenu,fichier_nom,notes,created_at) VALUES(?,?,?,?,?,?,?)",(mat_map.get(mat_nom),chap_map.get(chap_sel) if chap_sel!="Aucun" else None,titre,txt,fname,notes,datetime.now().isoformat()))
                        st.success("Cours enregistré!"); log_activite("cours", f"Import {titre}", mat_map.get(mat_nom), 15); st.balloons()
    with t2:
        cours=fetch_all("SELECT c.*, m.nom as matiere_nom FROM cours c LEFT JOIN matieres m ON c.matiere_id=m.id ORDER BY c.created_at DESC")
        for c in cours:
            with st.container(border=True):
                st.write(f"**{c['titre']}** · {c['matiere_nom'] or ''}")
                st.caption(f"{c['created_at'][:16]} • {c['fichier_nom'] or 'Manuel'}")
                st.text((c["contenu"][:400] if c["contenu"] else "Pas de contenu")+"...")
                if c["notes"]: st.info(f"Notes: {c['notes']}")
                if st.button("🗑️ Supprimer", key=f"dc_{c['id']}"): execute("DELETE FROM cours WHERE id=?", (c["id"],)); st.rerun()
    with t3:
        q=st.text_input("🔍 Recherche plein texte", placeholder="OSPF, SOLID, Docker...")
        if q:
            res=fetch_all("SELECT * FROM cours WHERE contenu LIKE ? OR titre LIKE ?", (f"%{q}%", f"%{q}%"))
            st.write(f"{len(res)} résultats")
            for r in res:
                with st.container(border=True): st.write(f"**{r['titre']}**"); st.caption(r['contenu'][:200])

elif page=="Fiches":
    st.title("📝 Fiches de révision")
    matieres=fetch_all("SELECT * FROM matieres"); mat_map={m["nom"]: m["id"] for m in matieres}
    t1,t2,t3=st.tabs(["✨ Auto depuis cours","✍️ Manuel","📚 Mes fiches"])
    with t1:
        cours=fetch_all("SELECT c.*, m.nom as mat_nom FROM cours c LEFT JOIN matieres m ON c.matiere_id=m.id")
        if not cours: st.info("Importe d'abord un cours")
        else:
            sel=st.selectbox("Choisir un cours", [f"{c['id']} - {c['titre']}" for c in cours])
            if st.button("✨ Générer fiche auto", type="primary", use_container_width=True):
                cid=int(sel.split(" - ")[0]); cobj=fetch_one("SELECT * FROM cours WHERE id=?", (cid,))
                if cobj and cobj["contenu"]:
                    fd=generate_fiche_auto(cobj["contenu"], cobj["titre"])
                    execute("INSERT INTO fiches(matiere_id,chapitre_id,titre,notions,definitions,points_cles,formules,exemples,erreurs,resume,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?)",(cobj["matiere_id"],cobj["chapitre_id"],f"Fiche - {cobj['titre']}",fd["notions"],fd["definitions"],fd["points_cles"],fd["formules"],fd["exemples"],fd["erreurs"],fd["resume"],datetime.now().isoformat()))
                    st.success("Fiche générée!"); log_activite("fiche", f"Auto {cobj['titre']}", cobj["matiere_id"]); st.balloons()
                else: st.error("Contenu vide")
    with t2:
        with st.form("fiche_man", clear_on_submit=True, border=True):
            titre=st.text_input("Titre fiche *")
            mat_nom=st.selectbox("Matière", list(mat_map.keys()) if mat_map else ["Aucune"])
            notions=st.text_area("Notions essentielles")
            definitions=st.text_area("Définitions")
            points=st.text_area("Points clés")
            formules=st.text_area("Formules / Syntaxes")
            exemples=st.text_area("Exemples pratiques")
            erreurs=st.text_area("Erreurs fréquentes")
            resume=st.text_area("Résumé final")
            if st.form_submit_button("Enregistrer", type="primary", use_container_width=True):
                if titre:
                    execute("INSERT INTO fiches(matiere_id,titre,notions,definitions,points_cles,formules,exemples,erreurs,resume,created_at) VALUES(?,?,?,?,?,?,?,?,?,?)",(mat_map.get(mat_nom),titre,notions,definitions,points,formules,exemples,erreurs,resume,datetime.now().isoformat()))
                    st.success("Fiche enregistrée!")
    with t3:
        fiches=fetch_all("SELECT f.*, m.nom as mat_nom FROM fiches f LEFT JOIN matieres m ON f.matiere_id=m.id ORDER BY f.created_at DESC")
        for f in fiches:
            with st.container(border=True):
                st.markdown(f"### 📝 {f['titre']} · {f['mat_nom'] or ''}")
                c1,c2=st.columns(2)
                with c1:
                    st.write(f"**Notions:** {f['notions'][:300]}")
                    st.write(f"**Définitions:** {f['definitions'][:300]}")
                with c2:
                    st.write(f"**Points clés:** {f['points_cles'][:300]}")
                    st.write(f"**Formules:** {f['formules'][:200]}")
                st.info(f"**Résumé:** {f['resume'][:400]}")
                if st.button("Suppr fiche", key=f"df_{f['id']}"): execute("DELETE FROM fiches WHERE id=?", (f["id"],)); st.rerun()

elif page=="Quiz & QCM":
    st.title("❓ Quiz & QCM")
    matieres=fetch_all("SELECT * FROM matieres"); mat_map={m["nom"]: m["id"] for m in matieres}
    t_list,t_create,t_hist=st.tabs(["🎯 Passer","➕ Créer","📊 Historique"])
    with t_list:
        quizzes=fetch_all("SELECT q.*, m.nom as mat_nom FROM quiz q LEFT JOIN matieres m ON q.matiere_id=m.id")
        if not quizzes: st.info("Aucun quiz - crée ton premier dans l'onglet Créer")
        else:
            q_sel=st.selectbox("Choisir quiz", [f"{q['id']} - {q['titre']} ({q['mat_nom']})" for q in quizzes])
            qid=int(q_sel.split(" - ")[0])
            questions=fetch_all("SELECT * FROM questions WHERE quiz_id=?", (qid,))
            if not questions: st.warning("Pas de questions pour ce quiz")
            else:
                mode=st.radio("Mode correction", ["À la fin","Après chaque question"], horizontal=True)
                nb_q=st.slider("Nombre de questions", 1, len(questions), len(questions), key="nbq")
                selected_q=questions[:nb_q]
                if st.button("🚀 Démarrer quiz", type="primary", use_container_width=True):
                    st.session_state.quiz_answers={}; st.session_state.quiz_started[qid]=datetime.now(); st.rerun()
                if qid in st.session_state.quiz_started:
                    st.divider()
                    for q in selected_q:
                        with st.container(border=True):
                            opts=json.loads(q["options"]); corrects=json.loads(q["reponses_correctes"])
                            st.markdown(f"**{q['question']}** *({q['difficulte']})*")
                            if q["type"]=="multiple":
                                ans=st.multiselect(f"Choix", opts, key=f"q_{q['id']}")
                                mapped=[opts.index(a) for a in ans if a in opts]
                                st.session_state.quiz_answers[q["id"]]=mapped
                            else:
                                ans=st.radio(f"Choix", opts, key=f"qr_{q['id']}", index=None)
                                if ans is not None: st.session_state.quiz_answers[q["id"]]=[opts.index(ans)]
                            if mode=="Après chaque question" and q["id"] in st.session_state.quiz_answers:
                                given=st.session_state.quiz_answers[q["id"]]
                                if set(map(str,given))==set(map(str,corrects)): st.success(f"✅ Correct! {q['explication']}")
                                else: st.error(f"❌ Raté. Attendu: {[opts[i] for i in corrects]} — {q['explication']}")
                    if st.button("✅ Valider et voir score", type="primary", use_container_width=True):
                        res=calculate_quiz_score(st.session_state.quiz_answers, selected_q)
                        st.balloons()
                        c1,c2,c3=st.columns(3)
                        c1.metric("Score /20", res["score20"]); c2.metric("%", f"{res['pct']:.1f}%"); c3.metric("Correct", f"{res['correct']}/{res['total']}")
                        start=st.session_state.quiz_started.get(qid, datetime.now())
                        elapsed=int((datetime.now()-start).total_seconds())
                        execute("INSERT INTO quiz_results(quiz_id,score,total,pourcentage,temps_sec,details,created_at) VALUES(?,?,?,?,?,?,?)",(qid,res["score20"],res["total"],res["pct"],elapsed,json.dumps(res["details"]),datetime.now().isoformat()))
                        log_activite("quiz", f"Quiz {qid} - {res['pct']:.0f}%", None, elapsed//60)
    with t_create:
        with st.form("create_quiz", clear_on_submit=True, border=True):
            titre=st.text_input("Titre quiz *")
            mat_nom=st.selectbox("Matière", list(mat_map.keys()) if mat_map else ["Aucune"])
            diff=st.selectbox("Difficulté", NIVEAUX_DIFFICULTE)
            if st.form_submit_button("Créer quiz", type="primary", use_container_width=True):
                if titre:
                    qid=execute("INSERT INTO quiz(matiere_id,titre,difficulte,created_at) VALUES(?,?,?,?)", (mat_map.get(mat_nom),titre,diff,datetime.now().isoformat()))
                    st.success(f"Quiz {qid} créé")
        st.divider()
        quizzes=fetch_all("SELECT * FROM quiz ORDER BY id DESC")
        if quizzes:
            q_sel2=st.selectbox("Ajouter question à", [f"{q['id']} - {q['titre']}" for q in quizzes], key="qadd")
            with st.form("add_q", clear_on_submit=True, border=True):
                question=st.text_area("Question *")
                type_q=st.selectbox("Type", ["unique","multiple"])
                opt1=st.text_input("Option 1 *"); opt2=st.text_input("Option 2 *"); opt3=st.text_input("Option 3"); opt4=st.text_input("Option 4")
                correct_str=st.text_input("Indices corrects (ex: 0 ou 0,1) *"); expl=st.text_area("Explication"); diff_q=st.selectbox("Difficulté question", NIVEAUX_DIFFICULTE, key="diff_q")
                if st.form_submit_button("Ajouter question", type="primary"):
                    if question and opt1 and opt2 and correct_str:
                        opts=[o for o in [opt1,opt2,opt3,opt4] if o]
                        try:
                            corrects=[int(x.strip()) for x in correct_str.split(",")]
                            qid=int(q_sel2.split(" - ")[0])
                            execute("INSERT INTO questions(quiz_id,question,type,options,reponses_correctes,explication,difficulte) VALUES(?,?,?,?,?,?,?)",(qid,question,type_q,json.dumps(opts),json.dumps(corrects),expl,diff_q))
                            st.success("Question ajoutée")
                        except Exception as e: st.error(f"Erreur: {e}")
    with t_hist:
        hist=fetch_all("SELECT qr.*, q.titre, m.nom as mat_nom FROM quiz_results qr JOIN quiz q ON qr.quiz_id=q.id LEFT JOIN matieres m ON q.matiere_id=m.id ORDER BY qr.created_at DESC")
        if hist:
            df=pd.DataFrame(hist)
            st.dataframe(df[["created_at","titre","mat_nom","score","pourcentage","temps_sec"]], use_container_width=True)
            try:
                fig=px.line(df, x="created_at", y="pourcentage", color="mat_nom", title="Évolution scores", markers=True)
                fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig, use_container_width=True)
            except: pass
        else: st.info("Pas encore de résultats")

elif page=="Exercices":
    st.title("💻 Exercices pratiques")
    cat_filter=st.selectbox("Filtrer catégorie", ["Tous","POO","SQL","Réseaux","Linux","Algo","Web","UML"])
    if cat_filter=="Tous": exos=fetch_all("SELECT e.*, m.nom as mat_nom FROM exercices e LEFT JOIN matieres m ON e.matiere_id=m.id ORDER BY e.created_at DESC")
    else: exos=fetch_all("SELECT e.*, m.nom as mat_nom FROM exercices e LEFT JOIN matieres m ON e.matiere_id=m.id WHERE e.categorie=? ORDER BY e.created_at DESC", (cat_filter,))
    for e in exos:
        with st.container(border=True):
            st.markdown(f"### 💻 {e['titre']} · `{e['categorie']}` · {e['difficulte']} · {e['mat_nom'] or ''}")
            st.write(f"**Énoncé:** {e['enonce']}")
            st.caption(f"Objectifs: {e['objectifs']}")
            st.text_area("Ta réponse", key=f"rep_{e['id']}", placeholder="Écris ta solution ici...")
            if st.button("👁️ Voir correction", key=f"cor_{e['id']}"): st.session_state.show_correction[e['id']]=True
            if st.session_state.show_correction.get(e['id']):
                st.success(f"**Solution:** {e['solution']}")
                st.warning(f"**Erreurs à éviter:** {e['erreurs']}")
    st.divider()
    matieres=fetch_all("SELECT * FROM matieres"); mat_map={m["nom"]: m["id"] for m in matieres}
    with st.container(border=True):
        st.subheader("➕ Créer un exercice")
        with st.form("ex_form", clear_on_submit=True):
            titre=st.text_input("Titre *"); mat_nom=st.selectbox("Matière", list(mat_map.keys()) if mat_map else ["Aucune"])
            enonce=st.text_area("Énoncé *"); objectifs=st.text_input("Objectifs"); diff=st.selectbox("Difficulté", NIVEAUX_DIFFICULTE); cat=st.text_input("Catégorie (POO, SQL...)")
            solution=st.text_area("Solution"); erreurs=st.text_area("Erreurs à éviter")
            if st.form_submit_button("Enregistrer", type="primary", use_container_width=True):
                if titre and enonce:
                    execute("INSERT INTO exercices(matiere_id,titre,enonce,objectifs,difficulte,solution,erreurs,categorie,created_at) VALUES(?,?,?,?,?,?,?,?,?)",(mat_map.get(mat_nom),titre,enonce,objectifs,diff,solution,erreurs,cat,datetime.now().isoformat()))
                    st.success("Exercice ajouté!")

elif page=="Assistant":
    st.title("🤖 Assistant de révision")
    with st.container(border=True):
        st.info("Assistant local - cherche d'abord dans TES cours importés. Option OpenAI via st.secrets si tu configures une clé.")
        q=st.text_input("Pose ta question", placeholder="Explique-moi la POO simplement, ou résume VLAN...")
        if q:
            cours=fetch_all("SELECT * FROM cours WHERE contenu LIKE ? LIMIT 5", (f"%{q.split()[0]}%",))
            if cours:
                st.write(f"📚 {len(cours)} cours trouvés avec ce mot-clé")
                for c in cours:
                    with st.expander(f"{c['titre']}"): st.text(c['contenu'][:800])
            qlow=q.lower()
            if "poo" in qlow or "objet" in qlow: st.success("**POO simplifiée:** Classe = moule, Objet = instance. 3 piliers: Encapsulation (private), Héritage (extends), Polymorphisme (override). Ex: class Chien(Animal): def aboyer(self): print('wouaf')")
            elif "réseau" in qlow or "tcp" in qlow or "vlan" in qlow: st.success("**Réseaux:** TCP fiable (3-way handshake SYN/SYN-ACK/ACK), UDP rapide. VLAN = séparation broadcast (802.1Q). OSPF = link-state.")
            elif "sql" in qlow: st.success("**SQL avancé:** INDEX pour perfs, EXPLAIN ANALYZE, RANK() OVER(PARTITION BY dept ORDER BY salaire DESC), CTE WITH.")
            elif "45" in qlow or "séance" in qlow: st.success("**Séance 45 min:** 10 min rappel fiche, 20 min exo, 10 min QCM, 5 min nouvelle fiche.")
            else: st.write(f"Réponse locale pour '{q}' — importe tes PDFs pour enrichir le contexte. Configure st.secrets['openai']['api_key'] pour IA externe.")

elif page=="Flashcards":
    st.title("🃏 Flashcards & Révision espacée")
    t1,t2=st.tabs(["🎯 Réviser","➕ Gérer"])
    with t2:
        matieres=fetch_all("SELECT * FROM matieres"); mat_map={m["nom"]: m["id"] for m in matieres}
        with st.form("flash_form", clear_on_submit=True, border=True):
            mat_nom=st.selectbox("Matière", list(mat_map.keys()) if mat_map else ["Aucune"])
            chapitres=fetch_all("SELECT * FROM chapitres WHERE matiere_id=?", (mat_map.get(mat_nom,0),)) if mat_map else []
            chap_map={c["titre"]: c["id"] for c in chapitres}
            chap_sel=st.selectbox("Chapitre", ["Aucun"]+list(chap_map.keys()))
            q=st.text_input("Question face avant *"); r=st.text_area("Réponse face arrière *")
            if st.form_submit_button("Ajouter carte", type="primary", use_container_width=True):
                if q and r:
                    execute("INSERT INTO flashcards(matiere_id,chapitre_id,question,reponse,statut,next_review,created_at) VALUES(?,?,?,?,?,?,?)",(mat_map.get(mat_nom),chap_map.get(chap_sel) if chap_sel!="Aucun" else None,q,r,"À revoir",spaced_next_review("À revoir"),datetime.now().isoformat()))
                    st.success("Carte ajoutée!")
        cards=fetch_all("SELECT f.*, m.nom as mat_nom FROM flashcards f LEFT JOIN matieres m ON f.matiere_id=m.id ORDER BY f.created_at DESC")
        for c in cards:
            with st.container(border=True):
                st.write(f"**{c['question'][:80]}** — {c['statut']} — {c['mat_nom'] or ''}")
                st.caption(f"Réponse: {c['reponse'][:150]}")
                if st.button("Suppr", key=f"dfc_{c['id']}"): execute("DELETE FROM flashcards WHERE id=?", (c["id"],)); st.rerun()
    with t1:
        cards=fetch_all("SELECT * FROM flashcards ORDER BY next_review ASC")
        if not cards: st.info("Aucune carte - crée ta première!")
        else:
            idx=st.session_state.flash_idx % len(cards); card=cards[idx]
            with st.container(border=True):
                st.markdown(f"### Carte {idx+1}/{len(cards)} — {card['statut']}")
                st.markdown(f"## {card['question']}")
                if st.button("🔍 Révéler réponse", type="primary", use_container_width=True): st.session_state.reveal=True
                if st.session_state.get("reveal"):
                    st.success(f"{card['reponse']}")
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
                if st.button("Suivant →"): st.session_state.flash_idx+=1; st.session_state.reveal=False; st.rerun()

elif page=="Planning":
    st.title("🗓️ Planning de révision")
    matieres=fetch_all("SELECT * FROM matieres"); mat_map={m["nom"]: m["id"] for m in matieres}
    chapitres_all=fetch_all("SELECT * FROM chapitres"); chap_map={f"{c['id']} - {c['titre']}": c["id"] for c in chapitres_all}
    with st.container(border=True):
        with st.form("plan_form", clear_on_submit=True):
            st.markdown("### Nouvelle séance")
            titre=st.text_input("Titre séance *", placeholder="Révision VLAN + exo")
            c1,c2=st.columns(2)
            with c1:
                mat_nom=st.selectbox("Matière", list(mat_map.keys()) if mat_map else ["Aucune"])
                chap_sel=st.selectbox("Chapitre", ["Aucun"]+list(chap_map.keys()))
            with c2:
                date=st.date_input("Date", datetime.now().date())
                duree=st.number_input("Durée min", 15,240,60, step=15)
                priorite=st.selectbox("Priorité", ["Basse","Moyenne","Haute","Critique"])
            if st.form_submit_button("Ajouter séance", type="primary", use_container_width=True):
                if titre:
                    execute("INSERT INTO planning(matiere_id,chapitre_id,titre,date,duree,priorite,statut,created_at) VALUES(?,?,?,?,?,?,?,?)",(mat_map.get(mat_nom),chap_map.get(chap_sel) if chap_sel!="Aucun" else None,titre,date.isoformat(),duree,priorite,"Prévu",datetime.now().isoformat()))
                    st.success("Séance ajoutée!")
    sessions=fetch_all("SELECT p.*, m.nom as mat_nom FROM planning p LEFT JOIN matieres m ON p.matiere_id=m.id ORDER BY p.date ASC")
    today=datetime.now().date()
    retard=[s for s in sessions if datetime.fromisoformat(s["date"]).date() < today and s["statut"]!="Terminée"]
    if retard:
        with st.container(border=True):
            st.warning(f"⚠️ {len(retard)} séances en retard!")
    for s in sessions:
        with st.container(border=True):
            c1,c2,c3=st.columns([3,1,1])
            with c1: st.write(f"**{s['titre']}** · {s['mat_nom'] or ''} · {s['date']} · {s['duree']}min · {s['priorite']} · {s['statut']}")
            with c2:
                if st.button("✅", key=f"done_{s['id']}"):
                    execute("UPDATE planning SET statut='Terminée' WHERE id=?", (s["id"],))
                    log_activite("planning", f"Terminée {s['titre']}", s["matiere_id"], s["duree"]); st.rerun()
            with c3:
                if st.button("🗑️", key=f"del_{s['id']}"):
                    execute("DELETE FROM planning WHERE id=?", (s["id"],)); st.rerun()
    if st.button("✨ Générer suggestions selon faiblesses", use_container_width=True):
        faibles=fetch_all("SELECT m.id, m.nom FROM matieres m WHERE m.statut!='Maîtrisé' LIMIT 5")
        for i,fm in enumerate(faibles):
            d=(today + timedelta(days=i)).isoformat()
            execute("INSERT INTO planning(matiere_id,titre,date,duree,priorite,statut,created_at) VALUES(?,?,?,?,?,?,?)",(fm["id"],f"Révision {fm['nom']}",d,60,"Haute","Prévu",datetime.now().isoformat()))
        st.success("Planning généré!"); st.rerun()

elif page=="Statistiques":
    st.title("📊 Statistiques & Progression")
    quiz_res=fetch_all("SELECT qr.*, q.titre, m.nom as mat_nom FROM quiz_results qr JOIN quiz q ON qr.quiz_id=q.id LEFT JOIN matieres m ON q.matiere_id=m.id")
    if not quiz_res:
        with st.container(border=True): st.info("Pas encore de données - passe un quiz!")
    else:
        df=pd.DataFrame(quiz_res)
        c1,c2,c3=st.columns(3)
        with c1:
            with st.container(border=True): st.metric("Score moyen /20", round(df["score"].mean(),2))
        with c2:
            with st.container(border=True): st.metric("Meilleur %", f"{df['pourcentage'].max():.1f}%")
        with c3:
            with st.container(border=True): st.metric("Temps total", f"{int(df['temps_sec'].sum()//60)} min")
        with st.container(border=True):
            try:
                fig1=px.line(df, x="created_at", y="pourcentage", color="mat_nom", title="Évolution des scores", markers=True)
                fig1.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig1, use_container_width=True)
                fig2=px.bar(df.groupby("mat_nom")["pourcentage"].mean().reset_index(), x="mat_nom", y="pourcentage", title="Taux réussite par matière", color="pourcentage", color_continuous_scale=["#E8F5E9","#2D6A4F"])
                fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig2, use_container_width=True)
            except Exception as e: st.write(e)
        with st.container(border=True):
            st.markdown("### 💡 Recommandations")
            low=df[df["pourcentage"]<60]
            if not low.empty:
                for _, row in low.iterrows(): st.warning(f"À revoir: {row['mat_nom']} - {row['titre']} ({row['pourcentage']}%)")
            else: st.success("Bonne progression!")

st.divider()
st.caption("✨ GLAR Revision Hub • Final Beautiful Complet • ESTM Dakar • Vert #1B4332 • Or #D4A017 • 10 modules fonctionnels")
