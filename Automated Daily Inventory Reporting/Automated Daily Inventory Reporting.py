# main.py
import os
import pandas as pd
import platform
from datetime import datetime
from dotenv import load_dotenv
import gutils  # Our Google Sheets utility module

# --- Load Configuration ---
load_dotenv()  # Load variables from .env file

# Load sensitive/environment-specific settings
SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
CSV_INPUT_PATH = os.getenv("CSV_INPUT_PATH")

# Basic validation
if not all([SERVICE_ACCOUNT_FILE, SPREADSHEET_ID, CSV_INPUT_PATH]):
    print("Error: Missing one or more required environment variables.")
    print("Please create a .env file (from .env.example) and fill in:")
    print("SERVICE_ACCOUNT_FILE, SPREADSHEET_ID, CSV_INPUT_PATH")
    exit(1)

# --- Application Constants ---
SHEET_NAME = "Bestandsabgleichfiltered"
TIMESTAMPSHEET = "test"
BATCH_ROWS = 2000

# Headers (we'll only use A..V = first 22)
HEADERS28 = [
    "MainLhm", "MainLhmdef", "Lager", "RegalStpl", "Ziel", "DistChannel", "SubLhm", "SubLhmdef",
    "Category", "Sortierziel ID", "SortKriterium", "sapcommoditygroupid", "Consumables",
    "Referenznummer", "Artikelnummer", "SKU", "BRANDCODE", "Qualität", "Source", "Anzahl",
    "Status", "Einlagerung", "Gewicht mainLhm", "Gewicht sublhm", "OVAPTypInfo", "Gemeldet",
    "SORTINGCRITERIAIDLHM", "SAPCOMMODITYGROUPIDLHM"
]
HEADERS_A_TO_V = HEADERS28[:22]  # first 22 headers for A..V

# Filters
keep_values = {"BGL", "SZROV"}  # for 'lager'
keep_lhm = {
    'DamenAccessoiresBeautyNOS', 'DamenAccessoiresBeautyFS',
    'DamenBeautySetsNOS', 'DamenBeautyDekorative KosmetikNOS',
    'DamenAccessoiresBeautyHW', 'DamenBeautyPflegeNOS',
    'StandardWomenBeautyMake-UpMake-UpNOS',
    'StandardMenBeautySkin & Hair CareSkin & Hair CareNOS',
    'StandardMenBeautyAccessoiresAccessoiresNOS',
    'StandardWomenBeautyAccessoiresAccessoiresNOS',
    'StandardWomenBeautySkin & Hair CareSkin & Hair CareNOS',
    'BeautyBeautyBeauty MixNOS', 'BeautyBeautyBeauty Mix SpecialNOS'
}

# 0-based numeric column indices within A..V: G(6), J(9), O(14), T(19)
NUM_IDXS = {6, 9, 14, 19}


def update_timestamp():
    """Updates a 'test' sheet with the current run time."""
    print(f"Updating timestamp in '{TIMESTAMPSHEET}' sheet...")
    gutils.ensure_sheet(SPREADSHEET_ID, TIMESTAMPSHEET)

    # Set format code based on Operating System
    if platform.system() == "Windows":
        date_format = "%#m/%d/%Y %H:%M:%S"  # Windows uses '#'
    else:
        date_format = "%-m/%d/%Y %H:%M:%S"  # macOS/Linux use '-'

    timestamp_string = datetime.now().strftime(date_format)

    gutils.update_values(
        SPREADSHEET_ID,
        f"'{TIMESTAMPSHEET}'!A2",
        [[f"Last Run: {timestamp_string}"]]
    )
    print("Timestamp updated.")


def prepare_main_sheet():
    """Ensures the main sheet exists, clears it, and writes the header."""
    print(f"Preparing main sheet: '{SHEET_NAME}'...")
    gutils.ensure_sheet(SPREADSHEET_ID, SHEET_NAME)
    gutils.clear_range(SPREADSHEET_ID, f"{SHEET_NAME}!A:V")  # wipe A..V
    gutils.update_values(SPREADSHEET_ID, f"{SHEET_NAME}!A1:V1", [HEADERS_A_TO_V])
    print("Main sheet prepared.")


def process_csv_and_upload():
    """Streams CSV, filters, cleans, and uploads data in batches."""
    print(f"Starting to process CSV file from: {CSV_INPUT_PATH}")
    buffer = []
    total_rows_uploaded = 0

    try:
        for chunk in pd.read_csv(CSV_INPUT_PATH, sep=";", dtype=str, chunksize=200000, engine="c"):
            # Robust views for filtering
            cat = chunk.get("category", pd.Series(index=chunk.index, dtype="object")).fillna("")
            lhm = chunk.get("sortkriterium", pd.Series(index=chunk.index, dtype="object")).fillna("")
            lager = chunk.get("lager", pd.Series(index=chunk.index, dtype="object")).fillna("")

            mask_lager = lager.str.strip().isin(keep_values)
            mask_beauty_or_lhm = cat.str.strip().str.casefold().eq("beauty") | lhm.str.strip().isin(keep_lhm)

            # Use .copy() to avoid SettingWithCopyWarning
            filtered_df = chunk.loc[mask_lager & mask_beauty_or_lhm].copy()

            if filtered_df.empty:
                continue

            # TRIM all string columns
            for col in filtered_df.select_dtypes(include=['object']).columns:
                filtered_df[col] = filtered_df[col].str.strip()

            # Drop Excel column AC (0-based index 28) if present
            if filtered_df.shape[1] > 28:
                filtered_df = filtered_df.drop(filtered_df.columns[28], axis=1)

            # Keep only first 22 columns (A..V). Pad if fewer.
            if filtered_df.shape[1] >= 22:
                filtered_df = filtered_df.iloc[:, :22]
            else:
                for i in range(22 - filtered_df.shape[1]):
                    filtered_df[f"pad{i+1}"] = ""
                filtered_df = filtered_df.iloc[:, :22]

            # Ensure types: Convert targeted columns to numeric (round to nearest int)
            for idx in NUM_IDXS:
                col_name = filtered_df.columns[idx]
                num = pd.to_numeric(filtered_df[col_name], errors="coerce").round(0)
                # Convert to Python ints where valid, else empty string
                filtered_df[col_name] = num.apply(lambda v: int(v) if pd.notna(v) else "")

            # All non-numeric columns -> strings (keep blanks)
            for idx, col_name in enumerate(filtered_df.columns):
                if idx not in NUM_IDXS:
                    # Fill NaN with empty string *before* converting to str
                    filtered_df[col_name] = filtered_df[col_name].fillna("")
                    # Ensure it's a string for sheets
                    filtered_df[col_name] = filtered_df[col_name].astype(str)

            # Build buffer (list of lists)
            buffer.extend(filtered_df.values.tolist())

            if len(buffer) >= BATCH_ROWS:
                print(f"Uploading {len(buffer)} rows...")
                gutils.append_rows(SPREADSHEET_ID, SHEET_NAME, buffer)
                total_rows_uploaded += len(buffer)
                buffer = []

        # Flush remainder
        if buffer:
            print(f"Uploading final {len(buffer)} rows...")
            gutils.append_rows(SPREADSHEET_ID, SHEET_NAME, buffer)
            total_rows_uploaded += len(buffer)

        print(f"\nDone: A..V cleared and rewritten with filtered data.")
        print(f"Total rows uploaded: {total_rows_uploaded}")

    except FileNotFoundError:
        print(f"Error: The file was not found at {CSV_INPUT_PATH}")
        print("Please check the 'CSV_INPUT_PATH' in your .env file.")
    except Exception as e:
        print(f"An error occurred during CSV processing: {e}")


def main():
    """Main execution function."""
    print("--- Starting CSV to Google Sheets Updater ---")
    gutils.init_service(SERVICE_ACCOUNT_FILE)

    update_timestamp()
    prepare_main_sheet()
    process_csv_and_upload()

    print("--- Script finished ---")


if __name__ == "__main__":
    main()