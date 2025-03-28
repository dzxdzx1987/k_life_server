
import requests
import json
import os
import datetime
import logging

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

        response.raise_for_status()  # raises exception when not a 2xx response
        logging.info(f"HTTP response code: {response.status_code}")
        if response.status_code == 204:
            return None

        parsed_data = json.loads(response.content)
        msgHeader = parsed_data['msgHeader']
        logging.info(f"응답코드: {msgHeader['headerCd']}")
        if msgHeader['headerCd'] != '0':
            logging.info(f"에러 메시지: {msgHeader['headerMsg']}")
            return None

        for item in parsed_data['msgBody']['itemList']:
            logging.info(f"버스 노선 ID: {item['busRouteId']}")
            logging.info(f"버스 노선명: {item['busRouteNm']}")
            logging.info(f"출발역: {item['stStationNm']}")
            logging.info(f"도착역: {item['edStationNm']}")
            logging.info(f"운행 거리: {item['length']} km")
            logging.info(f"첫차 시간: {item['firstBusTm']}")
            logging.info(f"막차 시간: {item['lastBusTm']}")
            logging.info(f"회사명: {item['corpNm']}")
            logging.info("-" * 30)
            # 检查是否已经存在相同的 busRouteId
            existing_route = BusRouteInfo.query.filter_by(busRouteId=item['busRouteId']).first()
            logging.info(f"existing_route: {existing_route}")
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
