import importlib.util
import sys
import os
import logging
from datetime import datetime, timedelta
# Import database and search modules
try:
    from database import DatabaseManager
    from bikeSearch import BicycleSearch
except ImportError:
    # Fallback for when running as module
    try:
        from .database import DatabaseManager
        from .bikeSearch import BicycleSearch
    except ImportError:
        print("Error: Could not import required modules")
        raise

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Note: membershipManager.pyc is corrupted, using fallback functions
print("Note: Using fallback membership functions. Some functionality may be limited.")
load_memberships = lambda: {}
check_membership = lambda member_id, memberships: True
get_rental_limit = lambda member_id, memberships: 3

# Note: Working directory should be set by the calling script if needed

class RentalTransactionManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def log_rental_transaction(self, bicycle_id, member_id, rental_date, expected_return_date):
        """Logs a rental transaction."""
        self.db_manager.connect()
        try:
            # Get member info for better logging
            member_info = self.db_manager.get_member_info(member_id)
            member_name = member_info['NAME'] if member_info else f"ID:{member_id}"
            
            with self.db_manager.connection:
                self.db_manager.connection.execute('''INSERT INTO rental_transactions 
                (BICYCLE_ID, MEMBER_ID, RENTAL_DATE, RETURN_DATE) VALUES (?, ?, ?, ?)''', 
                (bicycle_id, member_id, rental_date, expected_return_date))
            logging.info(f"Logged rental transaction for Bicycle ID: {bicycle_id}, Member: {member_name} (ID: {member_id})")
        except Exception as e:
            logging.error(f"Failed to log rental transaction: {e}")
        finally:
            self.db_manager.close()

    def get_active_rentals_for_member(self, member_id):
        """Get the number of active rentals for a member."""
        self.db_manager.connect()
        try:
            cursor = self.db_manager.connection.cursor()
            cursor.execute('''SELECT COUNT(*) FROM rental_transactions 
                            WHERE MEMBER_ID = ? AND RETURN_DATE IS NULL''', (member_id,))
            count = cursor.fetchone()[0]
            return count
        except Exception as e:
            logging.error(f"Failed to get active rentals for member {member_id}: {e}")
            return 0
        finally:
            self.db_manager.close()

class BikeRentSystem:
    def __init__(self):
        # Initialize database and managers
        self.db_manager = DatabaseManager()
        self.rental_manager = RentalTransactionManager(self.db_manager)
        self.search_manager = BicycleSearch(self.db_manager)  # Pass db_manager to BicycleSearch
        
        # Load memberships
        self.memberships = load_memberships()

    def validate_member(self, member_id):
        """Validate if a member is eligible to rent a bicycle."""
        print(f"Validating membership for Member ID: {member_id}")

        # Get member info from database
        member_info = self.db_manager.get_member_info(member_id)
        if not member_info:
            return False, "Invalid or inactive membership."

        current_rentals = self.rental_manager.get_active_rentals_for_member(member_id)
        rental_limit = member_info.get('RENTAL_LIMIT', 3)
        
        if current_rentals >= rental_limit:
            return False, f"Rental limit exceeded. Limit: {rental_limit}, Current rentals: {current_rentals}."

        return True, f"Member {member_info['NAME']} validated and eligible to rent."

    def validate_bicycle(self, bicycle_id):
        """Verify if a bicycle is available for rent by ID."""
        bicycle = self.search_manager.get_bicycle_by_id(bicycle_id)  # Ensure this method exists in BicycleSearch
        
        if not bicycle:
            return False, "Bicycle ID not found."
        
        if bicycle["STATUS"].lower() != "available":
            return False, f"Bicycle with ID {bicycle_id} is not available for rent. Current status: {bicycle['STATUS']}."

        return True, "Bicycle is available for rent."

    def rent_bicycle(self):
        """Prompts for Member ID and Bicycle ID, performs the necessary checks, and updates the database if the rental is successful."""
        try:
            member_id = int(input("Enter Member ID: "))
            bicycle_id = int(input("Enter Bicycle ID to rent: "))

            is_valid_member, member_message = self.validate_member(member_id)
            if not is_valid_member:
                print(member_message)
                return

            is_available, bike_message = self.validate_bicycle(bicycle_id)
            if not is_available:
                print(bike_message)
                return

            rental_date = datetime.now().strftime("%Y-%m-%d")
            expected_return_date = self.calculate_expected_return_date()
            self.rental_manager.log_rental_transaction(bicycle_id, member_id, rental_date, expected_return_date)
            print(f"Rental confirmed for Bicycle ID {bicycle_id} by Member ID {member_id}. Expected return date: {expected_return_date}.")

        except ValueError:
            print("Invalid input. Please enter numeric values for Member ID and Bicycle ID.")
        except Exception as e:
            print(f"An error occurred while processing the rental: {e}")

    def calculate_expected_return_date(self):
        """Calculates the expected return date based on rental policy (e.g., 7 days rental period)."""
        rental_period = 7  # Example: bikes are rented for a week
        expected_return_date = datetime.now() + timedelta(days=rental_period)
        return expected_return_date.strftime("%Y-%m-%d")

    def list_all_bicycles(self):
        """Lists all bicycles in the database for inventory review."""
        try:
            bicycles = self.search_manager.list_all_bicycles()
            for bike in bicycles:
                print(bike)
        except Exception as e:
            print(f"Error listing bicycles: {e}")

# Example Usage
if __name__ == "__main__":
    # When running directly, use absolute imports
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    from database import DatabaseManager
    
    db_manager = DatabaseManager()
    db_manager.populate_bicycles()  # Load bicycle data from Bicycle_Info.txt
    
    bike_rent_system = BikeRentSystem()
    bike_rent_system.list_all_bicycles()  # Display all bicycles for inventory check
    
    bike_rent_system.rent_bicycle()  # Prompt for Member ID and Bicycle ID to rent
