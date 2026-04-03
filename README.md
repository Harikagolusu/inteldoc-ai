<div align="center">
  <img src="https://img.shields.io/badge/IntelDoc_AI-4f46e5?style=for-the-badge&logo=microchip&logoColor=white" />
  <h1>IntelDoc AI</h1>
  <p><strong>Next-Generation Document Insights via Contextual AI</strong></p>

  <p>
    <img src="https://img.shields.io/badge/Python-3.9+-blue.svg" alt="Python 3.9+" />
    <img src="https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi" alt="FastAPI" />
    <img src="https://img.shields.io/badge/Google_Gemini-8E75B2?style=flat&logo=googlebard&logoColor=white" alt="Gemini" />
  </p>
</div>

<br />

IntelDoc AI is an end-to-end intelligent document processing system built for modern hackathons. It seamlessly ingests PDFs, DOCX files, and Images, extracts robust internal text, and pushes it through an advanced AI logic system (Google Gemini 2.5 Flash) to generate comprehensive executive summaries, sentiment ratings, and categorized entity tags.

The application pairs a highly modular, asynchronous **FastAPI backend** with a stunning **dark-mode glassmorphism frontend dashboard**.

---

## ✨ Key Features
- **Universally Compatible Extraction**: Ingests `.pdf`, `.docx`, and `.jpg/.png` files. Utilizes Tesseract OCR for physical image text extraction.
- **Smart Document Categorization**: Google Gemini natively evaluates context to classify your document (e.g., _Invoice, Resume, Report, Meeting Notes_).
- **Executive Summaries & Sentiment**: Automatic reduction of wall-of-text documents into crisp 3-4 sentence AI summaries alongside psychological sentiment analysis (Positive/Neutral/Negative).
- **Deep Entities (NER)**: Runs native LLM processing to deeply perform Named Entity Recognition (Persons, Orgs, Dates, Money, Locations) over text constraints.
- **Sleek UX/UI**: Beautiful neon-glow backdrop filtered glass interfaces complete with dynamic load-step simulations that trace execution phases for judges/users.

---

## 🛠️ System Architecture

1. **Client (Vanilla JS or Automated Tester)**: The document is uploaded natively via heavily optimized `multipart/form-data` requests bounding the file blob cleanly without massive Base64 encodings.
2. **API Layer (FastAPI)**: Endpoint `/analyze` intercepts payloads and securely parses **dual-authentication** limits, accepting either `Authorization: Bearer <API_KEY>` or `x-api-key`.
3. **Extraction Layer**:
   - `pdfplumber` for structured PDF ingestion
   - `python-docx` for MS Office metadata & strings
   - `pytesseract` (Tesseract) for spatial OCR on images
4. **Text Cleaning**: Cleans text strings, bounds paragraphs, strips OCR noise, and enforces limits.
5. **Generative Processing (Gemini)**: Truncates data strictly to a 4,000-character ceiling to guarantee **sub-5-second execution times**, then bypasses blocking via asynchronous thread delegation to `gemini-2.5-flash` for summary, sentiment, and entity extraction.
6. **Delivery**: Returns a unified JSON Object merging ML and LLM findings instantly back to the dynamic dashboard.

---

## 💻 Tech Stack
* **Language & Framework Backend**: Python 3.9+, FastAPI, Uvicorn
* **AI Ecosystem**: `google-generativeai`
* **Document Parsing**: `pdfplumber`, `python-docx`, `pytesseract`, `Pillow`
* **Frontend Design**: HTML5, Vanilla JavaScript, CSS3 (Glassmorphism + Animations), FontAwesome 6 icons.
* **Deployment System**: Docker-ready setup with Alpine/Slim configuration.

---

## 🚀 Getting Started
### 1. Prerequisites
- Python 3.9+ installed on your machine.
- [**Tesseract OCR**](https://tesseract-ocr.github.io/tessdoc/Installation.html): 
  * Windows: Download the Executable Installer.
  * Mac: `brew install tesseract`
  * Linux: `sudo apt-get install tesseract-ocr`

### 2. Installation
Clone the repository, then map and install your standard Python environment:

```bash
git clone https://github.com/your-username/inteldoc-ai.git
cd inteldoc-ai

# Create and activate virtual environment (recommended)
python -m venv venv
# Windows: venv\Scripts\activate | Mac/Linux: source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Variables (.env)
At the root of the project, create a `.env` file (or rename `.env.example`).
Insert your Gemini API Key and your secure Hackathon API key lock:
```env
GEMINI_API_KEY=AIzaSy...your-gemini-key
API_KEY=sk_track2_987654321
```

### 4. Run the Application
Start the Uvicorn ASGI server natively:
```bash
uvicorn src.main:app --reload
```
Navigate to your browser at **`http://localhost:8000/`** to view the main Web App!

---

## 📡 API Endpoints 

### `POST /analyze`
Analyzes a natively uploaded document via Form Data and routes it through extraction, NER, and Gemini summarization. Strict bounds guarantee robust execution.

**Headers (Requires one of the following):**
* `Authorization`: `Bearer [Your secret backend API_KEY]`
* `x-api-key`: `[Your secret backend API_KEY]`
* *(Note: Do NOT set `Content-Type` manually; allow HTTP clients to auto-set `multipart/form-data` boundaries)*

**Request Body (`multipart/form-data`):**
* `file`: (Type: File blob) - The raw `.pdf`, `.docx`, or `.jpg` document.

**Response Schema (200 OK):**
```json
{
  "file_type": "pdf",
  "summary": "This document outlines the strategic implementation metrics for next quarter. The management discusses potential architectural pivots targeting new hardware deployments.",
  "entities": {
    "persons": ["John Doe", "Jane Smith"],
    "organizations": ["Intel Corporation"],
    "dates": ["Q3 2026", "October"],
    "money": ["$5.2 Million"],
    "locations": ["Santa Clara", "California"]
  },
  "sentiment": "positive"
}
```

> **Zero-Crash API Policy:** If an edge case disrupts deep analysis, the endpoint is guaranteed to return HTTP 200 with fallback empty arrays and an "Error processing document" summary flag so integrated automation tools do not break under 500 server alerts.

---

## ☁️ Render Deployment (Native Python)
IntelDoc AI has been meticulously hardened to run seamlessly natively on Render's free or paid Python environments without requiring Docker or any complex system dependencies!

**1. Create New Web Service on Render:**
Connect your GitHub repository and build natively. 

**2. Configure Render Settings:**
*   **Environment:** `Python 3`
*   **Build Command:** 
    ```bash
    pip install -r requirements.txt
    ```
*   **Start Command:** 
    ```bash
    uvicorn src.main:app --host 0.0.0.0 --port 10000
    ```

**3. Configure Environment Variables:**
Inside the Render dashboard for your service, inject the specific security definitions so as to avoid hard-coded logic:
*   `GEMINI_API_KEY`: `your_provided_google_gemini_key`
*   `API_KEY`: `sk_track2_987654321` (Your Hackathon Access token)

Your application will boot effortlessly into the Render cluster, remaining stable, highly parallelized, and completely tester-compliant!

---

*IntelDoc Intelligence | Designed & Built for Hackathon Excellence.*
