from app import create_app
import io

app = create_app()
app.testing = True
client = app.test_client()

data = {
    'file': (io.BytesIO(b"car_name,price\nhonda,1000\ntoyota,2000\n"), 'test1.csv')
}
res1 = client.post('/analyze', data=data, content_type='multipart/form-data')
print("Test 1 response length:", len(res1.data))
print("Test 1 check if 'car_name' is in response:", b'car_name' in res1.data)

data2 = {
    'file': (io.BytesIO(b"bike_name,speed\nyamaha,100\nsuzuki,120\n"), 'test2.csv')
}
res2 = client.post('/analyze', data=data2, content_type='multipart/form-data')
print("Test 2 response length:", len(res2.data))
print("Test 2 check if 'bike_name' is in response:", b'bike_name' in res2.data)
print("Test 2 check if 'car_name' is STILL in response:", b'car_name' in res2.data)
