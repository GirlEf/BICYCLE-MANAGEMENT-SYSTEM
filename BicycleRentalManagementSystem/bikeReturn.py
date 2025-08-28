import sqlite3  # Import the sqlite3 module
from database import DatabaseManager
from datetime import datetime

class BikeReturn(DatabaseManager):
    def return_bike(self, bicycle_id, member_id):
        """Handles the return of a rented bicycle, including damage and late fee assessment."""
        self.connect()
        cursor = self.connection.cursor()

        # Validate bicycle ID and member ID input
        if not self.validate_ids(bicycle_id, member_id):
            return

        # Check if the bike is currently rented by the member
        transaction = self.get_active_rental(cursor, bicycle_id, member_id)
        if not transaction:
            print(f"No active rental found for Bicycle ID {bicycle_id} and Member ID {member_id}.")
            self.close()
            return

        # Display current rental details
        self.display_rental_details(transaction, bicycle_id, member_id)

        # Confirm the return
        if not self.confirm_return():
            print("Return canceled.")
            self.close()
            return

        # Update the rental transaction with the return date
        return_date = datetime.now().strftime("%Y-%m-%d")
        self.update_rental_transaction(cursor, transaction, return_date)

        # Calculate and display late fee
        late_fee = self.calculate_late_fee(transaction["rental_date"], member_id)

        # Assess damage and calculate damage fee
        damage_fee = self.assess_damage()

        # Store fees in rental_fees table
        self.store_fees(cursor, transaction, late_fee, damage_fee)

        # Update the bike's status and condition
        new_condition = self.update_bike_status(cursor, bicycle_id)

        # Commit changes and close the connection
        self.connection.commit()
        self.close()

        # Provide a summary to the member
        self.display_return_summary(bicycle_id, member_id, transaction, return_date, late_fee, damage_fee)

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
        cursor.execute(
            "SELECT * FROM rental_transactions WHERE bicycle_id = ? AND member_id = ? AND return_date IS NULL",
            (bicycle_id, member_id)
        )
        return cursor.fetchone()

    def display_rental_details(self, transaction, bicycle_id, member_id):
        """Display details of the rental transaction."""
        rental_date = transaction["rental_date"]
        print(f"\nRental found:\n - Rental Date: {rental_date}\n - Bicycle ID: {bicycle_id}\n - Member ID: {member_id}\n")

    def confirm_return(self):
        """Ask user to confirm the return."""
        confirm = input("Confirm return for this bicycle? (yes/no): ").strip().lower()
        return confirm == "yes"

    def update_rental_transaction(self, cursor, transaction, return_date):
        """Update the rental transaction with the return date."""
        cursor.execute(
            "UPDATE rental_transactions SET return_date = ? WHERE transaction_id = ?",
            (return_date, transaction["transaction_id"])
        )
        print(f"\nBicycle return date recorded as {return_date}.\n")

    def calculate_late_fee(self, rental_date, member_id):
        """Calculate late fees based on rental duration."""
        days_rented = (datetime.now() - datetime.strptime(rental_date, "%Y-%m-%d")).days
        allowed_days = self.calculate_allowed_days(member_id)
        late_fee = max(0, (days_rented - allowed_days) * 10)  # e.g., $10 per day late
        if late_fee > 0:
            print(f"Late Fee Applied: ${late_fee} for {days_rented - allowed_days} days over the limit.")
        return late_fee

    def assess_damage(self):
        """Assess if there is damage to the bike and add a damage fee if needed."""
        damaged = input("Is the bike damaged? (yes/no): ").strip().lower()
        if damaged == "yes":
            damage_fee = float(input("Enter damage fee amount: ").strip())
            print(f"Damage Fee Applied: ${damage_fee}")
            return damage_fee
        else:
            print("No damage fee applied.")
            return 0

    def store_fees(self, cursor, transaction, late_fee, damage_fee):
        """Store the calculated fees in the rental_fees table."""
        cursor.execute(
            "INSERT OR REPLACE INTO rental_fees (transaction_id, late_fee, damage_fee) VALUES (?, ?, ?)",
            (transaction["transaction_id"], late_fee, damage_fee)
        )

    def update_bike_status(self, cursor, bicycle_id):
        """Update the bike's status and condition after return."""
        new_condition = input("Enter updated condition of the bike (e.g., Good, Fair, Damaged): ").strip().capitalize()
        cursor.execute("UPDATE bicycles SET status = 'Available', condition = ? WHERE id = ?", (new_condition, bicycle_id))
        print(f"\nBicycle {bicycle_id} status updated to 'Available' with condition: {new_condition}\n")
        return new_condition

    def display_return_summary(self, bicycle_id, member_id, transaction, return_date, late_fee, damage_fee):
        """Display a summary of the return transaction."""
        rental_date = transaction["rental_date"]
        print("Return Summary:")
        print(f" - Bicycle ID: {bicycle_id}")
        print(f" - Member ID: {member_id}")
        print(f" - Rental Period: {rental_date} to {return_date}")
        print(f" - Late Fee: ${late_fee}")
        print(f" - Damage Fee: ${damage_fee}")
        print(f" - Total Fees: ${late_fee + damage_fee}")
        print("\nThank you for returning the bike!")

    def calculate_allowed_days(self, member_id):
        """Calculates allowed rental days based on a general default or custom rules."""
        allowed_days = 5  # Default allowed days
        print(f"Allowed Rental Days: {allowed_days} days")
        return allowed_days

# Example usage
if __name__ == "__main__":
    bike_return = BikeReturn()
    bicycle_id = input("Enter bicycle ID to return: ").strip()
    member_id = input("Enter member ID: ").strip()
    bike_return.return_bike(bicycle_id, member_id)
