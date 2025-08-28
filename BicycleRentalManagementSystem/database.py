import os
import sqlite3
import logging
import csv
from datetime import datetime

# Set up logging
logging.basicConfig(filename='database_manager.log', level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')

class DatabaseManager:
    def __init__(self, db_file="BicycleRental.db"):
        # Set to an absolute path to avoid ambiguity
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_file = os.path.join(base_dir, db_file)
        self.connection = None
        self.create_tables()  # Ensure tables are created upon initialization

    def connect(self):
        """Creates a database connection."""
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_file)
            self.connection.row_factory = sqlite3.Row  # Enable dictionary-like row access
            logging.info("Database connection established.")

    def close(self):
        """Closes the database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
            logging.info("Database connection closed.")

    def create_tables(self):
        """Creates the necessary database tables with data integrity constraints."""
        self.connect()
        with self.connection as conn:
            cursor = conn.cursor()

            # Create bicycles table
            cursor.execute('''CREATE TABLE IF NOT EXISTS bicycles (
                ID INTEGER PRIMARY KEY,
                BRAND TEXT NOT NULL,
                TYPE TEXT NOT NULL,
                FRAME_SIZE TEXT NOT NULL,
                RENTAL_RATE TEXT NOT NULL,
                PURCHASE_DATE TEXT NOT NULL,
                CONDITION TEXT CHECK(CONDITION IN ('New', 'Good', 'Damaged')) DEFAULT 'Good',
                STATUS TEXT CHECK(STATUS IN ('Available', 'Rented', 'Under Maintenance')) DEFAULT 'Available'
            )''')

            # Create members table
            cursor.execute('''CREATE TABLE IF NOT EXISTS members (
                MemberID INTEGER PRIMARY KEY,
                RentalLimit INTEGER NOT NULL,
                MembershipEndDate TEXT NOT NULL
            )''')

            # Create rental transactions table
            cursor.execute('''CREATE TABLE IF NOT EXISTS rental_transactions (
                TRANSACTION_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                BICYCLE_ID INTEGER NOT NULL,
                MEMBER_ID INTEGER NOT NULL,
                RENTAL_DATE TEXT NOT NULL,
                RETURN_DATE TEXT,
                FOREIGN KEY(BICYCLE_ID) REFERENCES bicycles(ID)
            )''')

            # Create rental fees table
            cursor.execute('''CREATE TABLE IF NOT EXISTS rental_fees (
                TRANSACTION_ID INTEGER PRIMARY KEY,
                LATE_FEE REAL DEFAULT 0,
                DAMAGE_FEE REAL DEFAULT 0,
                FOREIGN KEY(TRANSACTION_ID) REFERENCES rental_transactions(TRANSACTION_ID)
            )''')

        logging.info("Database tables created or verified.")
        self.close()

    def populate_bicycles(self, filename="Bicycle_Info.txt"):
        """Loads bicycle data from Bicycle_Info.txt into the bicycles table."""
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
        
        if not os.path.exists(file_path):
            logging.error(f"{file_path} not found.")
            print(f"Error: {file_path} not found. Please ensure the file is located at the specified path.")
            return
        
        self.connect()
        try:
            with open(file_path, mode="r") as file:
                reader = csv.DictReader(file, delimiter='|')
                for row in reader:
                    # Validate row data before insertion
                    self.validate_bicycle_data(row)
                    with self.connection as conn:
                        conn.execute('''INSERT OR IGNORE INTO bicycles (ID, BRAND, TYPE, FRAME_SIZE, RENTAL_RATE, PURCHASE_DATE, CONDITION, STATUS)
                                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', (
                            int(row["ID"]), row["Brand"], row["Type"], row["Frame Size"],
                            row["Rental Rate"], self.clean_date(row["Purchase Date"]),
                            row["Condition"], row["Status"]
                        ))
            logging.info("Bicycles data loaded successfully.")
        except Exception as e:
            logging.error(f"Error populating bicycles: {e}")
            print(f"An error occurred while populating bicycles: {e}")
        finally:
            self.close()

    def validate_bicycle_data(self, row):
        """Validates the bicycle data from a row before insertion."""
        if not row.get("ID") or not row.get("Brand") or not row.get("Type"):
            raise ValueError("ID, Brand, and Type are required fields.")
        # Additional validation checks can be added here

    def populate_members(self, filename="members.txt"):
        """Loads member data from members.txt into the members table."""
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
        
        if not os.path.exists(file_path):
            logging.error(f"{file_path} not found.")
            print(f"Error: {file_path} not found. Please ensure the file is located at the specified path.")
            return
        
        self.connect()
        try:
            with open(file_path, mode="r") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # Validate row data before insertion
                    self.validate_member_data(row)
                    with self.connection as conn:
                        conn.execute('''INSERT OR REPLACE INTO members (MemberID, RentalLimit, MembershipEndDate)
                                        VALUES (?, ?, ?)''', (
                            int(row["MemberID"]), int(row["RentalLimit"]), row["MembershipEndDate"]
                        ))
            logging.info("Members data loaded successfully.")
        except Exception as e:
            logging.error(f"Error populating members: {e}")
            print(f"An error occurred while populating members: {e}")
        finally:
            self.close()

    def validate_member_data(self, row):
        """Validates the member data from a row before insertion."""
        if not row.get("MemberID") or not row.get("RentalLimit"):
            raise ValueError("MemberID and RentalLimit are required fields.")
        # Additional validation checks can be added here

    def clean_date(self, date_str):
        """Cleans and formats date strings, returning None for invalid dates."""
        try:
            return datetime.strptime(date_str, "%d/%m/%Y").strftime("%Y-%m-%d")
        except ValueError:
            logging.warning(f"Invalid date format: {date_str}")
            print(f"Warning: Invalid date format '{date_str}'. Expected format 'dd/mm/yyyy'.")
            return None

# Example usage
if __name__ == "__main__":
    db_manager = DatabaseManager()
    db_manager.populate_bicycles()  # Load bicycles data from Bicycle_Info.txt
    db_manager.populate_members()   # Load members data from members.txt
