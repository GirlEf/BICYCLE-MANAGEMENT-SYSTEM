#!/usr/bin/env python3
"""
Flask Web Application for Bicycle Rental Management System
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash  # pyright: ignore[reportMissingImports]
from flask_sqlalchemy import SQLAlchemy  # pyright: ignore[reportMissingImports]
import os
import sys
from datetime import datetime, timedelta

# Add the BicycleRentalManagementSystem directory to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
bicycle_dir = os.path.join(current_dir, 'BicycleRentalManagementSystem')
sys.path.insert(0, bicycle_dir)

try:
    from database import DatabaseManager
    from bikeSearch import BicycleSearch
    from bikeRent import BikeRentSystem, RentalTransactionManager
    from bikeReturn import BikeReturn
    print(f"✅ Successfully imported modules from {bicycle_dir}")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Python path: {sys.path}")
    sys.exit(1)

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production

# Initialize database
db_manager = DatabaseManager()
search_manager = BicycleSearch(db_manager)
rental_system = BikeRentSystem()
return_system = BikeReturn(db_manager)

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
def search():
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
def rent():
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
def returns():
    """Process returns page"""
    return render_template('returns.html')

@app.route('/members')
def members():
    """Members management page"""
    return render_template('members.html')

@app.route('/reports')
def reports():
    """Reports and analytics page"""
    return render_template('reports.html')

@app.route('/api/analytics/overview')
def analytics_overview():
    """Get overview analytics data"""
    try:
        db_manager.connect()
        cursor = db_manager.connection.cursor()
        
        # Get total bicycles
        cursor.execute("SELECT COUNT(*) FROM bicycles")
        total_bikes = cursor.fetchone()[0]
        
        # Get available bicycles
        cursor.execute("SELECT COUNT(*) FROM bicycles WHERE STATUS = 'Available'")
        available_bikes = cursor.fetchone()[0]
        
        # Get rented bicycles
        cursor.execute("SELECT COUNT(*) FROM bicycles WHERE STATUS = 'Rented'")
        rented_bikes = cursor.fetchone()[0]
        
        # Get maintenance bicycles
        cursor.execute("SELECT COUNT(*) FROM bicycles WHERE STATUS = 'Maintenance'")
        maintenance_bikes = cursor.fetchone()[0]
        
        # Get total members
        cursor.execute("SELECT COUNT(*) FROM members")
        total_members = cursor.fetchone()[0]
        
        # Get total rentals
        cursor.execute("SELECT COUNT(*) FROM rental_transactions")
        total_rentals = cursor.fetchone()[0]
        
        # Get active rentals
        cursor.execute("SELECT COUNT(*) FROM rental_transactions WHERE RETURN_DATE IS NULL")
        active_rentals = cursor.fetchone()[0]
        
        # Get total revenue (from rental_fees if table exists)
        try:
            cursor.execute("SELECT SUM(LATE_FEE + DAMAGE_FEE) FROM rental_fees")
            total_revenue = cursor.fetchone()[0] or 0
        except:
            total_revenue = 0
        
        return jsonify({
            'success': True,
            'data': {
                'total_bikes': total_bikes,
                'available_bikes': available_bikes,
                'rented_bikes': rented_bikes,
                'maintenance_bikes': maintenance_bikes,
                'total_members': total_members,
                'total_rentals': total_rentals,
                'active_rentals': active_rentals,
                'total_revenue': total_revenue
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        db_manager.close()

@app.route('/api/analytics/rental-trends')
def rental_trends():
    """Get rental trends data"""
    try:
        db_manager.connect()
        cursor = db_manager.connection.cursor()
        
        # Get rentals by month for the last 12 months
        cursor.execute("""
            SELECT strftime('%Y-%m', RENTAL_DATE) as month, COUNT(*) as count
            FROM rental_transactions 
            WHERE RENTAL_DATE >= date('now', '-12 months')
            GROUP BY month 
            ORDER BY month
        """)
        
        monthly_rentals = cursor.fetchall()
        
        # Get popular bicycle types
        cursor.execute("""
            SELECT b.TYPE, COUNT(*) as count
            FROM rental_transactions rt
            JOIN bicycles b ON rt.BICYCLE_ID = b.ID
            GROUP BY b.TYPE
            ORDER BY count DESC
            LIMIT 5
        """)
        
        popular_types = cursor.fetchall()
        
        # Get popular brands
        cursor.execute("""
            SELECT b.BRAND, COUNT(*) as count
            FROM rental_transactions rt
            JOIN bicycles b ON rt.BICYCLE_ID = b.ID
            GROUP BY b.BRAND
            ORDER BY count DESC
            LIMIT 5
        """)
        
        popular_brands = cursor.fetchall()
        
        return jsonify({
            'success': True,
            'data': {
                'monthly_rentals': monthly_rentals,
                'popular_types': popular_types,
                'popular_brands': popular_brands
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        db_manager.close()

@app.route('/api/analytics/revenue')
def revenue_analytics():
    """Get revenue analytics data"""
    try:
        db_manager.connect()
        cursor = db_manager.connection.cursor()
        
        # Get monthly revenue
        cursor.execute("""
            SELECT strftime('%Y-%m', rt.RENTAL_DATE) as month, 
                   SUM(COALESCE(rf.LATE_FEE, 0) + COALESCE(rf.DAMAGE_FEE, 0)) as revenue
            FROM rental_transactions rt
            LEFT JOIN rental_fees rf ON rt.TRANSACTION_ID = rf.TRANSACTION_ID
            WHERE rt.RENTAL_DATE >= date('now', '-12 months')
            GROUP BY month 
            ORDER BY month
        """)
        
        monthly_revenue = cursor.fetchall()
        
        # Get revenue by fee type
        cursor.execute("""
            SELECT 'Late Fees' as type, SUM(LATE_FEE) as amount FROM rental_fees WHERE LATE_FEE > 0
            UNION ALL
            SELECT 'Damage Fees' as type, SUM(DAMAGE_FEE) as amount FROM rental_fees WHERE DAMAGE_FEE > 0
        """)
        
        fee_breakdown = cursor.fetchall()
        
        return jsonify({
            'success': True,
            'data': {
                'monthly_revenue': monthly_revenue,
                'fee_breakdown': fee_breakdown
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        db_manager.close()

@app.route('/api/analytics/inventory')
def inventory_analytics():
    """Get inventory analytics data"""
    try:
        db_manager.connect()
        cursor = db_manager.connection.cursor()
        
        # Get bicycles by condition
        cursor.execute("""
            SELECT CONDITION, COUNT(*) as count
            FROM bicycles
            GROUP BY CONDITION
            ORDER BY count DESC
        """)
        
        condition_distribution = cursor.fetchall()
        
        # Get bicycles by type
        cursor.execute("""
            SELECT TYPE, COUNT(*) as count
            FROM bicycles
            GROUP BY TYPE
            ORDER BY count DESC
        """)
        
        type_distribution = cursor.fetchall()
        
        # Get bicycles by brand
        cursor.execute("""
            SELECT BRAND, COUNT(*) as count
            FROM bicycles
            GROUP BY BRAND
            ORDER BY count DESC
        """)
        
        brand_distribution = cursor.fetchall()
        
        # Get rental frequency by bicycle
        cursor.execute("""
            SELECT b.ID, b.BRAND, b.TYPE, COUNT(rt.TRANSACTION_ID) as rental_count
            FROM bicycles b
            LEFT JOIN rental_transactions rt ON b.ID = rt.BICYCLE_ID
            GROUP BY b.ID, b.BRAND, b.TYPE
            ORDER BY rental_count DESC
            LIMIT 10
        """)
        
        rental_frequency = cursor.fetchall()
        
        return jsonify({
            'success': True,
            'data': {
                'condition_distribution': condition_distribution,
                'type_distribution': type_distribution,
                'brand_distribution': brand_distribution,
                'rental_frequency': rental_frequency
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        db_manager.close()

@app.route('/api/analytics/advanced')
def advanced_analytics():
    """Get advanced analytics including heatmaps and scatter plots"""
    try:
        db_manager.connect()
        cursor = db_manager.connection.cursor()
        
        # Get rental heatmap data (day of week vs hour)
        cursor.execute("""
            SELECT 
                strftime('%w', RENTAL_DATE) as day_of_week,
                strftime('%H', RENTAL_DATE) as hour,
                COUNT(*) as count
            FROM rental_transactions 
            WHERE RENTAL_DATE >= date('now', '-30 days')
            GROUP BY day_of_week, hour
            ORDER BY day_of_week, hour
        """)
        
        heatmap_data = cursor.fetchall()
        
        # Get rental duration vs revenue scatter data
        cursor.execute("""
            SELECT 
                CASE 
                    WHEN rt.RETURN_DATE IS NOT NULL 
                    THEN julianday(rt.RETURN_DATE) - julianday(rt.RENTAL_DATE)
                    ELSE julianday('now') - julianday(rt.RENTAL_DATE)
                END as duration_days,
                COALESCE(rf.LATE_FEE, 0) + COALESCE(rf.DAMAGE_FEE, 0) as total_fees
            FROM rental_transactions rt
            LEFT JOIN rental_fees rf ON rt.TRANSACTION_ID = rf.TRANSACTION_ID
            WHERE rt.RENTAL_DATE >= date('now', '-90 days')
        """)
        
        scatter_data = cursor.fetchall()
        
        return jsonify({
            'success': True,
            'data': {
                'heatmap_data': heatmap_data,
                'scatter_data': scatter_data
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        db_manager.close()

@app.route('/api/analytics/predictive')
def predictive_analytics():
    """Get predictive analytics data"""
    try:
        db_manager.connect()
        cursor = db_manager.connection.cursor()
        
        # Get demand forecast (simple trend-based prediction)
        cursor.execute("""
            SELECT 
                strftime('%Y-%m-%d', date('now', '+' || (rowid-1) || ' days')) as forecast_date,
                CASE 
                    WHEN strftime('%w', date('now', '+' || (rowid-1) || ' days')) IN ('0', '6') 
                    THEN 8  -- Weekend peak
                    ELSE 5  -- Weekday average
                END as predicted_rentals
            FROM (SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9 UNION SELECT 10 UNION SELECT 11 UNION SELECT 12 UNION SELECT 13 UNION SELECT 14 UNION SELECT 15 UNION SELECT 16 UNION SELECT 17 UNION SELECT 18 UNION SELECT 19 UNION SELECT 20 UNION SELECT 21 UNION SELECT 22 UNION SELECT 23 UNION SELECT 24 UNION SELECT 25 UNION SELECT 26 UNION SELECT 27 UNION SELECT 28 UNION SELECT 29 UNION SELECT 30)
            LIMIT 30
        """)
        
        demand_forecast = cursor.fetchall()
        
        # Get maintenance forecast
        cursor.execute("""
            SELECT 
                b.ID,
                b.BRAND,
                b.TYPE,
                b.CONDITION,
                COUNT(rt.TRANSACTION_ID) as rental_count,
                CASE 
                    WHEN b.CONDITION = 'New' THEN 50
                    WHEN b.CONDITION = 'Good' THEN 30
                    WHEN b.CONDITION = 'Fair' THEN 15
                    ELSE 5
                END - COUNT(rt.TRANSACTION_ID) as rentals_until_maintenance
            FROM bicycles b
            LEFT JOIN rental_transactions rt ON b.ID = rt.BICYCLE_ID
            GROUP BY b.ID, b.BRAND, b.TYPE, b.CONDITION
            HAVING rentals_until_maintenance <= 10
            ORDER BY rentals_until_maintenance ASC
        """)
        
        maintenance_forecast = cursor.fetchall()
        
        return jsonify({
            'success': True,
            'data': {
                'demand_forecast': demand_forecast,
                'maintenance_forecast': maintenance_forecast
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        db_manager.close()

@app.route('/api/analytics/filtered')
def filtered_analytics():
    """Get filtered analytics based on user criteria"""
    try:
        data = request.args
        date_range = data.get('date_range', '30')
        bike_category = data.get('bike_category', '')
        member_type = data.get('member_type', '')
        
        db_manager.connect()
        cursor = db_manager.connection.cursor()
        
        # Build dynamic query based on filters
        where_clause = "WHERE rt.RENTAL_DATE >= date('now', '-" + str(date_range) + " days')"
        
        if bike_category:
            where_clause += " AND b.TYPE = '" + bike_category + "'"
        
        # Get filtered rental data
        query = f"""
            SELECT 
                strftime('%Y-%m-%d', rt.RENTAL_DATE) as rental_date,
                COUNT(*) as rental_count,
                AVG(COALESCE(rf.LATE_FEE, 0) + COALESCE(rf.DAMAGE_FEE, 0)) as avg_revenue
            FROM rental_transactions rt
            JOIN bicycles b ON rt.BICYCLE_ID = b.ID
            LEFT JOIN rental_fees rf ON rt.TRANSACTION_ID = rf.TRANSACTION_ID
            {where_clause}
            GROUP BY rental_date
            ORDER BY rental_date
        """
        
        cursor.execute(query)
        filtered_data = cursor.fetchall()
        
        return jsonify({
            'success': True,
            'data': filtered_data,
            'filters_applied': {
                'date_range': date_range,
                'bike_category': bike_category,
                'member_type': member_type
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        db_manager.close()

@app.route('/api/export/report')
def export_report():
    """Export analytics report in various formats"""
    try:
        data = request.args
        report_type = data.get('type', 'overview')
        export_format = data.get('format', 'pdf')
        template = data.get('template', 'standard')
        include_charts = data.get('include_charts', 'true').lower() == 'true'
        granularity = data.get('granularity', 'detailed')
        
        # Get the appropriate data based on report type
        if report_type == 'overview':
            report_data = get_overview_data()
        elif report_type == 'rentals':
            report_data = get_rental_data()
        elif report_type == 'inventory':
            report_data = get_inventory_data()
        elif report_type == 'revenue':
            report_data = get_revenue_data()
        else:
            report_data = get_overview_data()
        
        # Generate export based on format
        if export_format == 'csv':
            return generate_csv_export(report_data, report_type)
        elif export_format == 'json':
            return generate_json_export(report_data, report_type)
        elif export_format == 'excel':
            return generate_excel_export(report_data, report_type)
        else:  # PDF
            return generate_pdf_export(report_data, report_type, template, include_charts)
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

def get_overview_data():
    """Get overview data for export"""
    db_manager.connect()
    cursor = db_manager.connection.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM bicycles")
    total_bikes = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM members")
    total_members = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM rental_transactions")
    total_rentals = cursor.fetchone()[0]
    
    db_manager.close()
    
    return {
        'total_bikes': total_bikes,
        'total_members': total_members,
        'total_rentals': total_rentals
    }

def get_rental_data():
    """Get rental data for export"""
    db_manager.connect()
    cursor = db_manager.connection.cursor()
    
    cursor.execute("""
        SELECT rt.RENTAL_DATE, rt.BICYCLE_ID, rt.MEMBER_ID, b.BRAND, b.TYPE
        FROM rental_transactions rt
        JOIN bicycles b ON rt.BICYCLE_ID = b.ID
        ORDER BY rt.RENTAL_DATE DESC
        LIMIT 100
    """)
    
    rentals = cursor.fetchall()
    db_manager.close()
    
    return {'rentals': rentals}

def get_inventory_data():
    """Get inventory data for export"""
    db_manager.connect()
    cursor = db_manager.connection.cursor()
    
    cursor.execute("SELECT ID, BRAND, TYPE, CONDITION, STATUS FROM bicycles")
    inventory = cursor.fetchall()
    
    db_manager.close()
    
    return {'inventory': inventory}

def get_revenue_data():
    """Get revenue data for export"""
    db_manager.connect()
    cursor = db_manager.connection.cursor()
    
    cursor.execute("""
        SELECT rt.RENTAL_DATE, COALESCE(rf.LATE_FEE, 0) as late_fee, 
               COALESCE(rf.DAMAGE_FEE, 0) as damage_fee
        FROM rental_transactions rt
        LEFT JOIN rental_fees rf ON rt.TRANSACTION_ID = rf.TRANSACTION_ID
        ORDER BY rt.RENTAL_DATE DESC
    """)
    
    revenue = cursor.fetchall()
    db_manager.close()
    
    return {'revenue': revenue}

def generate_csv_export(data, report_type):
    """Generate CSV export"""
    import csv
    from io import StringIO
    
    output = StringIO()
    writer = csv.writer(output)
    
    if report_type == 'overview':
        writer.writerow(['Metric', 'Value'])
        for key, value in data.items():
            writer.writerow([key.replace('_', ' ').title(), value])
    elif report_type == 'rentals':
        writer.writerow(['Rental Date', 'Bicycle ID', 'Member ID', 'Brand', 'Type'])
        for rental in data['rentals']:
            writer.writerow(rental)
    
    output.seek(0)
    
    from flask import Response
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename={report_type}_report.csv'}
    )

def generate_json_export(data, report_type):
    """Generate JSON export"""
    return jsonify({
        'success': True,
        'report_type': report_type,
        'data': data,
        'exported_at': datetime.now().isoformat()
    })

def generate_excel_export(data, report_type):
    """Generate Excel export (placeholder)"""
    return jsonify({
        'success': True,
        'message': f'Excel export for {report_type} report',
        'note': 'Excel export functionality requires additional libraries (openpyxl)'
    })

def generate_pdf_export(data, report_type, template, include_charts):
    """Generate PDF export (placeholder)"""
    return jsonify({
        'success': True,
        'message': f'PDF export for {report_type} report',
        'note': 'PDF export functionality requires additional libraries (reportlab)'
    })

if __name__ == '__main__':
    # Ensure database is populated
    db_manager.populate_bicycles()
    db_manager.populate_members()
    
    print("Starting Bicycle Rental Management System...")
    print("Open your browser and go to: http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000) 