# 🚲 Bicycle Rental Management System
A comprehensive Python-based system for managing bicycle rentals, inventory tracking, and purchase recommendations.

## Project Overview
This project implements a complete Bicycle Rental Management System for a bike rental store. The system allows store managers to manage bicycle inventory, process rentals and returns, search available bicycles, and generate purchase recommendations based on rental patterns and budget constraints.

## Key Features
- **Bicycle Inventory Management**: Track details including brand, type, frame size, condition, rental rates, and availability status.
- **Member Management**: Verify membership status and rental limits using the `membershipManager` module.
- **Rental Processing**: Handle bicycle checkouts with member validation and availability checks.
- **Return Processing**: Process returns with condition assessment, late fee calculation, and damage tracking.
- **Intelligent Search**: Find bicycles by brand, type, or frame size with current availability information.
- **Purchase Recommendations**: Data-driven suggestions for inventory expansion based on rental patterns and budget.
- **Data Visualization**: Matplotlib-based visualizations for rental trends and inventory analysis.
- **User-Friendly Interface**: Simple GUI built with IPyWidgets in Jupyter Notebook.

## Technical Implementation
- **SQLite database** for persistent data storage.
- **Modular Python design** with specialized components.
- **Data cleaning procedures** for handling inconsistent input data.
- **Object-oriented architecture** for code reusability.
- **Data analysis with Pandas** for inventory optimization.
- **Normalized database schema** (3NF compliant).

## Project Structure
- `menu.ipynb`: Main Jupyter Notebook interface with IPyWidgets GUI.
- `bikeSearch.py`: Module for bicycle search functionality.
- `bikeRent.py`: Module for processing rental transactions.
- `bikeReturn.py`: Module for handling bicycle returns.
- `bikeSelect.py`: Module for purchase recommendations.
- `database.py`: Database interaction and initialization module.
- `BicycleRental.db`: SQLite database.
- `Bicycle_Info.txt & Rental_History.txt`: Initial data files.

## Technologies Used
- Python 3.11
- SQLite
- Jupyter Notebook
- Pandas & Matplotlib
- IPyWidgets

## Academic Context
This project was developed as coursework for 24COP501 - Programming for Specialist Applications, demonstrating proficiency in Python programming, database design, data analysis, and software architecture.

**Note**: This project is an academic exercise and showcase of programming skills.

