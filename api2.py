from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)
DATABASE = 'sales.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    month = request.args.get('month')
    year = request.args.get('year')

    if not month or not year:
        return jsonify({'error': 'Month and year are required parameters'}), 400

    try:
        start_date = datetime.strptime(f'{year}-{month}-01', '%Y-%m-%d')
        end_date = datetime.strptime(f'{year}-{int(month)+1}-01', '%Y-%m-%d')
    except ValueError:
        return jsonify({'error': 'Invalid month or year format'}), 400

    db = get_db()
    cursor = db.cursor()

  
    cursor.execute("""
        SELECT SUM(amount) AS total_sales 
        FROM sales 
        WHERE sold_date >= ? AND sold_date < ? AND sold = 1
    """, (start_date, end_date))
    total_sales = cursor.fetchone()['total_sales'] or 0

  
    cursor.execute("""
        SELECT COUNT(*) AS total_sold 
        FROM sales 
        WHERE sold_date >= ? AND sold_date < ? AND sold = 1
    """, (start_date, end_date))
    total_sold = cursor.fetchone()['total_sold']

   
    cursor.execute("""
        SELECT COUNT(*) AS total_not_sold 
        FROM sales 
        WHERE sold_date >= ? AND sold_date < ? AND sold = 0
    """, (start_date, end_date))
    total_not_sold = cursor.fetchone()['total_not_sold']

    db.close()

    return jsonify({
        'total_sales': total_sales,
        'total_sold': total_sold,
        'total_not_sold': total_not_sold
    })

if __name__ == '__main__':
    app.run(debug=True)
