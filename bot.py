from datetime import datetime, timedelta
import os
import pymongo
from pyrogram import Client, filters
from pyrogram.types import Message

# -----------------------------
# MongoDB variables
# -----------------------------
MONGO_URI = os.getenv("MONGO_URI", "")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "mydatabase")
MONGO_COLLECTION_NAME = os.getenv("MONGO_COLLECTION_NAME", "kicks")

# -----------------------------
# Pyrogram variables
# -----------------------------
SESSION_NAME = os.getenv("SESSION_NAME", "kickbot")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")

# Command prefix
COMMAND_PREFIX = os.getenv("PREFIX", ".")

# Default kick time in hours (30 días = 720 horas)
DEFAULT_KICK_TIME_HOURS = int(os.getenv("DEFAULT_KICK_TIME_HOURS", "720"))

# -----------------------------
# Setup MongoDB client
# -----------------------------
mongo_client = pymongo.MongoClient(MONGO_URI)
db = mongo_client[MONGO_DB_NAME]
col = db[MONGO_COLLECTION_NAME]

# -----------------------------
# Setup Pyrogram client
# -----------------------------
app = Client(SESSION_NAME, bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH)

# -----------------------------
# Kick command
# -----------------------------
@app.on_message(filters.command("kick", prefixes=COMMAND_PREFIX) & filters.group)
async def kick_command(client: Client, message: Message):
    # Check if the user is a group admin
    member = await client.get_chat_member(message.chat.id, message.from_user.id)
    is_admin = member.status in ("creator", "administrator")

    if not is_admin:
        await message.reply_text("❌ Solo los administradores pueden usar este comando.")
        return

    # Aquí puedes agregar la lógica de kick a un usuario específico
    await message.reply_text("✅ Comando recibido. Procesando kick...")

# -----------------------------
# Scheduler: check kicks
# -----------------------------
async def check_kicks():
    """Expulsa automáticamente usuarios que superen el tiempo."""
    now = datetime.utcnow()
    expired = col.find({"kick_time": {"$lte": now}})
    for user in expired:
        chat_id = user["chat_id"]
        user_id = user["user_id"]
        try:
            await app.kick_chat_member(chat_id, user_id)
            col.delete_one({"_id": user["_id"]})
            print(f"Usuario {user_id} expulsado del chat {chat_id}")
        except Exception as e:
            print(f"Error al expulsar {user_id}: {e}")

# -----------------------------
# Start bot
# -----------------------------
if __name__ == "__main__":
    import asyncio
    import traceback

    # Solo inicia si existen todas las variables importantes
    required_vars = ["BOT_TOKEN", "API_ID", "API_HASH", "MONGO_URI"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print(f"⚠️ Faltan variables de entorno: {missing_vars}")
        print("El bot no arrancará hasta que estén configuradas.")
    else:
        # Inicia el scheduler cada 1 hora
        async def scheduler_loop():
            while True:
                try:
                    await check_kicks()
                except Exception:
                    traceback.print_exc()
                await asyncio.sleep(3600)  # 1 hora

        loop = asyncio.get_event_loop()
        loop.create_task(scheduler_loop())
        app.run()
