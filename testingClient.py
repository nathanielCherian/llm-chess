import requests

# Prepare your data
fen1 = "rnbqkbnr/pppppppp/8/8/RRP4R/2q5/PP1PPPPP/R3KBNR w KQkq - 0 1"
fen2 = "rnbqkbnr/pppppppp/8/8/RRP4R/2q5/PP1PPPPP/R3KBNR w KQkq - 0 1"

san1 = "e4"
san2 = "e5"


data = [
    {"prompt": fen1, "completion": san1},
    {"prompt": fen2, "completion": san2}
]

# Send POST request
response = requests.post(
    'http://127.0.0.1:5000/eval',
    json=data  # This automatically sets the Content-Type header to application/json
)

# Print the response
#print("Status code:", response.status_code)
#print("Response JSON:", response.json())