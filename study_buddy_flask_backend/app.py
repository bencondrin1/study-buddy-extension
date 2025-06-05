from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)

# Allow only your Chrome extension to access it (recommended)
CORS(app, origins=["chrome-extension://ehmbcgoamlbnggoeapgglllpahhlhbha"])

@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    print("Received from extension:", data)

    # Dummy response
    return jsonify({"message": "Received PDF URLs and options successfully!"})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5050, debug=True)
