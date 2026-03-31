@app.on_message(filters.new_chat_members)
async def new_member_register(client, message):
    for user in message.new_chat_members:
        # Guarda en MongoDB la fecha de entrada
        col.insert_one({
            "user_id": user.id,
            "username": user.username or user.first_name,
            "join_date": datetime.utcnow()
        })
        await message.reply_text(f"¡Bienvenido @{user.username}! Te registraré automáticamente para que seas expulsado después del tiempo configurado.")
