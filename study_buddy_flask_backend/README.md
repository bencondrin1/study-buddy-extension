# Study Buddy Flask Backend

This is a simple local Flask API for testing.

## Setup

1. Create a virtual environment (optional but recommended):

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the server:

```bash
python app.py
```

4. It will be available at http://localhost:5000

## Endpoint

- `POST /generate`
  - Request JSON:
    ```json
    {
      "text": "Your note text",
      "depth": "Basic",
      "studyType": "Flash Cards"
    }
    ```
  - Response JSON:
    ```json
    {
      "status": "success",
      "result": "Generated Flash Cards at Basic level..."
    }
    ```
