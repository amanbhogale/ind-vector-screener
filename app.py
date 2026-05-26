from flask import Flask, request, jsonify, send_from_directory
import os
import json
from dcf_engine import DCFEngine

app = Flask(__name__, static_folder='.')

dcf_engine = DCFEngine()

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('.', path)

@app.route('/api/calculate', methods=['POST'])
def calculate_dcf():
    try:
        data = request.json
        ticker = data.get('ticker')
        if not ticker:
            return jsonify({'error': 'Ticker is required'}), 400
            
        # The frontend will pass the stock_data directly to avoid re-fetching in the backend for now,
        # or we could fetch it from our global JSON structure if we preferred. 
        # But letting the frontend pass the pre-loaded data is faster.
        stock_data = data.get('stock_data', {})
        user_params = data.get('params', {})
        
        # Calculate
        results = dcf_engine.calculate_dcf(stock_data, user_params, ticker=ticker)
        
        return jsonify(results)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting Market Analysis Server...")
    print("Serving on http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
