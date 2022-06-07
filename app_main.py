import json
import os
import uuid

from flask_swagger_ui import get_swaggerui_blueprint
from flask import Flask, request, send_from_directory
from flask_restful import Api

from vehicle_card_ocr import scan_vehicle_card
from class_part import Part
from class_vehicle import Vehicle
from data_utils import parse_vehicle_file, find_vehicle, add_new_vehicle, remove_vehicle, update_vehicle_parameters, \
    parse_parts_file, find_part, add_new_part, update_part_parameters, remove_part, get_parts_for_vin, create_order

app = Flask(__name__)

### swagger specific ###
SWAGGER_URL = '/swagger'
API_URL = '/config/swagger.json'
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Vehicle Rest API"
    }
)
app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)
### end swagger specific ###
api = Api(app)


@app.route('/config/<path:path>')
def send_static(path):
    return send_from_directory('config', path)


@app.route("/")
def main_page():
    return "<p>Jesteś na stronie początkowej<p>"


@app.route('/getVehicles', methods=['GET'])
def get_vehicles():
    vehicles = parse_vehicle_file()
    result = [vehicle.to_dict() for vehicle in vehicles]
    return json.dumps(result)


@app.route('/findVehicle', methods=['PUT'])
def find_vehicle_by_vin():
    request_data = request.get_json()
    print(request_data)
    vin = request_data.get('vin')
    vehicle = find_vehicle(vin)
    return json.dumps(vehicle.__dict__)


@app.route('/addVehicle', methods=['PUT'])
def add_vehicles():
    request_data = request.get_json()
    vehicle = Vehicle(str(uuid.uuid4()), request_data.get('make'), request_data.get('model'),
                      request_data.get('model_code'), request_data.get('production_years'), request_data.get('vin_const'),
                      request_data.get('engine'),
                      request_data.get('description'))
    return add_new_vehicle(vehicle)


@app.route('/deleteVehicle', methods=['PUT'])
def delete_vehicle():
    request_data = request.get_json()
    vin = request_data.get('vin')
    return remove_vehicle(vin)


@app.route('/updateVehicleParameter', methods=['PUT'])
def update_vehicle_parameter():
    request_data = request.get_json()
    param_name = request_data.get('param_name')
    param_value = request_data.get('param_value')
    vin = request_data.get('vin')
    update_res = update_vehicle_parameters(param_name, param_value, vin)
    if update_res:
        vehicle = find_vehicle(vin)
        return json.dumps(vehicle.__dict__)
    else:
        return json.dumps("Error")


# Parts endpoints
@app.route('/getParts', methods=['GET'])
def get_parts():
    parts = parse_parts_file()
    result = [part.to_dict() for part in parts]
    return json.dumps(result)


@app.route('/findPart', methods=['PUT'])
def find_part_by_sn():
    request_data = request.get_json()
    sn = request_data.get('sn')
    part = find_part(sn)
    return json.dumps(part.__dict__)


@app.route('/addPart', methods=['PUT'])
def add_part():
    request_data = request.get_json()
    part = Part(str(uuid.uuid4()), request_data.get('name'), request_data.get('sn'), request_data.get('producer'), request_data.get('price'),
                request_data.get('availability'), request_data.get('order_wait_days'))
    return add_new_part(part)


@app.route('/updatePartParameter', methods=['PUT'])
def update_part_parameter():
    request_data = request.get_json()
    param_name = request_data.get('param_name')
    param_value = request_data.get('param_value')
    sn = request_data.get('sn')
    update_res = update_part_parameters(param_name, param_value, sn)
    if update_res:
        part = find_part(sn)
        return json.dumps(part.__dict__)
    else:
        return json.dumps("Error")


@app.route('/deletePart', methods=['PUT'])
def delete_part():
    request_data = request.get_json()
    sn = request_data.get('sn')
    return remove_part(sn)


@app.route('/getPartsMap', methods=['GET'])
def get_parts_map():
    parts_car_map = parse_vehicle_file()
    result = [part_car_map.to_dict() for part_car_map in parts_car_map]
    return json.dumps(result)


@app.route('/getPartsForVin', methods=['PUT'])
def get_matching_parts():
    request_data = request.get_json()
    vin = request_data.get('vin')
    parts = get_parts_for_vin(vin)
    result = [part.to_dict() for part in parts]
    return json.dumps(result)


@app.route('/createOrder', methods=['PUT'])
def place_order():
    request_data = request.get_json()
    vin = request_data.get('vin')
    parts = request_data.get('parts')
    new_order = create_order(vin, parts)
    if new_order is not None:
        return json.dumps(new_order.to_dict())
    else:
        return "Cannot place order"


@app.route('/scanVehicleCard', methods=['PUT'])
def get_vehicle_data_from_vehicle_card():
    request_data = request.get_json()
    url_to_file = request_data.get('url')
    result = scan_vehicle_card(url_to_file)
    if result is not None:
        return json.dumps(result)
    else:
        return "Cannot scan vehicle card"


if __name__ == '__main__':
    # Ustawiam hosta na 0.0.0.0 i mapuje port -> wymaganie aby aplikacja wstała na heroku!!
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
