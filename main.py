import os
import discord
import random
import re
import asyncio
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('TOKEN')

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

processed_messages = set()

@client.event
async def on_ready():
    print(f'Бот запущений як {client.user}')

@client.event
async def on_message(message):
    # Пропускаємо повідомлення від ботів
    if message.author.bot:
        return

    # Перевіряємо, чи повідомлення вже оброблене
    if message.id in processed_messages:
        return

    # Додаємо ID повідомлення до оброблених
    processed_messages.add(message.id)

    content = message.content.strip().lower()

    # Перевірка формату NdM
    if re.fullmatch(r"\d{1,2}d\d{1,3}", content):
        amount, sides = map(int, content.split('d'))

        # Перевірка коректності значень
        if amount <= 0 or sides <= 0 or amount > 20 or sides > 1000:
            await message.channel.send("❗ Некоректний запит. Можна максимум 20 кидків і не більше 1000 граней.")
            # Видаляємо ID повідомлення після обробки помилки
            processed_messages.discard(message.id)
            return

        # Генерація кидків
        rolls = [random.randint(1, sides) for _ in range(amount)]
        rolls_str = ", ".join(str(r) for r in rolls)

        description = f"**Результат:** {rolls_str}\n"
        if amount > 1:
            total = sum(rolls)
            description += f"**Сума:** {total}"

        embed = discord.Embed(
            title=f"🎲 {message.author.display_name} кидає {amount}d{sides}",
            description=description,
            color=discord.Color.green()
        )

        # Спроба видалити повідомлення користувача
        try:
            await message.delete()
        except discord.Forbidden:
            print("❗ Бот не має права видаляти повідомлення.")
        except discord.HTTPException:
            print("⚠️ Не вдалося видалити повідомлення.")

        # Відправка результату
        result_message = await message.channel.send(embed=embed)

        await asyncio.sleep(600)
        try:
            await result_message.delete()
        except discord.NotFound:
            pass  # Повідомлення вже видалене
        except discord.HTTPException:
            print("⚠️ Не вдалося видалити повідомлення з результатом.")

        # Видаляємо ID повідомлення після завершення обробки
        processed_messages.discard(message.id)

    # Дозволяємо обробку інших команд, якщо вони є
    await client.process_commands(message)

client.run(TOKEN)