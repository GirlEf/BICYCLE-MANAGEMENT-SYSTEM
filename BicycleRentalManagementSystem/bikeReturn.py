import sqlite3
from datetime import datetime, timedelta
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class BikeReturn:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def return_bike(self, bicycle_id, member_id):
        """Handles the return of a rented bicycle, including damage and late fee assessment."""
        try:
            self.db_manager.connect()
            cursor = self.db_manager.connection.cursor()

            # Validate bicycle ID and member ID input
            if not self.validate_ids(bicycle_id, member_id):
                return False, "Invalid bicycle ID or member ID"

            # Check if the bike is currently rented by the member
            transaction = self.get_active_rental(cursor, bicycle_id, member_id)
            if not transaction:
                return False, f"No active rental found for Bicycle ID {bicycle_id} and Member ID {member_id}"

            # Display current rental details
            self.display_rental_details(transaction, bicycle_id, member_id)

            # Confirm the return
            if not self.confirm_return():
                return False, "Return canceled by user"

            # Update the rental transaction with the return date
            return_date = datetime.now().strftime("%Y-%m-%d")
            self.update_rental_transaction(cursor, transaction, return_date)

            # Calculate and display late fee
            late_fee = self.calculate_late_fee(transaction[2], member_id)  # rental_date is at index 2

            # Assess damage and calculate damage fee
            damage_fee = self.assess_damage()

            # Store fees in rental_fees table
            self.store_fees(cursor, transaction[0], late_fee, damage_fee)  # transaction_id is at index 0

            # Update the bike's status and condition
            new_condition = self.update_bike_status(cursor, bicycle_id)

            # Commit changes
            self.db_manager.connection.commit()
            logging.info(f"Bicycle {bicycle_id} returned successfully by member {member_id}")

            # Provide a summary to the member
            self.display_return_summary(bicycle_id, member_id, transaction, return_date, late_fee, damage_fee)
            
            return True, "Bicycle returned successfully"

        except Exception as e:
            logging.error(f"Error during bike return: {e}")
            if self.db_manager.connection:
                self.db_manager.connection.rollback()
            return False, f"Error during return: {str(e)}"
        finally:
            self.db_manager.close()

    def validate_ids(self, bicycle_id, member_id):
        """Validate bicycle and member IDs."""
        try:
            int(bicycle_id)
            int(member_id)
            return True
        except ValueError:
            print("Bicycle ID and Member ID must be numeric values.")
            return False

    def get_active_rental(self, cursor, bicycle_id, member_id):
        """Check if the bicycle is currently rented by the member."""
        try:
            cursor.execute(
                "SELECT * FROM rental_transactions WHERE BICYCLE_ID = ? AND MEMBER_ID = ? AND RETURN_DATE IS NULL",
                (bicycle_id, member_id)
            )
            result = cursor.fetchone()
            if result:
                # Convert to list for easier access
                columns = [description[0] for description in cursor.description]
                return list(result)
            return None
        except Exception as e:
            logging.error(f"Error getting active rental: {e}")
            return None

    def display_rental_details(self, transaction, bicycle_id, member_id):
        """Display details of the rental transaction."""
        try:
            rental_date = transaction[2]  # rental_date
            print(f"\nRental found:")
            print(f" - Rental Date: {rental_date}")
            print(f" - Bicycle ID: {bicycle_id}")
            print(f" - Member ID: {member_id}")
            print(f" - Transaction ID: {transaction[0]}")
            print()
        except Exception as e:
            logging.error(f"Error displaying rental details: {e}")

    def confirm_return(self):
        """Ask user to confirm the return."""
        try:
            confirm = input("Confirm return for this bicycle? (yes/no): ").strip().lower()
            return confirm == "yes"
        except Exception:
            return False

    def update_rental_transaction(self, cursor, transaction, return_date):
        """Update the rental transaction with the return date."""
        try:
            cursor.execute(
                "UPDATE rental_transactions SET RETURN_DATE = ? WHERE TRANSACTION_ID = ?",
                (return_date, transaction[0])  # transaction_id
            )
            print(f"Bicycle return date recorded as {return_date}.")
        except Exception as e:
            logging.error(f"Error updating rental transaction: {e}")
            raise

    def calculate_late_fee(self, rental_date, member_id):
        """Calculate late fees based on rental duration."""
        try:
            # Parse rental date
            if isinstance(rental_date, str):
                rental_datetime = datetime.strptime(rental_date, "%Y-%m-%d")
            else:
                rental_datetime = rental_date
            
            days_rented = (datetime.now() - rental_datetime).days
            allowed_days = self.calculate_allowed_days(member_id)
            late_fee = max(0, (days_rented - allowed_days) * 10)  # $10 per day late
            
            if late_fee > 0:
                print(f"Late Fee Applied: ${late_fee} for {days_rented - allowed_days} days over the limit.")
            else:
                print(f"No late fee - returned within {days_rented} days (limit: {allowed_days} days)")
            
            return late_fee
        except Exception as e:
            logging.error(f"Error calculating late fee: {e}")
            return 0

    def assess_damage(self):
        """Assess if there is damage to the bike and add a damage fee if needed."""
        try:
            damaged = input("Is the bike damaged? (yes/no): ").strip().lower()
            if damaged == "yes":
                while True:
                    try:
                        damage_fee = float(input("Enter damage fee amount ($): ").strip())
                        if damage_fee >= 0:
                            print(f"Damage Fee Applied: ${damage_fee}")
                            return damage_fee
                        else:
                            print("Damage fee must be a positive number.")
                    except ValueError:
                        print("Please enter a valid number for the damage fee.")
            else:
                print("No damage fee applied.")
                return 0
        except Exception as e:
            logging.error(f"Error assessing damage: {e}")
            return 0

    def store_fees(self, cursor, transaction_id, late_fee, damage_fee):
        """Store the calculated fees in the rental_fees table."""
        try:
            cursor.execute(
                "INSERT OR REPLACE INTO rental_fees (TRANSACTION_ID, LATE_FEE, DAMAGE_FEE) VALUES (?, ?, ?)",
                (transaction_id, late_fee, damage_fee)
            )
            print(f"Fees stored: Late Fee: ${late_fee}, Damage Fee: ${damage_fee}")
        except Exception as e:
            logging.error(f"Error storing fees: {e}")
            raise

    def update_bike_status(self, cursor, bicycle_id):
        """Update the bike's status and condition after return."""
        try:
            # Get current bike condition
            cursor.execute("SELECT CONDITION FROM bicycles WHERE ID = ?", (bicycle_id,))
            current_condition = cursor.fetchone()
            
            print(f"Current bike condition: {current_condition[0] if current_condition else 'Unknown'}")
            
            # Ask for new condition
            while True:
                new_condition = input("Enter updated condition (New/Good/Fair/Damaged): ").strip().capitalize()
                if new_condition in ['New', 'Good', 'Fair', 'Damaged']:
                    break
                else:
                    print("Please enter a valid condition: New, Good, Fair, or Damaged")
            
            # Update bike status and condition
            cursor.execute(
                "UPDATE bicycles SET STATUS = 'Available', CONDITION = ? WHERE ID = ?", 
                (new_condition, bicycle_id)
            )
            
            print(f"Bicycle {bicycle_id} status updated to 'Available' with condition: {new_condition}")
            return new_condition
            
        except Exception as e:
            logging.error(f"Error updating bike status: {e}")
            raise

    def display_return_summary(self, bicycle_id, member_id, transaction, return_date, late_fee, damage_fee):
        """Display a summary of the return transaction."""
        try:
            rental_date = transaction[2]  # rental_date
            total_fees = late_fee + damage_fee
            
            print("\n" + "="*50)
            print("RETURN SUMMARY")
            print("="*50)
            print(f"Bicycle ID: {bicycle_id}")
            print(f"Member ID: {member_id}")
            print(f"Rental Period: {rental_date} to {return_date}")
            print(f"Late Fee: ${late_fee:.2f}")
            print(f"Damage Fee: ${damage_fee:.2f}")
            print(f"Total Fees: ${total_fees:.2f}")
            print("="*50)
            
            if total_fees > 0:
                print(f"⚠️  Total amount due: ${total_fees:.2f}")
            else:
                print("✅ No fees due - thank you for returning on time!")
            
            print("\nThank you for returning the bike!")
            
        except Exception as e:
            logging.error(f"Error displaying return summary: {e}")

    def calculate_allowed_days(self, member_id):
        """Calculates allowed rental days based on membership type."""
        try:
            # This could be enhanced to check actual membership details
            # For now, using a default value
            allowed_days = 7  # Default allowed days (1 week)
            print(f"Allowed Rental Days: {allowed_days} days")
            return allowed_days
        except Exception as e:
            logging.error(f"Error calculating allowed days: {e}")
            return 7  # Default fallback

    def get_returnable_bikes(self):
        """Get a list of all currently rented bicycles that can be returned."""
        try:
            self.db_manager.connect()
            cursor = self.db_manager.connection.cursor()
            
            cursor.execute("""
                SELECT rt.TRANSACTION_ID, rt.BICYCLE_ID, rt.MEMBER_ID, rt.RENTAL_DATE,
                       b.BRAND, b.TYPE, b.CONDITION
                FROM rental_transactions rt
                JOIN bicycles b ON rt.BICYCLE_ID = b.ID
                WHERE rt.RETURN_DATE IS NULL
                ORDER BY rt.RENTAL_DATE
            """)
            
            results = cursor.fetchall()
            return results
            
        except Exception as e:
            logging.error(f"Error getting returnable bikes: {e}")
            return []
        finally:
            self.db_manager.close()

    def display_returnable_bikes(self):
        """Display all bicycles that are currently rented and can be returned."""
        bikes = self.get_returnable_bikes()
        
        if not bikes:
            print("No bicycles are currently rented.")
            return
        
        print(f"\nCurrently Rented Bicycles ({len(bikes)} total):")
        print("-" * 80)
        print(f"{'Transaction ID':<15} {'Bicycle ID':<12} {'Member ID':<10} {'Rental Date':<12} {'Brand':<15} {'Type':<15}")
        print("-" * 80)
        
        for bike in bikes:
            transaction_id, bicycle_id, member_id, rental_date, brand, bike_type, condition = bike
            print(f"{transaction_id:<15} {bicycle_id:<12} {member_id:<10} {rental_date:<12} {brand:<15} {bike_type:<15}")
        
        print("-" * 80)

# Example usage
if __name__ == "__main__":
    from database import DatabaseManager
    
    db_manager = DatabaseManager()
    bike_return = BikeReturn(db_manager)
    
    print("🚲 Bicycle Return System")
    print("=" * 40)
    
    # Show returnable bikes
    bike_return.display_returnable_bikes()
    
    print("\n" + "=" * 40)
    
    # Get return details
    bicycle_id = input("Enter bicycle ID to return: ").strip()
    member_id = input("Enter member ID: ").strip()
    
    # Process return
    success, message = bike_return.return_bike(bicycle_id, member_id)
    
    if not success:
        print(f"❌ Return failed: {message}")
    else:
        print(f"✅ {message}")
