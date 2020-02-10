# Weather-Service
Weather API

## Getting Started

### Prerequisites
To run this service you have to have installed Docker.
(https://www.docker.com/)

### Installition
After cloning execute this:

```
macbook$ docker build -t api:latest .
```

### Running

To run the server use the following command:

```
macbook$ docker run -it -p 8080:8080 api
```

Then from a different terminal window you can send requests.

## API Documentation

- GET **/ping**

    Run this in order to check the server is up and running

- GET **/forecast/\<city\>**
  
    Get forecast for the specified \<city\>.
    
    Parameters:
    
      * temp = F(Fahrenheit), C(Celcius), K(Kelvin)
      
      * pres = atm, torr, hPa, bar
  
- POST **/users/new**

    Create new user.</br>
    The body must contain a JSON object with username and password.

- GET **/users**

    List all existing users
  
  
## Examples

Check the server status

```
$ curl -si http://localhost:8080/ping
```

```json
HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 62

{
    "name": "weatherservice", 
    "status": "ok", 
    "version": "1.0.0"
}
```

Get forecast for London with specified temperature and pressure units

```
curl -si -u admin:secret  'http://localhost:8080/forecast/london?temp=F&pres=torr'
```
```json
HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 96

{
    "clouds": "broken clouds", 
    "humidity": "61%", 
    "pressure": "748.5torr", 
    "temperature": "46.63F"
}
```

Creating new user

```
curl -i -X POST -H "Content-Type: application/json" -d '{"username":"stan","password":"secret"}' 'http://localhost:8080/users/new'
```

```json
HTTP/1.0 201 CREATED
Content-Type: application/json
Content-Length: 28

{
    "created username": "stan"
}
```

List all existing users

```
curl -si 'http://localhost:8080/users'
```

```json
HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 37

{
    "user 0": "admin", 
    "user 1": "stan"
}
```

