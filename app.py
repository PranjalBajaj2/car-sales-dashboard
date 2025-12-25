from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
import os

app = Flask(__name__)


MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = os.getenv("DB_NAME", "mydb")

# MongoDB connection
client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# Collections
cars_col = db["Cars"]
dealers_col = db["Dealers"]
services_col = db["Services"]



# Dashboard Home
@app.route('/')
def index():
    
    dealers = list(cars_col.distinct("DealerID"))
    models = list(cars_col.distinct("Model"))
    prices = list(cars_col.distinct("Price"))
    min_price, max_price = (min(prices) if prices else 0, max(prices) if prices else 100000)
    return render_template('index.html', dealers=dealers, models=models, min_price=min_price, max_price=max_price)


@app.route('/get_data', methods=['POST'])
def get_data():
    filters = request.json or {}
    query = {}

    if filters.get('dealer_id'):
        query['DealerID'] = filters['dealer_id']
    if filters.get('model'):
        query['Model'] = filters['model']
    if filters.get('min_price') is not None:
        query['Price'] = query.get('Price', {})
        query['Price']['$gte'] = filters['min_price']
    if filters.get('max_price') is not None:
        query['Price'] = query.get('Price', {})
        query['Price']['$lte'] = filters['max_price']

    data = list(cars_col.find(query, {"_id": 0}))
    return jsonify(data)


@app.route('/get_charts', methods=['POST'])
def get_charts():
    filters = request.json or {}
    query = {}

    if filters.get('dealer_id'):
        query['DealerID'] = filters['dealer_id']
    if filters.get('model'):
        query['Model'] = filters['model']
    if filters.get('min_price') is not None:
        query['Price'] = query.get('Price', {})
        query['Price']['$gte'] = filters['min_price']
    if filters.get('max_price') is not None:
        query['Price'] = query.get('Price', {})
        query['Price']['$lte'] = filters['max_price']

    # Cars per Dealer (Bar chart)
    pipeline_dealer = [
        {"$match": query},
        {"$group": {"_id": "$DealerID", "count": {"$sum": 1}}}
    ]
    dealer_data = list(cars_col.aggregate(pipeline_dealer))

    # Model Distribution (Pie chart)
    pipeline_model = [
        {"$match": query},
        {"$group": {"_id": "$Model", "count": {"$sum": 1}}}
    ]
    model_data = list(cars_col.aggregate(pipeline_model))

    # Service Costs Over Time (Line chart)
    service_query = {}
    if filters.get('dealer_id'):
        dealer_cars = list(cars_col.find({"DealerID": filters['dealer_id']}, {"CarID": 1}))
        car_ids = [c['CarID'] for c in dealer_cars]
        if car_ids:
            service_query['CarID'] = {"$in": car_ids}
    if service_query:
        pipeline_service = [
            {"$match": service_query},
            {"$group": {"_id": "$Date", "total_cost": {"$sum": "$Cost"}}},
            {"$sort": {"_id": 1}}
        ]
        service_data = list(services_col.aggregate(pipeline_service))
    else:
        service_data = []

    return jsonify({
        "dealer": dealer_data,
        "model": model_data,
        "service": service_data
    })


if __name__ == '__main__':
    app.run(debug=True)
