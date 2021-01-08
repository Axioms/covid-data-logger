import requests, re, sqlite3, time
from discord_webhook import DiscordWebhook as wh, DiscordEmbed as Embed
import datetime as date

db = ""
table = ""
wait_time = 86400
URL = ''
regex = ""
webhook_url = ""



def create_date(month, day):
    now = date.datetime.now()
    year = now.year
    month = month.lower().strip()
    month_converter = {
        "january"   : 1,
        "february"  : 2,
        "march"     : 3,
        "april"     : 4,
        "may"       : 5,
        "june"      : 6,
        "july"      : 7,
        "august"    : 8, 
        "september" : 9, 
        "october"   : 10,
        "november"  : 11,
        "december"  : 12
    }
    
    return date.datetime(year, month_converter[month], day)

def log(start_date, end_date, cases, text):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    
    c.execute("create table if not exists " + table + " (start Date UNIQUE, end Date, cases number, log date, string text UNIQUE)")
    
    data = (start_date, end_date, cases, date.datetime.now(), text)
    
    c.execute("INSERT OR IGNORE into " + table + " values (?,?,?,?,?)", data)
    conn.commit()
    conn.close()
    
def get_total_cases():
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute("create table if not exists " + table + " (start Date, end Date, cases number, log date, string text)")
    
    total_cases = 0
    for row in c.execute("SELECT cases FROM " + table):
        total_cases = total_cases + row[0]
    conn.close()
    
    return total_cases

def get_weekly_cases():
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute("create table if not exists " + table + " (start Date, end Date, cases number, log date, string text)")
    
    c.execute("SELECT cases FROM " + table + " ORDER BY log DESC")
    cases = c.fetchone()[0]
    conn.close()
    
    return cases

def get_weekly_text():
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute("create table if not exists " + table + " (start Date, end Date, cases number, log date, string text)")
    
    c.execute("SELECT string FROM " + table + " ORDER BY log DESC")
    text = c.fetchone()[0]
    conn.close()
    
    return text

def poll_site():
    page = requests.get(URL)

    result = re.search(regex, page.content.decode('utf-8'))
    return result.group()

def discord_hook():
    now = date.datetime.now()
    weekly_cases = get_weekly_cases()
    weekly_text = get_weekly_text()
    total_cases = get_total_cases()
    
    webhook = wh(url=webhook_url)
    
    embed = Embed(title='Covid Numbers', description=weekly_text, color=242424)
    embed.set_author(name='Axiom', url='https://github.com/Axioms', icon_url='https://avatars1.githubusercontent.com/u/15842624?s=400&u=1b28628ffc8782cb9ea538f3ac026af6a218af55&v=4')
    embed.set_footer(text='</> with <3')
    embed.set_timestamp()
    embed.add_embed_field(name='Weekly Cases', value=weekly_cases)
    embed.add_embed_field(name='Total Cases Since 2021', value=total_cases)
    
    webhook.add_embed(embed)
    webhook.execute()
    

def main():
    print("retrieving data from School servers...")
    result = poll_site()
    text = result
    result = result.split()
    
    start_date = create_date(result[4], int(result[5]))
    end_date = create_date(result[7], int(result[8].strip(",")))
    cases = int(result[11])
    
    print("Logging data...")
    log(start_date, end_date, cases, text)
    print("Sendeding data to discord...")
    discord_hook()
    
    print("waiting for a day...")
    time.sleep(time_time)


main()
