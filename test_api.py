import unittest
import json
import requests

from api import app, db, os


class Test(unittest.TestCase):

    def setUp(self):
        # creates a test client
        self.app = app.test_client()
        # propagate the exceptions to the test client
        self.app.testing = True

        self.test_user = ('admin', 'secret')  # creating admin user for testing
        self.test_url = 'http://0.0.0.0:5000'
        if not os.path.exists('db.sqlite'):
            db.create_all()

    def test_up_n_running(self):
        result = self.app.get('/ping')
        self.assertEqual(result.status, '200 OK')
        result_status = json.loads(result.data)
        self.assertEqual(result_status['status'], 'ok')

    def test_404(self):
        result = self.app.get('/someinvalidinput')
        self.assertEqual(result.status, '404 NOT FOUND')

    def test_no_city(self):
        result = requests.get(self.test_url + '/forecast', auth=self.test_user)
        self.assertEqual(result.status_code, 400)

    def test_london(self):
        result = requests.get(self.test_url + '/forecast/london', auth=self.test_user)
        self.assertEqual(result.status_code, 200)

    def test_pressure_bar(self):
        result = requests.get(self.test_url + '/forecast/london?pres=bar', auth=self.test_user)
        self.assertEqual(result.status_code, 200)

    def test_pressure_hPa(self):
        result = requests.get(self.test_url + '/forecast/london?pres=hPa', auth=self.test_user)
        self.assertEqual(result.status_code, 200)

    def test_pressure_atm(self):
        result = requests.get(self.test_url + '/forecast/london?pres=atm', auth=self.test_user)
        self.assertEqual(result.status_code, 200)

    def test_pressure_null(self):
        result = requests.get(self.test_url + '/forecast/london?pres=', auth=self.test_user)
        self.assertEqual(result.status_code, 400)

    def test_pressure_inc(self):
        result = requests.get(self.test_url + '/forecast/london?pres=someincorrectunit', auth=self.test_user)
        self.assertEqual(result.status_code, 400)

    def test_temp_F(self):
        result = requests.get(self.test_url + '/forecast/london?temp=F', auth=self.test_user)
        self.assertEqual(result.status_code, 200)

    def test_temp_inc(self):
        result = requests.get(self.test_url + '/forecast/london?temp=someincorrectunit', auth=self.test_user)
        self.assertEqual(result.status_code, 400)

    def test_temp_null(self):
        result = requests.get(self.test_url + '/forecast/london?temp=', auth=self.test_user)
        self.assertEqual(result.status_code, 400)

    def test_get_users(self):
        result = self.app.get('users')
        self.assertEqual(result.status, '200 OK')

    def test_create_user(self):
        result = requests.post(self.test_url + '/users/new', json={'username': 'dummy', 'password': 'not so secret'})
        self.assertEqual(result.status_code, 201)