from flask import Flask, jsonify, request, send_from_directory, render_template
import json, os, time

app = Flask(__name__)

CONFIG_PATH = '/data/config.json'

DEFAULT_CONFIG = {
    "child_name": "LittleNugget",
    "daily": {
        "reward": "🍦 Ice Cream!",
        "chores": [
            {"emoji": "🛏️", "name": "Make bed"},
            {"emoji": "🦷", "name": "Brush teeth"},
            {"emoji": "🧺", "name": "Tidy toys"},
            {"emoji": "🍽️", "name": "Clear dishes"},
            {"emoji": "🐾", "name": "Feed pet"},
            {"emoji": "👗", "name": "Get dressed"}
        ]
    },
    "weekly": {
        "reward": "🎬 Movie Night!",
        "chores": [
            {"emoji": "🧹", "name": "Vacuum room"},
            {"emoji": "🪟", "name": "Wipe surfaces"},
            {"emoji": "🗑️", "name": "Empty bins"},
            {"emoji": "🧴", "name": "Tidy bathroom"},
            {"emoji": "👟", "name": "Sort shoes"},
            {"emoji": "📚", "name": "Tidy bookshelf"}
        ]
    }
}

def read_config():
    if not os.path.exists(CONFIG_PATH):
        write_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG
    with open(CONFIG_PATH, 'r') as f:
        return json.load(f)

def write_config(data):
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

@app.route('/')
def index():
    response = app.make_response(render_template('chart.html', ts=int(time.time())))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/api/config', methods=['GET'])
def get_config():
    return jsonify(read_config())

@app.route('/api/config', methods=['POST'])
def set_config():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'no data'}), 400
    write_config(data)
    return jsonify({'ok': True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8090, debug=False)
