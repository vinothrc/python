from flask import Flask, request, jsonify
import pandas as pd
from datetime import datetime
import os

app = Flask(__name__)

@app.route('/compare', methods=['POST'])
def compare_excel():
    if 'input_file1' not in request.files or 'input_file2' not in request.files:
        return jsonify({'error': 'No files provided'}), 400

    input_file1 = request.files['input_file1']
    input_file2 = request.files['input_file2']

    try:
        # Read the Excel files into dataframes
        df1 = pd.read_excel(input_file1, engine='openpyxl')
        df2 = pd.read_excel(input_file2, engine='openpyxl')

        # Ensure both dataframes have a column named 'SKU'
        if 'SKU' not in df1.columns or 'SKU' not in df2.columns:
            return jsonify({'error': 'Both files must contain an "SKU" column'}), 400

        # Sort dataframes by 'SKU' column
        df1 = df1.sort_values(by='SKU').reset_index(drop=True)
        df2 = df2.sort_values(by='SKU').reset_index(drop=True)

        # Merge the two dataframes on 'SKU'
        merged_df = pd.merge(df1, df2, on='SKU', suffixes=('_input_file1', '_input_file2'), how='outer')

        # Save the comparison results to a new Excel file
        output_dir = './output_files'
        os.makedirs(output_dir, exist_ok=True)
        date_str = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        output_file = os.path.join(output_dir, f'comparison_{date_str}.xlsx')

        merged_df.to_excel(output_file, index=False)

        return jsonify({'message': f'Comparison file saved to {output_file}'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000)
