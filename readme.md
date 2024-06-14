# Simple Commerce
Simple commerce simulates placing an order, saving the order to the database and then publishing it to a RabbitMQ.

### API Docs
[x] User Service: `http://localhost:8081/docs`  
[x] Product Service: `http://localhost:8081/docs`  
[x] Order Service: `http://localhost:8083/docs` 

### Order Request Sample
```json
{
  "user_id": "7c11e1ce2741",
  "product_code": "product1"
}
```

## How to set up

### With Docker
1. Clone the repository
```bash
git clone https://github.com/mhope-2/simple-commerce.git
```
2. Build services
```bash
docker-compose build
```
3. Startup services using docker
```bash
docker-compose up
``` 
