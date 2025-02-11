# filepath: /d:/plantai/flask-chatbot-app/gspread.py
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Define the scope
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Add credentials to the account
creds = ServiceAccountCredentials.from_json_keyfile_name("cred.json", scope)

# Authorize the clientsheet 
client = gspread.authorize(creds)

# Get the instance of the Spreadsheet
sheet = client.open("plantai").sheet1

# Function to read data from the spreadsheet
def read_data():
    data = sheet.get_all_records()
    return data

# Function to write data to the spreadsheet
def write_data(row, col, value):
    sheet.update_cell(row, col, value)

if __name__ == "__main__":
    # Example usage
    print("Reading data from the spreadsheet:")
    data = read_data()
    print(data)

    print("Writing data to the spreadsheet:")
    write_data(2, 2, "Hello, PlantAI!")
    print("Data written successfully.")