import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os

class BikeSelector:
    def __init__(self, bike_data_file="Bicycle_Info.txt", rental_data_file="Rental_History.txt"):
        # Set up the absolute paths to the files
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.bike_data_path = os.path.join(base_dir, bike_data_file)
        self.rental_data_path = os.path.join(base_dir, rental_data_file)
        
        # Loading bike and rental data from the .txt files
        self.bike_data = self.load_data(self.bike_data_path)
        self.rental_data = self.load_data(self.rental_data_path)
        
        self.clean_data()
        self.current_year = datetime.now().year

    def load_data(self, file_path):
        """Loads data from a specified file path."""
        try:
            data = pd.read_csv(file_path, sep="|")
            return data
        except FileNotFoundError:
            print(f"Error: {file_path} not found. Please ensure the file is located at the specified path.")
            return pd.DataFrame()  # Return an empty DataFrame if file not found

    def clean_data(self):
        """Cleans and preprocesses bike and rental data."""
        # Process the rental rate by extracting the daily rate
        self.bike_data['Rental Rate'] = self.bike_data['Rental Rate'].str.split(';').str[0]
        
        # Remove any dollar signs and '/day' suffix, then convert to float; fill non-numeric with NaN and then with 0.0
        self.bike_data['Rental Rate'] = (
            self.bike_data['Rental Rate']
            .replace({'\$': '', '/day': '', 'Missing': '0'}, regex=True)
            .astype(float)
            .fillna(0.0)  # Fill missing values with 0.0
        )
        
        # Convert 'Condition' and 'Status' to lowercase for consistency
        self.bike_data['Condition'] = self.bike_data['Condition'].str.lower()
        self.bike_data['Status'] = self.bike_data['Status'].str.lower()
        
        # Convert 'Purchase Date' and 'Rental Date' to datetime format with day-first
        self.bike_data['Purchase Date'] = pd.to_datetime(self.bike_data['Purchase Date'], dayfirst=True, errors='coerce')
        self.rental_data['Rental Date'] = pd.to_datetime(self.rental_data['Rental Date'], dayfirst=True, errors='coerce')

    def rental_frequency_analysis(self):
        """Analyzes rental frequency by bike type."""
        try:
            bike_type_counts = self.rental_data.merge(self.bike_data[['ID', 'Type']], left_on='Bicycle ID', right_on='ID') \
                                               .groupby('Type').size().sort_values(ascending=False)
            return bike_type_counts
        except Exception as e:
            print(f"Error during rental frequency analysis: {e}")
            return pd.Series()

    def age_analysis(self):
        """Calculates the average age of each bike type."""
        self.bike_data['Age'] = self.current_year - self.bike_data['Purchase Date'].dt.year
        return self.bike_data[['Type', 'Age']].groupby('Type').mean().sort_values(by='Age', ascending=False)

    def condition_analysis(self):
        """Counts the number of bikes in poor condition by type."""
        condition_counts = self.bike_data[self.bike_data['Condition'] == 'poor']['Type'].value_counts()
        return condition_counts

    def recommend_purchases(self, budget, avg_cost_per_bike=100):
        """Generates a purchase recommendation based on budget and demand factors."""
        recommended_purchases = []

        # Analysis factors: rental frequency, age, and condition
        rental_freq = self.rental_frequency_analysis()
        avg_age = self.age_analysis()
        poor_condition_counts = self.condition_analysis()

        for bike_type, freq in rental_freq.items():
            # Determine purchase needs based on demand, age, and condition
            age_factor = avg_age.loc[bike_type, 'Age'] if bike_type in avg_age.index else 0
            condition_factor = poor_condition_counts.get(bike_type, 0)

            # Estimate units to purchase within the budget
            units = min(budget // avg_cost_per_bike, (freq + age_factor + condition_factor))
            total_cost = units * avg_cost_per_bike
            
            # Add to recommendations if within budget
            if budget >= total_cost:
                recommended_purchases.append({
                    'Type': bike_type,
                    'Units': units,
                    'Estimated Cost': total_cost
                })
                budget -= total_cost  # Deduct from the budget

        recommended_purchases_df = pd.DataFrame(recommended_purchases)
        if not recommended_purchases_df.empty:
            print("\nRecommended Purchase Order:")
            print(recommended_purchases_df)
        else:
            print("No recommendations available within your budget.")
        return recommended_purchases_df

    def plot_demand_trends(self):
        """Plots rental frequency and age distribution trends."""
        rental_freq = self.rental_frequency_analysis()
        avg_age = self.age_analysis()

        plt.figure(figsize=(12, 5))

        # Plotting rental frequency
        plt.subplot(1, 2, 1)
        rental_freq.plot(kind='bar', color='skyblue')
        plt.title('Rental Frequency by Bike Type')
        plt.xlabel('Bike Type')
        plt.ylabel('Number of Rentals')

        # Plotting average age
        plt.subplot(1, 2, 2)
        avg_age['Age'].plot(kind='bar', color='salmon')
        plt.title('Average Age by Bike Type')
        plt.xlabel('Bike Type')
        plt.ylabel('Average Age (years)')

        plt.tight_layout()
        plt.show()

# Example usage:
if __name__ == "__main__":
    selector = BikeSelector("Bicycle_Info.txt", "Rental_History.txt")
    selector.plot_demand_trends()
    
    # Recommend purchases based on a budget
    budget = 1000  # Example budget
    selector.recommend_purchases(budget)
