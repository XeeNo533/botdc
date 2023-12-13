import discord
from discord.ext import commands, tasks
from discord import integrations
import sqlite3

# Inicjalizacja bota
bot = commands.Bot(command_prefix='!',intents=discord.Intents.all())

# Tworzenie bazy danych SQLite
conn = sqlite3.connect('voice_points.db', detect_types=sqlite3.PARSE_DECLTYPES)
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS voice_points (
        user_id INTEGER PRIMARY KEY,
        points INTEGER
    )
''')
conn.commit()

# Funkcja do dodawania punktu
def add_point(user_id):
    cursor.execute('INSERT OR IGNORE INTO voice_points (user_id, points) VALUES (?, 0)', (user_id,))
    cursor.execute('UPDATE voice_points SET points = points + 1 WHERE user_id = ?', (user_id,))
    conn.commit()

# Zadanie cykliczne dodające punkt co minutę
@tasks.loop(minutes=1)
async def add_points_task():
    for guild in bot.guilds:
        for member in guild.members:
            if member.voice and member.voice.channel:
                add_point(member.id)

# Komenda do sprawdzania liczby punktów dla wszystkich użytkowników
@bot.command(name='czas', help='Wyświetla liczbę punktów za czas spędzony na kanale głosowym dla wszystkich użytkowników')
async def show_all_points(ctx):
    cursor.execute('SELECT user_id, points FROM voice_points ORDER BY points DESC')
    results = cursor.fetchall()

    if not results:
        await ctx.send('Brak danych o punktach.')
        return

    message = 'Punkty za czas spędzony na kanale głosowym :\n'
    for user_id, points in results:
        member = ctx.guild.get_member(user_id)
        if member:
            message += f'{member.display_name}: {points} punktów\n'
        else:
            message += f'Użytkownik o ID {user_id}: {points} punktów\n'

    await ctx.send(message)

# Event przygotowania bota
@bot.event
async def on_ready():
    print(f'Zalogowano jako {bot.user.name}')
    add_points_task.start()

# Rozpoczęcie bota
bot.run('MTE4Mzg5MjI5NTQxMDUyMDExNA.GbQCbK.ZmDxH44SX3_FMSej_1CJ7397m8GjlfBNTIDkWY')