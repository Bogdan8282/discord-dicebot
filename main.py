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
    if message.author.bot:
        return

    if message.id in processed_messages:
        return

    processed_messages.add(message.id)

    content = message.content.strip().lower()

    # Патерн для парсингу: 5d20+3 adv sum, 4d6-2 dis, тощо
    pattern = r"(\d{1,2})d(\d{1,3})([+-]\d+)?(?:\s+(adv|dis))?(?:\s+(sum))?"

    match = re.fullmatch(pattern, content)

    if match:
        amount = int(match.group(1))
        sides = int(match.group(2))
        modifier_str = match.group(3)
        modifier = int(modifier_str) if modifier_str else 0
        advantage = match.group(4)  # 'adv' або 'dis'
        show_sum = match.group(5) == "sum"

        if amount <= 0 or sides <= 0 or amount > 20 or sides > 1000:
            await message.channel.send("❗ Некоректний запит. Можна максимум 20 кидків і не більше 1000 граней.")
            processed_messages.discard(message.id)
            return

        rolls = []
        detailed_rolls = []

        for _ in range(amount):
            if advantage == "adv":
                roll1 = random.randint(1, sides)
                roll2 = random.randint(1, sides)
                chosen = max(roll1, roll2)
                if modifier_str:
                    final_roll = chosen + modifier
                    detailed_rolls.append(f"[{roll1}, {roll2}] → **{chosen}**{modifier_str}={final_roll}")
                else:
                    final_roll = chosen
                    detailed_rolls.append(f"[{roll1}, {roll2}] → **{final_roll}**")
                rolls.append(final_roll)
            elif advantage == "dis":
                roll1 = random.randint(1, sides)
                roll2 = random.randint(1, sides)
                chosen = min(roll1, roll2)
                if modifier_str:
                    final_roll = chosen + modifier
                    detailed_rolls.append(f"[{roll1}, {roll2}] → **{chosen}**{modifier_str}={final_roll}")
                else:
                    final_roll = chosen
                    detailed_rolls.append(f"[{roll1}, {roll2}] → **{final_roll}**")
                rolls.append(final_roll)
            else:
                roll = random.randint(1, sides)
                if modifier_str:
                    final_roll = roll + modifier
                    detailed_rolls.append(f"{roll}{modifier_str}={final_roll}")
                else:
                    final_roll = roll
                    detailed_rolls.append(str(final_roll))
                rolls.append(final_roll)

        rolls_str = "\n".join(detailed_rolls)
        description = f"**Кидки:**\n{rolls_str}\n"

        if show_sum:
            total = sum(rolls)
            description += f"\n**Сума:** {total}"

        title_text = f"🎲 {message.author.display_name} кидає {amount}d{sides}"
        if modifier_str:
            title_text += f"{modifier_str}"
        if advantage:
            title_text += f" з {'перевагою' if advantage == 'adv' else 'перешкодою'}"
        if show_sum:
            title_text += " з підрахунком суми"

        embed = discord.Embed(
            title=title_text,
            description=description,
            color=discord.Color.green()
        )

        try:
            await message.delete()
        except discord.Forbidden:
            print("❗ Бот не має права видаляти повідомлення.")
        except discord.HTTPException:
            print("⚠️ Не вдалося видалити повідомлення.")

        result_message = await message.channel.send(embed=embed)

        await asyncio.sleep(480)  # Інтервал видалення повідомлення бота
        try:
            await result_message.delete()
        except discord.NotFound:
            pass
        except discord.HTTPException:
            print("⚠️ Не вдалося видалити повідомлення з результатом.")

        processed_messages.discard(message.id)

client.run(TOKEN)
