# CSV to Google Sheets Uploader

This project contains a Python script that reads a large CSV file, applies specific filters, cleans the data, and uploads the results to a Google Sheet in batches. It also updates a separate "test" sheet with a "Last Run" timestamp.

## Features

-   **Streaming:** Reads the CSV in chunks to handle large files without high memory usage.
-   **Filtering:** Applies specific logic to filter rows based on `lager`, `category`, and `sortkriterium` columns.
-   **Data Cleaning:** Trims whitespace, selects specific columns (A-V), and enforces data types (numeric vs. string).
-   **Batch Uploads:** Appends data to Google Sheets in batches to work efficiently and avoid API rate limits.
-   **Secure Configuration:** Uses a `.env` file to manage secret keys and configuration, which are kept out of version control via `.gitignore`.

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd <your-repo-name>
```

### 2. Create a Virtual Environment

It's highly recommended to use a virtual environment to manage dependencies.

```bash
# On macOS/Linux
python3 -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
.\venv\Scripts\activate
```

### 3. Install Dependencies

Install the required Python packages.

```bash
pip install -r requirements.txt
```

### 4. Google Service Account Setup

This script requires a Google Cloud Service Account to interact with Google Sheets.

1.  Follow the [Google Cloud documentation](https://cloud.google.com/iam/docs/service-accounts-create) to create a service account.
2.  Enable the **Google Sheets API** for your project.
3.  Download the service account's JSON key file.
4.  **Share your Google Sheet** with the service account's email address (e.g., `your-service-account@...gserviceaccount.com`) and give it **Editor** permissions.
5.  Save the downloaded JSON file somewhere safe on your computer.

### 5. Configure Environment Variables

1.  Make a copy of the example environment file and name it `.env`:
    ```bash
    # On macOS/Linux
    cp .env.example .env

    # On Windows (Command Prompt)
    copy .env.example .env
    ```

2.  Open the new `.env` file in a text editor and fill in your values.

    ```ini
    # Path to your Google Service Account JSON file (from step 4)
    SERVICE_ACCOUNT_FILE="C:/Users/YourUser/secrets/my-service-account.json"

    # Your Google Sheet ID (from the URL)
    # e.g., [https://docs.google.com/spreadsheets/d/THIS_IS_THE_ID/edit](https://docs.google.com/spreadsheets/d/THIS_IS_THE_ID/edit)
    SPREADSHEET_ID="12345abcdeFGHIJKLMnopqRSTUvwxyz"

    # Path to your input CSV file
    CSV_INPUT_PATH="C:/Users/YourUser/Downloads/input_data.csv"
    ```

---

## How to Run

Once you have activated your virtual environment (step 2) and configured your `.env` file (step 5), simply run the `main.py` script:

```bash
python main.py
```

The script will print its progress to the console.
