#!/usr/bin/env python3
"""
Flask Web Application for Bicycle Rental Management System
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import os
import sys
from datetime import datetime, timedelta

# Add the BicycleRentalManagementSystem directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'BicycleRentalManagementSystem'))

from database import DatabaseManager
from bikeSearch import BicycleSearch
from bikeRent import BikeRentSystem, RentalTransactionManager

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production

# Initialize database
db_manager = DatabaseManager()
search_manager = BicycleSearch(db_manager)
rental_system = BikeRentSystem()

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/bicycles')
def bicycles():
    """Display all bicycles"""
    try:
        bicycles = search_manager.list_all_bicycles()
        return render_template('bicycles.html', bicycles=bicycles)
    except Exception as e:
        flash(f'Error loading bicycles: {str(e)}', 'error')
        return render_template('bicycles.html', bicycles=[])

@app.route('/search')
def search_page():
    """Search bicycles page"""
    return render_template('search.html')

@app.route('/api/search', methods=['POST'])
def search_bicycles():
    """API endpoint for searching bicycles"""
    try:
        data = request.get_json()
        brand = data.get('brand', '').strip()
        bike_type = data.get('type', '').strip()
        status = data.get('status', 'Available')
        condition = data.get('condition', '').strip()
        min_rate = data.get('min_rate')
        max_rate = data.get('max_rate')
        sort_by = data.get('sort_by')

        # Convert rates to integers if provided
        if min_rate:
            min_rate = int(min_rate)
        if max_rate:
            max_rate = int(max_rate)

        # Perform search using the existing search functionality
        search_manager.search_bicycles(
            brand=brand or None,
            bike_type=bike_type or None,
            status=status,
            condition=condition or None,
            min_rate=min_rate,
            max_rate=max_rate,
            sort_by=sort_by
        )

        # Get results from the search
        results = search_manager.list_all_bicycles()
        
        # Filter results based on search criteria
        filtered_results = []
        for bike in results:
            if brand and brand.lower() not in bike['BRAND'].lower():
                continue
            if bike_type and bike_type.lower() not in bike['TYPE'].lower():
                continue
            if condition and bike['CONDITION'].lower() != condition.lower():
                continue
            if min_rate is not None:
                try:
                    rate = int(bike['RENTAL_RATE'].split('/')[0])
                    if rate < min_rate:
                        continue
                except:
                    pass
            if max_rate is not None:
                try:
                    rate = int(bike['RENTAL_RATE'].split('/')[0])
                    if rate > max_rate:
                        continue
                except:
                    pass
            filtered_results.append(bike)

        return jsonify({'success': True, 'bicycles': filtered_results})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/rent')
def rent_page():
    """Rent a bicycle page"""
    return render_template('rent.html')

@app.route('/api/rent', methods=['POST'])
def rent_bicycle():
    """API endpoint for renting a bicycle"""
    try:
        data = request.get_json()
        member_id = int(data.get('member_id'))
        bicycle_id = int(data.get('bicycle_id'))

        # Validate member
        is_valid_member, member_message = rental_system.validate_member(member_id)
        if not is_valid_member:
            return jsonify({'success': False, 'error': member_message})

        # Validate bicycle
        is_available, bike_message = rental_system.validate_bicycle(bicycle_id)
        if not is_available:
            return jsonify({'success': False, 'error': bike_message})

        # Process rental
        rental_date = datetime.now().strftime("%Y-%m-%d")
        expected_return_date = rental_system.calculate_expected_return_date()
        
        rental_system.rental_manager.log_rental_transaction(
            bicycle_id, member_id, rental_date, expected_return_date
        )

        return jsonify({
            'success': True,
            'message': f'Rental confirmed for Bicycle ID {bicycle_id} by Member ID {member_id}. Expected return date: {expected_return_date}.'
        })

    except ValueError:
        return jsonify({'success': False, 'error': 'Invalid input. Please enter numeric values for Member ID and Bicycle ID.'})
    except Exception as e:
        return jsonify({'success': False, 'error': f'An error occurred while processing the rental: {str(e)}'})

@app.route('/returns')
def returns_page():
    """Process returns page"""
    return render_template('returns.html')

@app.route('/members')
def members_page():
    """Members management page"""
    return render_template('members.html')

@app.route('/reports')
def reports_page():
    """Reports and analytics page"""
    return render_template('reports.html')

if __name__ == '__main__':
    # Ensure database is populated
    db_manager.populate_bicycles()
    db_manager.populate_members()
    
    print("Starting Bicycle Rental Management System...")
    print("Open your browser and go to: http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000) 