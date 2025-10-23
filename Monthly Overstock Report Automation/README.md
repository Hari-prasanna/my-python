CSV to Google Sheets - Monthly Batch Uploader

This project contains a Python script that reads a CSV file, performs data cleaning and transformation, and then uploads the data to a Google Sheet.

It splits the data into two main batches ("ZFS" and "BBeauty"), groups them by month (mm.yyyy), and uploads each month's data to a separate worksheet (e.g., ZFS01.2024, BBeauty01.2024).

Features

Secure Configuration: Uses a .env file to manage secret keys and API credentials, keeping them out of version control.

Robust Data Loading: Handles specific CSV encodings (cp1252) and cleans column headers (e.g., removes newlines).

Data Transformation: Parses dates, strips whitespace, and creates a month_key for batching.

Dynamic Worksheets: Automatically creates new worksheets for each month if they don't already exist.

Modular Code: Separates Google Sheets logic from data processing logic for easier maintenance.

Setup Instructions

1. Clone the Repository

git clone <your-repo-url>
cd <your-project-name>


2. Create a Virtual Environment

It's highly recommended to use a virtual environment to manage dependencies.

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
.\venv\Scripts\activate


3. Install Dependencies

Install the required Python packages using the requirements.txt file.

pip install -r requirements.txt


4. Google Service Account Setup

This script requires a Google Cloud Service Account to interact with Google Sheets.

Follow the Google Cloud documentation to create a service account.

Enable the Google Sheets API and Google Drive API for your project.

Download the service account's JSON key file.

Important: Open your Google Sheet and share it with the service account's email address (e.g., your-service-account@...gserviceaccount.com). Give it Editor permissions.

Save the downloaded JSON file somewhere safe on your computer.

5. Configure Environment Variables

In the project folder, make a copy of the example environment file and name it .env:

# On macOS/Linux
cp .env.example .env

# On Windows (Command Prompt)
copy .env.example .env


Open the new .env file in a text editor and fill in your values.

# Path to your Google Service Account JSON file (from step 4)
SERVICE_ACCOUNT_FILE="C:/Users/YourUser/secrets/my-service-account.json"

# Your Google Sheet ID (from the URL)
# e.g., [https://docs.google.com/spreadsheets/d/THIS_IS_THE_ID/edit](https://docs.google.com/spreadsheets/d/THIS_IS_THE_ID/edit)
GOOGLE_SHEET_ID="12345abcdeFGHIJKLMnopqRSTUvwxyz"

# Path to your input CSV file
CSV_INPUT_PATH="C:/Users/YourUser/Downloads/input_data.csv"


How to Run

Once your virtual environment is activated and your .env file is configured, run the main.py script:

python main.py


The script will print its progress to the console, indicating when it's connecting, cleaning data, and uploading batches.
