# 📚 Study Buddy Flask Backend

A local Flask API that powers a Chrome extension for generating study materials (Flashcards, Study Guides, Practice Exams, Diagrams) from Canvas-hosted PDFs.

---

## 🚀 Features

- Accepts one or more Canvas PDF URLs
- Extracts text or uses OCR fallback
- Calls OpenAI GPT to generate study materials
- Returns content in JSON format
- Generates visual diagrams using Mermaid.js
- Supports multiple diagram types: flowcharts, mind maps, sequence diagrams, and relationship diagrams

---

## 🛠️ Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/your-username/study-buddy-backend.git
cd study-buddy-backend
```

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 3. Install Mermaid CLI (for diagram generation)

The diagrams feature requires mermaid-cli to convert Mermaid diagrams to SVG images.

**On macOS:**
```bash
npm install -g @mermaid-js/mermaid-cli
```

**On Windows:**
```bash
npm install -g @mermaid-js/mermaid-cli
```

**On Linux:**
```bash
npm install -g @mermaid-js/mermaid-cli
```

**Note:** You need Node.js installed to use npm. Download it from [nodejs.org](https://nodejs.org/).
