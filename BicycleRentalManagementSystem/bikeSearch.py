import sqlite3  # Import the sqlite3 module
# Conditional imports for module vs direct execution
try:
    from .database import DatabaseManager
except ImportError:
    # When running directly, use absolute imports
    from database import DatabaseManager

class BicycleSearch:
    def __init__(self, db_manager):
        self.db_manager = db_manager
    def search_bicycles(self, brand=None, bike_type=None, status="available", condition=None, min_rate=None, max_rate=None, sort_by=None):
        """Searches for bicycles based on specified criteria."""
        self.db_manager.connect()
        cursor = self.db_manager.connection.cursor()
        
        # Base query
        query = "SELECT * FROM bicycles WHERE LOWER(STATUS) = LOWER(?)"
        criteria = [status]

        # Add filters based on user input
        if brand:
            query += " AND LOWER(BRAND) LIKE LOWER(?)"
            criteria.append(f"%{brand}%")
        if bike_type:
            query += " AND LOWER(TYPE) LIKE LOWER(?)"
            criteria.append(f"%{bike_type}%")
        if condition:
            query += " AND LOWER(CONDITION) LIKE LOWER(?)"
            criteria.append(f"%{condition}%")
        if min_rate is not None:
            query += " AND CAST(SUBSTR(RENTAL_RATE, 1, INSTR(RENTAL_RATE, '/') - 1) AS INTEGER) >= ?"
            criteria.append(min_rate)
        if max_rate is not None:
            query += " AND CAST(SUBSTR(RENTAL_RATE, 1, INSTR(RENTAL_RATE, '/') - 1) AS INTEGER) <= ?"
            criteria.append(max_rate)

        # Sorting if specified
        if sort_by in ["BRAND", "TYPE", "RENTAL_RATE", "CONDITION"]:
            query += f" ORDER BY {sort_by}"

        # Execute the search query
        try:
            print("Executing query:", query)
            cursor.execute(query, criteria)
            results = cursor.fetchall()
        except sqlite3.OperationalError as e:
            print(f"Database error: {e}")
            self.db_manager.close()
            return

        # Display results or suggest similar bicycles
        if results:
            print("Exact matches found:")
            self.display_results(results)
            self.display_summary(results)
        else:
            print("No exact matches found.")
            self.suggest_similar_bicycles(cursor, brand, bike_type, status, condition)  # Suggest similar bicycles
        self.db_manager.close()

    def suggest_similar_bicycles(self, cursor, brand, bike_type, status, condition):
        """Suggests similar bicycles by relaxing search criteria."""
        suggestions_query = "SELECT * FROM bicycles WHERE LOWER(STATUS) = LOWER(?)"
        suggestion_criteria = [status]

        # Relaxed conditions for similarity suggestions
        if brand:
            suggestions_query += " AND LOWER(BRAND) LIKE LOWER(?)"
            suggestion_criteria.append(f"%{brand}%")
        if bike_type:
            suggestions_query += " OR LOWER(TYPE) LIKE LOWER(?)"
            suggestion_criteria.append(f"%{bike_type}%")
        if condition:
            suggestions_query += " OR LOWER(CONDITION) LIKE LOWER(?)"
            suggestion_criteria.append(f"%{condition}%")

        print("Executing suggestions query:", suggestions_query)
        cursor.execute(suggestions_query, suggestion_criteria)
        suggestions = cursor.fetchall()
        
        if suggestions:
            print("Similar bicycles found:")
            self.display_results(suggestions)
            self.display_summary(suggestions)
        else:
            print("No similar bicycles available at this time.")

    def display_results(self, results, page_size=10):
        """Displays search results with pagination."""
        if not results:
            print("No results found.")
            return
        
        for i in range(0, len(results), page_size):
            for row in results[i:i+page_size]:
                print(f"ID: {row[0]}, Brand: {row[1]}, Type: {row[2]}, Frame Size: {row[3]}, "
                      f"Rental Rate: {row[4]}, Purchase Date: {row[5]}, Condition: {row[6]}, Status: {row[7]}")
            if i + page_size < len(results):
                if input("View more results? (yes/no): ").strip().lower() != "yes":
                    break

    def display_summary(self, results):
        """Displays a summary of the search results."""
        total_bikes = len(results)
        if total_bikes > 0:
            avg_rate = sum(float(row[4].split('/')[0]) for row in results if row[4]) / total_bikes
            print(f"\nSummary: Total Bikes Found: {total_bikes}, Average Daily Rate: ${avg_rate:.2f}\n")

    def get_user_input_and_search(self):
        """Gets user input for search criteria and performs the search."""
        print("Enter search criteria (leave blank to ignore a criterion):")
        brand = input("Enter bike brand: ").strip()
        bike_type = input("Enter bike type (e.g., Road Bike): ").strip()
        status = input("Enter bike status (e.g., available, rented): ").strip() or "available"
        condition = input("Enter bike condition (e.g., new, fair, damaged): ").strip()

        min_rate_input = input("Enter minimum daily rental rate: ").strip()
        max_rate_input = input("Enter maximum daily rental rate: ").strip()

        try:
            min_rate = int(min_rate_input) if min_rate_input else None
            max_rate = int(max_rate_input) if max_rate_input else None
        except ValueError:
            print("Invalid rate input. Please enter numbers only.")
            return

        sort_by = input("Sort results by (options: BRAND, TYPE, RENTAL_RATE, CONDITION; leave blank for no sorting): ").strip().upper()

        self.search_bicycles(
            brand=brand or None, 
            bike_type=bike_type or None, 
            status=status, 
            condition=condition or None, 
            min_rate=min_rate, 
            max_rate=max_rate, 
            sort_by=sort_by or None
        )

    def get_bicycle_by_id(self, bicycle_id):
        """Get a specific bicycle by its ID."""
        self.db_manager.connect()
        try:
            cursor = self.db_manager.connection.cursor()
            cursor.execute("SELECT * FROM bicycles WHERE ID = ?", (bicycle_id,))
            result = cursor.fetchone()
            
            if result:
                # Convert to dictionary format for easier access
                columns = [description[0] for description in cursor.description]
                bicycle_dict = dict(zip(columns, result))
                return bicycle_dict
            else:
                return None
        except Exception as e:
            print(f"Error retrieving bicycle {bicycle_id}: {e}")
            return None
        finally:
            self.db_manager.close()

    def list_all_bicycles(self):
        """List all bicycles in the database."""
        self.db_manager.connect()
        try:
            cursor = self.db_manager.connection.cursor()
            cursor.execute("SELECT * FROM bicycles ORDER BY ID")
            results = cursor.fetchall()
            
            bicycles = []
            for row in results:
                columns = [description[0] for description in cursor.description]
                bicycle_dict = dict(zip(columns, row))
                bicycles.append(bicycle_dict)
            
            return bicycles
        except Exception as e:
            print(f"Error listing bicycles: {e}")
            return []
        finally:
            self.db_manager.close()

# Run the program
if __name__ == "__main__":
    db_manager = DatabaseManager()
    search = BicycleSearch(db_manager)
    search.get_user_input_and_search()
