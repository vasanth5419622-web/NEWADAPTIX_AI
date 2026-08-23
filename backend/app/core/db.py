import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from app.core.config import settings, DATA_DIR

DB_PATH = DATA_DIR / "adaptix_farm.db"

def init_db():
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    # Analyses Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS analyses (
        request_id TEXT PRIMARY KEY,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        crop TEXT,
        user_query TEXT,
        image_path TEXT,
        status TEXT,
        possible_condition TEXT,
        confidence_level TEXT,
        confidence_score REAL,
        verification_status TEXT,
        total_latency_ms REAL,
        total_estimated_cost REAL,
        recommendation TEXT,
        full_state_json TEXT
    )
    """)
    
    # Documents Table for RAG
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS documents (
        doc_id TEXT PRIMARY KEY,
        filename TEXT,
        title TEXT,
        crop TEXT,
        category TEXT,
        page_count INTEGER,
        uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        file_path TEXT,
        chunk_count INTEGER
    )
    """)
    
    # Document Chunks Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS document_chunks (
        chunk_id TEXT PRIMARY KEY,
        doc_id TEXT,
        page_number INTEGER,
        crop TEXT,
        disease TEXT,
        growth_stage TEXT,
        content TEXT,
        source TEXT,
        FOREIGN KEY(doc_id) REFERENCES documents(doc_id)
    )
    """)
    
    conn.commit()
    conn.close()

def save_analysis(state: Dict[str, Any]):
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    req_id = state.get("request_id", "")
    crop = state.get("context", {}).get("crop", "")
    user_query = state.get("user_input", {}).get("text", "")
    image_path = state.get("image_metadata", {}).get("file_path", "")
    status = state.get("status", "completed")
    
    final_res = state.get("final_result", {})
    possible_cond = final_res.get("possible_condition", "")
    rec = final_res.get("recommendation", "")
    
    conf = state.get("confidence", {})
    conf_level = conf.get("level", "Moderate")
    conf_score = conf.get("score", 0.0)
    
    verif = state.get("verification_results", {})
    verif_status = "Verified" if verif.get("verified") else "Requires Review"
    
    total_lat = state.get("total_latency_ms", 0.0)
    total_cost = state.get("total_estimated_cost", 0.0)
    full_json = json.dumps(state)
    
    cursor.execute("""
    INSERT OR REPLACE INTO analyses (
        request_id, crop, user_query, image_path, status,
        possible_condition, confidence_level, confidence_score,
        verification_status, total_latency_ms, total_estimated_cost,
        recommendation, full_state_json
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        req_id, crop, user_query, image_path, status,
        possible_cond, conf_level, conf_score,
        verif_status, total_lat, total_cost,
        rec, full_json
    ))
    
    conn.commit()
    conn.close()

def get_analysis_by_id(request_id: str) -> Optional[Dict[str, Any]]:
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute("SELECT full_state_json FROM analyses WHERE request_id = ?", (request_id,))
    row = cursor.fetchone()
    conn.close()
    if row and row[0]:
        return json.loads(row[0])
    return None

def get_all_analyses(limit: int = 50) -> List[Dict[str, Any]]:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
    SELECT request_id, created_at, crop, user_query, possible_condition,
           confidence_level, confidence_score, verification_status,
           total_latency_ms, total_estimated_cost
    FROM analyses
    ORDER BY created_at DESC LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

# Initialize database schema immediately upon module import
init_db()
