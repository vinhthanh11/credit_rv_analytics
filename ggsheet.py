import gspread
from google.oauth2.service_account import Credentials

# CONFIG
CREDENTIALS_FILE = "bond_data.json"
SPREADSHEET_ID = "18mUrmjxvfKvVHpsXsz-MSvUFCwAHXdmWguGSVa9gODk"
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets"
]


# --------------------------------------------------
# Google Sheets Connection
# --------------------------------------------------

def get_client():
    """
    Authenticate with Google Sheets using
    the service account credentials.
    """

    credentials = Credentials.from_service_account_file(
        CREDENTIALS_FILE,
        scopes=SCOPES
    )

    return gspread.authorize(credentials)


def get_workbook():
    """
    Connect to the Bond Trading Google Sheet.
    """
    client = get_client()
    return client.open_by_key(SPREADSHEET_ID)


# --------------------------------------------------
# Worksheet Functions
# --------------------------------------------------

def get_sheet_names():
    """
    Return all worksheet/tab names.
    """
    workbook = get_workbook()

    return [
        worksheet.title
        for worksheet in workbook.worksheets()
    ]


def get_sheet(sheet_name):
    """
    Return a particular worksheet.
    """

    workbook = get_workbook()

    return workbook.worksheet(sheet_name)


def get_records(sheet_name):
    """
    Return worksheet data as a list of dictionaries.

    Example:
    [
        {"CUSIP": "...", "Issuer": "..."},
        {"CUSIP": "...", "Issuer": "..."}
    ]
    """

    worksheet = get_sheet(sheet_name)

    return worksheet.get_all_records()


# --------------------------------------------------
# Test
# --------------------------------------------------

if __name__ == "__main__":

    print("Connecting to Google Sheets...")

    sheet_names = get_sheet_names()

    print("Connected.")
    print("Available sheets:")

    for name in sheet_names:
        print(f" - {name}")