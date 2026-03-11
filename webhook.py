from fastapi import FastAPI, Request
import config, database
from aiogram import Bot

app = FastAPI()
bot = Bot(config.BOT_TOKEN)

@app.post("/crypto")
async def crypto_webhook(request: Request):
    data = await request.json()
    if data.get("update_type") == "invoice_paid":
        payload = data.get("payload")
        user_id, product_id = payload.split(":")
        item = database.get_item(product_id)
        if item:
            database.add_balance(user_id, -item[1])
            if item[3]:
                await bot.send_document(user_id, open(item[3], "rb"))
            else:
                await bot.send_message(user_id, f"✅ Оплата прошла!\nВаш товар: {item[2]}")
    return {"ok": True}
