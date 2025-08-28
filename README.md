# Bicycle Rental Management System

A comprehensive Python-based system for managing bicycle rentals, memberships, and inventory tracking.

## 🚲 Features

- **Bicycle Management**: Add, search, and track bicycle inventory
- **Member Management**: Handle member registrations and rental limits
- **Rental Operations**: Process bike rentals and returns
- **Search & Filter**: Advanced search functionality with multiple criteria
- **Database Management**: SQLite-based data persistence
- **Interactive Interface**: Jupyter Notebook-based user interface
- **Transaction Logging**: Comprehensive rental history tracking

## 📁 Project Structure

```
BicycleRentalManagementSystem/
├── database.py              # Database management and operations
├── bikeRent.py             # Bike rental functionality
├── bikeReturn.py           # Bike return processing
├── bikeSearch.py           # Search and filter bicycles
├── bikeSelect.py           # Bicycle selection interface
├── menu.ipynb              # Main interactive interface
├── Bicycle_Info.txt        # Sample bicycle data
├── Rental_History.txt      # Sample rental history
├── members.txt             # Sample member data
└── BicycleRental.db       # SQLite database (auto-generated)
```

## 🛠️ Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Setup
1. Clone the repository:
   ```bash
   git clone <your-repository-url>
   cd BICYCLERENTALMANAGEMENTSYSTEM
   ```

2. Install required dependencies:
   ```bash
   pip install ipywidgets jupyter sqlite3
   ```

3. Run the system:
   ```bash
   jupyter notebook BicycleRentalManagementSystem/menu.ipynb
   ```

## 🚀 Usage

### Starting the System
1. Navigate to the project directory
2. Run `jupyter notebook` or open `menu.ipynb` in Jupyter
3. Execute the cells to initialize the system

### Main Functions

#### Search for Bicycles
- Use the search interface to find available bicycles
- Filter by brand, type, status, condition, and rental rate
- Sort results by various criteria

#### Rent a Bicycle
- Enter Member ID and Bicycle ID
- System validates membership and availability
- Automatic rental period calculation (7 days default)

#### Return a Bicycle
- Process bicycle returns
- Calculate any late fees or damage charges
- Update inventory status

#### Manage Inventory
- View all bicycles in the system
- Check rental status and condition
- Monitor rental history

## 🗄️ Database Schema

### Tables
- **bicycles**: Bicycle inventory information
- **members**: Member details and rental limits
- **rental_transactions**: Rental history and dates
- **rental_fees**: Additional charges and fees

### Key Fields
- Bicycle ID, Brand, Type, Frame Size
- Rental Rate, Purchase Date, Condition, Status
- Member ID, Rental Limit, Membership End Date
- Transaction tracking with dates and fees

## 🔧 Configuration

### Database Settings
- Default database: `BicycleRental.db`
- Auto-created tables on first run
- Data loaded from text files on initialization

### Rental Policies
- Default rental period: 7 days
- Configurable rental limits per membership
- Automatic status updates

## 📊 Sample Data

The system includes sample data files:
- **Bicycle_Info.txt**: Sample bicycle inventory
- **Rental_History.txt**: Sample rental transactions
- **members.txt**: Sample member information

## 🐛 Troubleshooting

### Common Issues
1. **Database Connection Errors**: Ensure write permissions in the project directory
2. **Import Errors**: Check that all Python files are in the same directory
3. **File Not Found**: Verify data files are present in the correct location

### Logs
- Check `database_manager.log` for database operations
- Review `bike_return.log` for return processing issues

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 👨‍💻 Author

Created as part of a bicycle rental management system project.

## 📞 Support

For questions or issues, please open an issue in the GitHub repository.

---

**Note**: This is a development project. For production use, additional security measures and error handling should be implemented. 