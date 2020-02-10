#!flask/bin/python
import os
import json
import urllib.request

from flask import request, g, abort
from flask_api import FlaskAPI
from flask_sqlalchemy import SQLAlchemy
from passlib.apps import custom_app_context as pwd_context
from flask_httpauth import HTTPBasicAuth
from flask_caching import Cache

app = FlaskAPI(__name__)
app.config.from_object('config')
cache = Cache(app)

db = SQLAlchemy(app)
auth = HTTPBasicAuth()


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True)
    password_hash = db.Column(db.String(128))

    def __init__(self, username, password):
        self.username = username
        self.hash_password(password)

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)


def cloud_coverage_desc(cc):  # change percentage cloud coverage to description
    if cc <= 10:
        return 'clear sky'
    if cc <= 36:
        return 'few clouds'
    if cc <= 60:
        return 'scattered clouds'
    if cc <= 84:
        return 'broken clouds'
    else:
        return 'overcast'


def temperature_unit(unit):  # convert unit to openWeatherMap data
    if unit == 'C':
        return 'metric'
    if unit == 'F':
        return 'imperial'
    if unit == 'K':
        return 'standard'
    else:
        return 'error'


def pressure_unit_converter(unit, value):
    if unit == 'atm':
        return value * 0.0009869
    if unit == 'bar':
        return value * 0.001
    if unit == 'torr' or unit == 'mmHg':
        return value * 0.75
    if unit == 'hPa':
        return value
    else:
        return 'error'


@app.route('/ping', methods=['GET'])  # Request to make sure the server is up
def get_ping():
    ping_data = {
        "name": "weatherservice",
        "status": "ok",
        "version": "1.0.0"
    }
    return ping_data


@app.route('/users/new', methods=['POST'])  # creating new user
def new_user():
    try:
        username = request.json.get('username')
        password = request.json.get('password')
        if username is None or password is None:
            return {
                       'error': 'user name or password is not provided',
                       'error_code': 'invalid parameters'
                   }, 400
        if User.query.filter_by(username=username).first() is not None:
            return {
                       'error': 'user name already exist',
                       'error_code': 'invalid parameters'
                   }, 400
        user = User(username, password)
        db.session.add(user)
        db.session.commit()
        return {'created username': user.username}, 201
    except:
        return not_found_error('')


@app.route('/users')  # listing all users in database
def get_users():
    users = User.query.order_by(User.username).all()
    users_json = {}
    for index, user in enumerate(users):
        users_json['user ' + str(index)] = user.username
    return users_json


@app.route('/forecast', methods=['GET'])  # Resolving request when no city is provided
@auth.login_required
def get_no_city():
    return {
               "error": "no city provided",
               "error_code": "invalid request"
           }, 400


@app.route('/forecast/<city>', methods=['GET'])  # Getting weather data for specific city
@auth.login_required
@cache.cached(timeout=30, query_string=True)  # caching function, url parameters also in consideration
def get_forecast(city):
    incorrect_unit_error = {
                               "error": "Incorrect unit symbol",
                               "error_code": "invalid request"
                           }, 400

    open_weather_map_KEY = app.config['API_KEY']

    # Unit requests for temperature || ?temp=C,F,K || Incorrect unit gives error
    temp_symbol = request.args.get('temp', 'C')
    unit_temp = temperature_unit(temp_symbol)
    if unit_temp == 'error':
        return incorrect_unit_error

    # Unit requests for pressure || ?pres=hPa,Bar,
    pres_symbol = request.args.get('pres', 'hPa')

    try:
        with urllib.request.urlopen(
                "https://api.openweathermap.org/data/2.5/weather?q=" + city +
                "&units=" + unit_temp +
                "&APPID=" + open_weather_map_KEY) as url:

            data = json.loads(url.read().decode())
            req = {}

            # parse data
            cloud_coverage = data['clouds']['all']
            cc = cloud_coverage_desc(cloud_coverage)
            req['clouds'] = cc

            humidity = data['main']['humidity']
            req['humidity'] = str(humidity) + '%'

            pressure = data['main']['pressure']
            pressure = pressure_unit_converter(pres_symbol, pressure)
            if pressure == 'error':
                return incorrect_unit_error
            req['pressure'] = str(round(pressure, 4)) + pres_symbol

            temp = data['main']['temp']
            req['temperature'] = str(temp) + temp_symbol

            return req
    except Exception as err:
        if err.code == 404:
            return {"error": "Cannot find country \'" + city + "\'", "error_code": "country not found"}, 404


@auth.verify_password
def verify_password(username, password):
    user = User.query.filter_by(username=username).first()
    if not user or not user.verify_password(password):
        return abort(401)
    g.user = user
    return True


@app.errorhandler(400)
def not_found_error(error):
    return {
               "error": "Invalid request",
               "error_code": "invalid request"
           }, 400


@app.errorhandler(401)
def unauthorized_access(error):
    return {
               "error": "You do not have access to this request",
               "error_code": "unauthorized access"
           }, 401


@app.errorhandler(404)
def bad_request_error(error):
    return {
               "error": "Request not found'",
               "error_code": "request not found"
           }, 404


@app.errorhandler(500)
def internal_error(error):
    return {
               "error": "Something went wrong",
               "error_code": "internal server error"
           }, 500


if __name__ == "__main__":
    if not os.path.exists('db.sqlite'):
        db.create_all()
    admin = User('admin', app.config['ADMIN_PASSWORD'])  # For testing purposes
    db.session.add(admin)
    db.session.commit()
    cache.init_app(app, config={'CACHE_TYPE': 'simple'})
    app.run(host=app.config['HOST'], port=app.config['PORT'])
