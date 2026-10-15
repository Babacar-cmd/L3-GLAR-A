
import sqlite3, os
from datetime import datetime
DB_PATH=os.path.join(os.path.dirname(os.path.abspath(__file__)),"glar_revision.db")
def get_connection():
    conn=sqlite3.connect(DB_PATH, check_same_thread=False, timeout=10)
    conn.row_factory=sqlite3.Row
    return conn
def init_db():
    conn=get_connection(); cur=conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS matieres(id INTEGER PRIMARY KEY AUTOINCREMENT, nom TEXT UNIQUE, description TEXT, semestre TEXT, difficulte TEXT, statut TEXT DEFAULT 'Non commencé', objectif INTEGER DEFAULT 80, created_at TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS chapitres(id INTEGER PRIMARY KEY AUTOINCREMENT, matiere_id INTEGER, titre TEXT, contenu TEXT, ordre INTEGER DEFAULT 0, statut TEXT DEFAULT 'Non commencé', created_at TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS cours(id INTEGER PRIMARY KEY AUTOINCREMENT, matiere_id INTEGER, chapitre_id INTEGER, titre TEXT, contenu TEXT, fichier_nom TEXT, notes TEXT, created_at TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS fiches(id INTEGER PRIMARY KEY AUTOINCREMENT, matiere_id INTEGER, chapitre_id INTEGER, titre TEXT, notions TEXT, definitions TEXT, points_cles TEXT, formules TEXT, exemples TEXT, erreurs TEXT, resume TEXT, created_at TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS quiz(id INTEGER PRIMARY KEY AUTOINCREMENT, matiere_id INTEGER, titre TEXT, difficulte TEXT, created_at TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS questions(id INTEGER PRIMARY KEY AUTOINCREMENT, quiz_id INTEGER, question TEXT, type TEXT, options TEXT, reponses_correctes TEXT, explication TEXT, difficulte TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS quiz_results(id INTEGER PRIMARY KEY AUTOINCREMENT, quiz_id INTEGER, score REAL, total INTEGER, pourcentage REAL, temps_sec INTEGER, details TEXT, created_at TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS exercices(id INTEGER PRIMARY KEY AUTOINCREMENT, matiere_id INTEGER, titre TEXT, enonce TEXT, objectifs TEXT, difficulte TEXT, solution TEXT, erreurs TEXT, categorie TEXT, created_at TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS flashcards(id INTEGER PRIMARY KEY AUTOINCREMENT, matiere_id INTEGER, chapitre_id INTEGER, question TEXT, reponse TEXT, statut TEXT DEFAULT 'À revoir', next_review TEXT, created_at TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS planning(id INTEGER PRIMARY KEY AUTOINCREMENT, matiere_id INTEGER, chapitre_id INTEGER, titre TEXT, date TEXT, duree INTEGER, priorite TEXT, statut TEXT DEFAULT 'Prévu', created_at TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS activites(id INTEGER PRIMARY KEY AUTOINCREMENT, type TEXT, description TEXT, matiere_id INTEGER, duree INTEGER DEFAULT 0, created_at TEXT)")
    conn.commit()
    cur.execute("SELECT COUNT(*) as c FROM matieres"); row=cur.fetchone()
    if row["c"]==0:
        from config import MATIERES_EXEMPLE
        now=datetime.now().isoformat()
        for m in MATIERES_EXEMPLE:
            cur.execute("INSERT OR IGNORE INTO matieres(nom,description,semestre,difficulte,objectif,statut,created_at) VALUES(?,?,?,?,?,?,?)",(m["nom"],m["description"],m["semestre"],m["difficulte"],m["objectif"],"Non commencé",now))
        conn.commit()
    conn.close()
def fetch_all(q,p=()):
    try:
        conn=get_connection(); cur=conn.cursor(); cur.execute(q,p); rows=cur.fetchall(); conn.close(); return [dict(r) for r in rows]
    except Exception as e:
        print("fetch_all",e); return []
def fetch_one(q,p=()):
    try:
        conn=get_connection(); cur=conn.cursor(); cur.execute(q,p); r=cur.fetchone(); conn.close(); return dict(r) if r else None
    except: return None
def execute(q,p=()):
    conn=get_connection(); cur=conn.cursor(); cur.execute(q,p); conn.commit(); last=cur.lastrowid; conn.close(); return last
def get_storage_info():
    exists=os.path.exists(DB_PATH); size=os.path.getsize(DB_PATH) if exists else 0
    return {"size_kb":round(size/1024,1),"mode":"SQLite local"}
