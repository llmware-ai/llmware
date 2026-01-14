import subprocess
import re
import webbrowser
from flask import Flask, render_template

app = Flask(__name__)

# Route to display the buttons
@app.route('/')
def index():
    return render_template('index.html')

# Route for About Us page (about_us.html)
@app.route('/about_us')
def about_us():
    return render_template('about_us.html')

# Route for Scan AI page (scan_ai.html)
@app.route('/scan_ai')
def scan_ai():
    return render_template('scan_ai.html')

# Route for Invoice Decoder page (invoice_decoder.html)
@app.route('/invoice_decoder')
def invoice_decoder():
    return render_template('invoice_decoder.html')

# Route for Consultation Analysis page (consultation_analysis.html)
@app.route('/consultation_analysis')
def consultation_analysis():
    return render_template('consultation_analysis.html')

# Route to run scanAi.py with Streamlit
@app.route('/run_button1', methods=['POST'])
def run_button1():
    try:
        # Run the scanAi.py Streamlit app in the background
        subprocess.Popen(['streamlit', 'run', 'scanAi.py'])
    except Exception as e:
        print(f"Error running scanAi.py with Streamlit: {str(e)}")
    # Stay on the index page without any message
    return render_template('index.html')

# Route to run invoiceDecoder.py with Streamlit
@app.route('/run_button2', methods=['POST'])
def run_button2():
    try:
        # Run the invoiceDecoder.py Streamlit app in the background
        subprocess.Popen(['streamlit', 'run', 'invoiceDecoder.py'])
    except Exception as e:
        print(f"Error running invoiceDecoder.py with Streamlit: {str(e)}")
    # Stay on the index page without any message
    return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True)
