# Compare Excel Files Flask Application

## Overview

This project is a Flask-based web application that compares two uploaded Excel files based on a common 'SKU' column, sorts the data, merges the dataframes, and saves the comparison results to a new Excel file. The application is containerized using Docker and orchestrated with Docker Compose.

## Project Structure

- **main.py**: The main Flask application script.
- **requirements.txt**: A list of Python dependencies needed for the application.
- **compare-excel-files.dockerfile**: The Dockerfile to build the Docker image for the Flask application.
- **docker-compose.yml**: Docker Compose file to manage the Docker container.

## Requirements

- Docker
- Docker Compose

## Setup Instructions

1. **Clone the repository**:
    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

2. **Build and run the application**:
    ```bash
    docker-compose up --build
    ```

3. **Access the application**:
    The application will be accessible at `http://localhost:5000`.

## API Endpoints

### Compare Excel Files

- **URL**: `/compare`
- **Method**: `POST`
- **Description**: Compares two Excel files based on the 'SKU' column.
- **Parameters**:
  - `file1`: The first Excel file (uploaded via form-data).
  - `file2`: The second Excel file (uploaded via form-data).
- **Response**:
  - `200 OK`: JSON message indicating the location of the saved comparison file.
  - `400 Bad Request`: JSON error message if the required files are not provided or if the files do not contain an 'SKU' column.
  - `500 Internal Server Error`: JSON error message if an error occurs during processing.

## Dockerize the application

1. **compare-excel-files.dockerfile**

```dockerfile
FROM python:3.10
ENV APP /app
RUN mkdir $APP
WORKDIR $APP
EXPOSE 5000

RUN mkdir ./log

RUN pip install --upgrade pip
ADD requirements.txt .
RUN python -m pip install -r requirements.txt

# Add a new user and group
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Change the ownership of the working directory
RUN chown -R appuser:appuser /app

# Switch to the new user
USER appuser

# Uncomment the lines below to add the application files and run the application
#COPY . .
#CMD ["python", "/app/main.py"]
```

2. **Create a `requirements.txt` file**:

    ```text
    Flask==3.0.3
    pandas==2.2.2
    openpyxl==3.1.5
    gunicorn==22.0.0
    numpy==2.0.1
    ```

3. **Create a `docker-compose.yml` file**:

    ```yaml
    version: '3.4'
    services:
      flask-app:
        image: compare-excel-files:latest
        restart: always
        build:
          context: .
          dockerfile: compare-excel-files.dockerfile
        command: gunicorn --log-level debug --workers=2 --threads=2 -b 0.0.0.0:5000 --worker-class="gthread" --timeout 600 main:app
        ports:
          - 5000:5000
        volumes:
          - ./:/app
    ```

4. **Create a `main.py` file**:

    ```python
    from flask import Flask, request, jsonify
    import pandas as pd
    from datetime import datetime
    import os

    app = Flask(__name__)

    @app.route('/compare', methods=['POST'])
    def compare_excel():
        if 'file1' not in request.files or 'file2' not in request.files:
            return jsonify({'error': 'No files provided'}), 400

        file1 = request.files['file1']
        file2 = request.files['file2']

        try:
            # Read the Excel files into dataframes
            df1 = pd.read_excel(file1, engine='openpyxl')
            df2 = pd.read_excel(file2, engine='openpyxl')

            # Ensure both dataframes have a column named 'SKU'
            if 'SKU' not in df1.columns or 'SKU' not in df2.columns:
                return jsonify({'error': 'Both files must contain an "SKU" column'}), 400

            # Sort dataframes by 'SKU' column
            df1 = df1.sort_values(by='SKU').reset_index(drop=True)
            df2 = df2.sort_values(by='SKU').reset_index(drop=True)

            # Merge the two dataframes on 'SKU'
            merged_df = pd.merge(df1, df2, on='SKU', suffixes=('_file1', '_file2'), how='outer')

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
    ```

## Running the Application

1. **Build and start the application using Docker Compose**:

    ```bash
    docker-compose up --build
    ```

2. **Access the application**:
    - The application will be available at `http://localhost:5000`.
    
3. **Compare Excel files**:
    - Use a tool like Postman or `curl` to send a POST request to `http://localhost:5000/compare` with two Excel files.

    ```bash
    curl -X POST -F "file1=@path/to/first/file.xlsx" -F "file2=@path/to/second/file.xlsx" http://localhost:5000/compare
    ```

    - The response will indicate where the comparison file is saved.

## Notes

- Ensure that the `output_files` directory exists and has the necessary permissions for the application to save files.
- The application uses Gunicorn as the WSGI HTTP Server to handle multiple requests efficiently.

## License

This project is licensed under the MIT License.

