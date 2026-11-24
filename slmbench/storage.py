"""SQLite persistence for model registry, run metadata and individual trials."""
from __future__ import annotations
import sqlite3, json
from pathlib import Path
import pandas as pd

DEFAULT_MODELS=[("Demo Reference","Synthetic","N/A","N/A","N/A","Built-in deterministic demo")]
def connect(db_path="data/slmbench.db"):
    path=Path(db_path); path.parent.mkdir(parents=True,exist_ok=True); return sqlite3.connect(path)
def initialize(db_path="data/slmbench.db"):
    with connect(db_path) as c:
        c.executescript("""CREATE TABLE IF NOT EXISTS models(id INTEGER PRIMARY KEY, name TEXT UNIQUE, family TEXT, parameter_size TEXT, model_format TEXT, quantization TEXT, source TEXT);
        CREATE TABLE IF NOT EXISTS runs(id INTEGER PRIMARY KEY, created_at TEXT, model TEXT, runtime TEXT, mode TEXT, device_json TEXT, config_json TEXT, execution_mode TEXT, prompt_id TEXT, category TEXT, prompt TEXT, expected TEXT, answer TEXT, ttft_s REAL, latency_s REAL, generated_tokens INTEGER, tokens_per_second REAL, process_memory_mb REAL, quality_pass INTEGER, error TEXT);""")
        for row in DEFAULT_MODELS: c.execute("INSERT OR IGNORE INTO models(name,family,parameter_size,model_format,quantization,source) VALUES(?,?,?,?,?,?)",row)
def models(db_path="data/slmbench.db"):
    with connect(db_path) as c: return pd.read_sql_query("SELECT * FROM models ORDER BY name",c)
def add_model(values,db_path="data/slmbench.db"):
    with connect(db_path) as c: c.execute("INSERT INTO models(name,family,parameter_size,model_format,quantization,source) VALUES(?,?,?,?,?,?)",tuple(values))
def save_run(row,db_path="data/slmbench.db"):
    keys=list(row.keys())
    with connect(db_path) as c: c.execute(f"INSERT INTO runs({','.join(keys)}) VALUES({','.join('?' for _ in keys)})",[json.dumps(row[k]) if k in ('device_json','config_json') and not isinstance(row[k],str) else row[k] for k in keys])
def runs(db_path="data/slmbench.db"):
    with connect(db_path) as c: return pd.read_sql_query("SELECT * FROM runs ORDER BY id DESC",c)
