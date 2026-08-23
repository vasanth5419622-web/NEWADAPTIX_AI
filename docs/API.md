# ADAPTIX-FARM — REST API Specification

Base URL: `http://127.0.0.1:8000/api`

---

## Endpoints

### 1. `POST /api/analyze`
Executes complete multimodal crop pathology pipeline with image upload and field context.
* **Content-Type:** `multipart/form-data`
* **Form Parameters:**
  - `image` (File, Optional): Crop photograph (JPG/PNG/WEBP)
  - `crop` (String, Optional): Stated crop name
  - `growth_stage` (String, Optional): e.g. "Vegetative", "Flowering"
  - `season` (String, Optional): e.g. "Kharif", "Rabi"
  - `location` (String, Optional): e.g. "Coimbatore, Tamil Nadu"
  - `notes` (String, Optional): Field observations
  - `user_query` (String, Optional): Natural language question
  - `language` (String, Default: "en"): "en" or "ta"
* **Response:** JSON `ExecutionState` object containing `request_id`, `route_trace`, `final_result`, `confidence`, `evidence_fusion`, etc.

### 2. `POST /api/analyze/text`
Executes text/voice-only query pipeline for unseen or general agronomic inquiries.
* **Content-Type:** `application/json`
* **Body:**
  ```json
  {
    "text": "My chilli plant leaves are curling with pale patches",
    "crop": "Chilli",
    "growth_stage": "Vegetative",
    "language": "en"
  }
  ```

### 3. `POST /api/documents/upload`
Uploads and indexes an agricultural extension advisory PDF or text document into the vector store.
* **Content-Type:** `multipart/form-data`
* **Form Parameters:**
  - `file` (File, Required): PDF or TXT advisory bulletin
  - `crop` (String, Default: "General"): Target crop
  - `title` (String, Optional): Title of advisory bulletin
* **Response:**
  ```json
  {
    "doc_id": "DOC-7a8b9c",
    "chunks_indexed": 4,
    "message": "Successfully extracted and indexed 4 semantic advisory chunks."
  }
  ```

### 4. `GET /api/documents/list`
Lists all indexed advisory document chunks and metadata.

### 5. `POST /api/documents/query`
Direct semantic vector search against indexed bulletins.

### 6. `GET /api/analysis/{request_id}`
Retrieves historical analysis record and execution trace by ID.

### 7. `GET /api/history`
Returns list of previous analyses stored in SQLite database.

### 8. `GET /api/metrics`
Returns aggregate observability metrics (average latency, cumulative costs, model invocations).

### 9. `GET /api/health`
Health check endpoint reporting API status and indexed RAG chunk count.
