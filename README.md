# Ind Vector Screener

This project is a web-based financial analysis tool, including a DCF (Discounted Cash Flow) engine and market data visualizations.

## Prerequisites
- Python 3.x
- pip (Python package installer)

## Setup

1. **Clone or navigate to the repository:**
   ```bash
   cd ind-vector-screener
   ```

2. **Install dependencies:**
   It is recommended to use a virtual environment.
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

To start the server, run:
```bash
python app.py
```
This will launch a Flask application on `http://127.0.0.1:5000`. 
Open your web browser and navigate to this URL to access the application.

## Other Scripts
- `data_market_visualization.py`: Generates static/interactive market visualization outputs.
- `dcf_engine.py`: The backend engine for discounted cash flow calculations.
- `plot_ind.py`: Additional plotting utility.
- `test_bubble.py`: Bubble chart testing script.
