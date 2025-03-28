from flask import jsonify

from server import app, db
from server.models import User, Movie, BusRouteInfo

@app.route('/api/queryBusRouteList', methods=['GET'])
def queryBusRouteList():
    busRouteInfoList = BusRouteInfo.query.all()

    # Convert the list of BusRouteInfo objects to a list of dictionaries
    busRouteInfoList_json = [
        {
            'busRouteId': route.busRouteId,
            'busRouteNm': route.busRouteNm,
            'stStationNm': route.stStationNm,
            'edStationNm': route.edStationNm,
            'length': route.length,
            'firstBusTm': route.firstBusTm,
            'lastBusTm': route.lastBusTm,
            'corpNm': route.corpNm
        }
        for route in busRouteInfoList
    ]

    # Return the JSON response
    return jsonify(busRouteInfoList_json)