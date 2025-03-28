
import requests
import json
import os
import datetime

from server import app, db
from server.models import BusRouteInfo

DATA_GO_KR_API_KEY = 'QVNQRT5AY8CEBiz4SLIKanU892F4I/kdkF3FmoyQKO+h/O9sz1m5oa3cABQktGyybPJ/UXhDp3hdb5z2c3X8/g=='
SERVICE_KEY = os.getenv('DATA_GO_KR_API_KEY', DATA_GO_KR_API_KEY)
GET_BUS_ROUTE_LIST = 'http://ws.bus.go.kr/api/rest/busRouteInfo/getBusRouteList'

def getBusRouteList(busRouteNm):
        response = requests.get(GET_BUS_ROUTE_LIST, params ={
            'serviceKey' : SERVICE_KEY, 
            'strSrch' : busRouteNm, 
            'resultType' : 'json'
        })

        
        parsed_data = json.loads(response.content)

        msgHeader = parsed_data['msgHeader']
        print(f"응답코드: {msgHeader['headerCd']}")
        if msgHeader['headerCd'] != '0':
            print(f"에러 메시지: {msgHeader['headerMsg']}")
            return None

        for item in parsed_data['msgBody']['itemList']:
            print(f"버스 노선명: {item['busRouteNm']}")
            print(f"출발역: {item['stStationNm']}")
            print(f"도착역: {item['edStationNm']}")
            print(f"운행 거리: {item['length']} km")
            print(f"첫차 시간: {item['firstBusTm']}")
            print(f"막차 시간: {item['lastBusTm']}")
            print(f"회사명: {item['corpNm']}")
            print("-" * 30)
            # 检查是否已经存在相同的 busRouteId
            existing_route = BusRouteInfo.query.filter_by(busRouteId=item['busRouteId']).first()
            if not existing_route:
                # 如果不存在，则添加新条目
                busRouteInfo = BusRouteInfo(
                    busRouteId=item['busRouteId'],
                    busRouteNm=item['busRouteNm'],
                    busRouteAbrv=item['busRouteNm'],
                    length=item['length'],
                    routeType=item['routeType'],
                    stStationNm=item['stStationNm'],
                    edStationNm=item['edStationNm'],
                    term=item['term'],
                    lastBusYn=item['lastBusYn'],
                    lastBusTm=item['lastBusTm'],
                    firstBusTm=item['firstBusTm'],
                    firstLowTm=item['firstLowTm'],
                    lastLowTm=item['lastLowTm'],
                    corpNm=item['corpNm'],
                    createdTm=datetime.datetime.now()
                )
                db.session.add(busRouteInfo)
                db.session.commit()

        busRouteInfoList = BusRouteInfo.query.all()
        return busRouteInfoList
