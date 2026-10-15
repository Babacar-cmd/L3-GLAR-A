
from datetime import datetime, timedelta
import json
def extract_text_from_pdf(file_bytes):
    try:
        import fitz
        doc=fitz.open(stream=file_bytes, filetype="pdf")
        text=""
        for page in doc: text+=page.get_text()+"\n"
        pages=doc.page_count; doc.close()
        if len(text.strip())<50: return {"success":False,"text":"","warning":"PDF scanné ou image - colle le texte manuellement dans le champ prévu"}
        return {"success":True,"text":text,"pages":pages}
    except ImportError: return {"success":False,"text":"","warning":"PyMuPDF non installé"}
    except Exception as e: return {"success":False,"text":"","warning":f"Erreur PDF: {e}"}
def extract_text_from_txt(file_bytes):
    for enc in ["utf-8","latin-1","cp1252"]:
        try: return {"success":True,"text":file_bytes.decode(enc)}
        except: continue
    return {"success":False,"text":"","warning":"Encodage non reconnu"}
def generate_fiche_auto(contenu,titre="Fiche"):
    lines=[l.strip() for l in contenu.split("\n") if l.strip()]
    notions="\n".join([f"- {l[:120]}" for l in lines[:8]]) or "- À synthétiser"
    defs="\n".join([f"- {l}" for l in lines[:3]]) or "- Définition 1"
    points="\n".join([f"• {l[:100]}" for l in lines[2:10]]) or "• Point clé 1"
    return {"notions":notions,"definitions":defs,"points_cles":points,"formules":"À compléter","exemples":"Voir cours original","erreurs":"Ne pas confondre","resume":"\n".join(lines[:5])[:500]}
def calculate_quiz_score(answers,questions):
    correct=0; total=len(questions); details=[]
    for q in questions:
        exp=json.loads(q["reponses_correctes"]) if isinstance(q["reponses_correctes"],str) else q["reponses_correctes"]
        given=answers.get(q["id"],[])
        ok=set(map(str,given))==set(map(str,exp))
        if ok: correct+=1
        details.append({"qid":q["id"],"ok":ok,"expected":exp,"given":given})
    pct=(correct/total*100) if total else 0
    return {"correct":correct,"total":total,"pct":pct,"score20":round(correct/total*20,2) if total else 0,"details":details}
def spaced_next_review(statut):
    now=datetime.now()
    if statut=="Maîtrisé": return (now+timedelta(days=7)).isoformat()
    if statut=="En cours d'acquisition": return (now+timedelta(days=2)).isoformat()
    return (now+timedelta(days=1)).isoformat()
