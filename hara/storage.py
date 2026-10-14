import json, os, sqlite3
from pathlib import Path
from datetime import datetime, timezone
DB_PATH=Path(os.getenv("HARA_DB_PATH","data/hara.db"))
def _conn():
    DB_PATH.parent.mkdir(parents=True,exist_ok=True)
    c=sqlite3.connect(DB_PATH); c.row_factory=sqlite3.Row; return c
def init_db():
    with _conn() as c:
        c.execute("CREATE TABLE IF NOT EXISTS records (hazard_id TEXT PRIMARY KEY, data TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL, review_status TEXT NOT NULL, reviewer TEXT NOT NULL DEFAULT '')")
        c.execute("CREATE TABLE IF NOT EXISTS audit (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT NOT NULL, event_type TEXT NOT NULL, payload TEXT NOT NULL)")
def save_hara(record):
    now=datetime.now(timezone.utc).isoformat(); d=dict(record); d.setdefault("created_at",now); d["updated_at"]=now; d.setdefault("review_status","Pending")
    with _conn() as c:
        c.execute("INSERT INTO records VALUES(?,?,?,?,?,?) ON CONFLICT(hazard_id) DO UPDATE SET data=excluded.data,updated_at=excluded.updated_at,review_status=excluded.review_status",
                  (d["hazard_id"],json.dumps(d),d["created_at"],now,d["review_status"],d.get("reviewer","")))
def list_hara():
    with _conn() as c: rows=c.execute("SELECT * FROM records ORDER BY created_at").fetchall()
    out=[]
    for row in rows:
        d=json.loads(row["data"]); d.update(created_at=row["created_at"],updated_at=row["updated_at"],review_status=row["review_status"],reviewer=row["reviewer"]); out.append(d)
    return out
def set_review_status(hid,status,reviewer=""):
    with _conn() as c:
        row=c.execute("SELECT data FROM records WHERE hazard_id=?",(hid,)).fetchone()
        if not row: raise KeyError(hid)
        d=json.loads(row["data"]); d.update(review_status=status,reviewer=reviewer,updated_at=datetime.now(timezone.utc).isoformat())
        c.execute("UPDATE records SET data=?,updated_at=?,review_status=?,reviewer=? WHERE hazard_id=?",(json.dumps(d),d["updated_at"],status,reviewer,hid))
def audit(event_type,payload):
    with _conn() as c: c.execute("INSERT INTO audit(timestamp,event_type,payload) VALUES(?,?,?)",(datetime.now(timezone.utc).isoformat(),event_type,json.dumps(payload)))
