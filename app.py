from flask import Flask, render_template, request, jsonify, make_response
from decimal import Decimal
from datetime import datetime

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
    # Pass the current date/time to the template
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

    if choice in ('DV', 'AP', 'ML', 'DV Injection'):
        result = add(num1, num2)
        message = f"{choice}: {round(result, 2)}"
    elif choice == 'SKULL Leveling':
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
    # Retrieve form fields
    mouse_id = data.get("mouse_id", "unknown")
    mouse_weight = data.get("mouse_weight", "")
    surgeon = data.get("surgeon", "")
    target_area = data.get("target_area", "")
    calculations = data.get("calculations", "")
    notes = data.get("notes", "")
    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    content = (
        f"Date: {current_datetime}\n"
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

@app.route('/health')
def health_check():
    return "OK", 200

if __name__ == '__main__':
    app.run(debug=True)
