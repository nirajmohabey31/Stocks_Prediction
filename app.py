import os
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Create directories if they do not exist
directories = ['Stocks/forecasts', 'Stocks/visualizations', 'Stocks/analysis']
for directory in directories:
    if not os.path.exists(directory):
        os.makedirs(directory)

@app.route('/')
def index():
    # List available stock symbols from visualizations folder
    stock_symbols = [f.split('_')[1] for f in os.listdir('Stocks/visualizations') if f.endswith('.html')]
    return render_template('index.html', stocks=stock_symbols)

@app.route('/results', methods=['POST'])
def results():
    data = request.json
    stock_symbol = data['stock_symbol']

    # Assuming you generate the visualization HTML file with this naming convention
    visualization_file = f'C:/Users/niraj/CS539 ML PROJECT/Stocks/visualizations/visualization_{stock_symbol}.html'
    forecast_file = f'C:/Users/niraj/CS539 ML PROJECT/Stocks/forecasts/forecast_{stock_symbol}.csv'  # or whatever your naming convention is
    analysis_file = f'C:/Users/niraj/CS539 ML PROJECT/Stocks/analysis/analysis_{stock_symbol}.txt'  # or whatever your naming convention is

    # Return paths to the files
    return jsonify({
        'visualization': visualization_file,
        'forecast': forecast_file,
        'analysis': analysis_file
    })

if __name__ == '__main__':
    app.run(debug=True)
