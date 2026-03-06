from fastapi import FastAPI, Request

app = FastAPI()

@app.post("/test")
async def receive_webhook(request: Request):
    payload = await request.json()
    print("Webhook received:")
    print(payload)
    return {"status": "ok"}