import requests

headers = {
    "authorization" : "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1IiwiZXhwIjoxNzY4MDM5MzMxfQ.gKkZ0K6ekgX_1auGw4m-794zArOddYXpN6o_x6AboKQ" 
}
req = requests.get("http://127.0.0.1:8000/auth/refresh", headers=headers)
print(req)
print(req.json)