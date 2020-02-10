# weather-service
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

## Running

### To run the server use the following command:

```
macbook$ docker run -it -p 8080:8080 api
```

### Then from a different terminal window you can send requests.

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
  
