from flask import Flask, render_template, request, jsonify, make_response
from decimal import Decimal
from datetime import datetime
import re

app = Flask(__name__)

# Basic arithmetic functions
def add(x, y):
    return x + y

def subtract(x, y):
    return x - y

def is_skull_level(num1, num2):
    num1_decimal = Decimal(str(num1))
    num2_decimal = Decimal(str(num2))
    return abs(subtract(num1_decimal, num2_decimal)) <= Decimal("0.2")

@app.route('/')
def home():
    current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return render_template('index.html', current_datetime=current_datetime)

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.get_json()
    choice = data.get('choice')
    try:
        num1 = float(data.get('num1'))
        num2 = float(data.get('num2'))
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid input numbers"}), 400

    if choice in ('AP', 'ML', 'DV INJECTION', 'DV FIBER'):
        result = add(num1, num2)
        message = f"{choice}: {round(result, 2)}"
    elif choice == 'SKULL LEVELING':
        if is_skull_level(num1, num2):
            message = "The Skull is level, proceed to the next step"
        elif num1 > num2:
            message = "Nope! LOWER the skull and retry!"
        elif num1 < num2:
            message = "Nope! RAISE the skull and retry!"
        else:
            message = "Unexpected condition"
    else:
        message = "Unknown measurement type"
    
    return jsonify({"message": message})

@app.route('/save', methods=['POST'])
def save():
    data = request.get_json()
    mouse_id = data.get("mouse_id", "unknown")
    mouse_weight = data.get("mouse_weight", "")
    surgeon = data.get("surgeon", "")
    target_area = data.get("target_area", "")
    calculations = data.get("calculations", "")
    notes = data.get("notes", "")
    local_time = data.get("local_time")
    if not local_time:
        local_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    content = (
        f"Date: {local_time}\n"
        f"Mouse ID: {mouse_id}\n"
        f"Mouse Bodyweight (g): {mouse_weight}\n"
        f"Surgeon: {surgeon}\n"
        f"Target area: {target_area}\n\n"
        f"Measurements:\n{calculations}\n\n"
        f"Notes:\n{notes}\n"
    )
    
    filename = f"{mouse_id}_measurements.txt"
    response = make_response(content)
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    response.headers["Content-Type"] = "text/plain"
    return response

@app.route('/update_notes', methods=['POST'])
def update_notes():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    if not file.filename.endswith('.txt'):
        return jsonify({"error": "Only text files are allowed"}), 400

    new_notes = request.form.get('new_notes', '')
    if not new_notes:
        return jsonify({"error": "No new notes provided"}), 400
    
    try:
        original_content = file.read().decode('utf-8')
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        updated_content = (
            original_content +
            f"\n\nAdditional Notes ({timestamp}):\n{new_notes}\n"
        )
        
        # Generate a new filename with an incrementing number.
        base_filename = file.filename.rsplit('.', 1)[0]
        match = re.search(r'_(\d+)$', base_filename)
        if match:
            version = int(match.group(1))
            base_name = base_filename[:match.start()]
            new_version = version + 1
        else:
            base_name = base_filename
            new_version = 1
        filename = f"{base_name}_{new_version}.txt"

        response = make_response(updated_content)
        response.headers["Content-Disposition"] = f"attachment; filename={filename}"
        response.headers["Content-Type"] = "text/plain"
        return response
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health')
def health_check():
    return "OK", 200

if __name__ == '__main__':
    app.run(debug=True)
