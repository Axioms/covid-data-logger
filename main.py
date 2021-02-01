import requests, re, sqlite3, time, os, json, graphing
from discord_webhook import DiscordWebhook as wh, DiscordEmbed as Embed
from dotenv import load_dotenv
import datetime as date

load_dotenv()
db = os.getenv("DB_FILE")
table_school = os.getenv("TABLE_SCHOOL")
table_state = os.getenv("TABLE_STATE")
wait_time = 3600
SCHOOL_URL = os.getenv("SCHOOL_URL")
STATE_URL = os.getenv("STATE_URL")  
regex = os.getenv("REGEX")
webhook_url = os.getenv("WEB_HOOK")



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

def init_db():
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute("create table if not exists " + table_state + " (start Date, end Date, cases number, log date, string text UNIQUE)")
    c.execute("create table if not exists " + table_school + " (start Date, end Date, cases number, log date, string text UNIQUE)")
    

def log(table, start_date, end_date, cases, text):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    
    data = (start_date, end_date, cases, date.datetime.now(), text)
    
    c.execute("INSERT OR IGNORE into " + table + " values (?,?,?,?,?)", data)
    conn.commit()
    conn.close()
    
def get_total_cases(table):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    
    total_cases = 0
    for row in c.execute("SELECT cases FROM " + table):
        total_cases = total_cases + row[0]
    conn.close()
    
    return total_cases

def get_current_cases(table):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    
    c.execute("SELECT cases FROM " + table + " ORDER BY log DESC")
    cases = c.fetchone()[0]
    conn.close()
    
    return cases

def get_current_text(table):
    conn = sqlite3.connect(db)
    c = conn.cursor()
        
    c.execute("SELECT string FROM " + table + " ORDER BY log DESC")
    text = c.fetchone()[0]
    conn.close()
    
    return text

def poll_site():
    page = requests.get(SCHOOL_URL)

    result = re.search(regex, page.content.decode('utf-8'))
    return result.group()

def graph(table):
    graphData = [[],[]]
    conn = sqlite3.connect(db)
    c = conn.cursor()
    
    c.execute("SELECT cases, end FROM " + table + " ORDER BY start ASC")
    data = c.fetchall()
    
    for row in data:
        graphData[0].append(row[0])
        graphData[1].append(row[1][5:10])
    
    if table == table_state:
        return graphing.graph(graphData)
    else:
        return graphing.graph(graphData, False)
    

def discord_state_hook(data_quality, data_date):
    daily_cases = get_current_cases(table_state)
    total_cases = get_total_cases(table_state)
    image_url = graph(table_state)
    webhook = wh(url=webhook_url)
    
    embed = Embed(title='Covid Numbers for STATE', description="Data Quality " + data_quality +"\nThis data pertains to the day of " + data_date.strftime("%m/%d/%y"), color=16727078)
    embed.set_author(name='Axiom', url='https://github.com/Axioms', icon_url='https://avatars1.githubusercontent.com/u/15842624?s=400&u=1b28628ffc8782cb9ea538f3ac026af6a218af55&v=4')
    embed.set_timestamp()
    embed.add_embed_field(name='Daily Cases', value=daily_cases)
    embed.add_embed_field(name='Total Cases Since 2021', value=total_cases)
    embed.set_image(url=image_url)
    
    webhook.add_embed(embed)
    webhook.execute()

def discord_school_hook():
    weekly_cases = get_current_cases(table_school)
    weekly_text = get_current_text(table_school)
    total_cases = get_total_cases(table_school)
    image_url = graph(table_school)
    webhook = wh(url=webhook_url)
    
    embed = Embed(title='Covid Numbers for SCHOOL', description=weekly_text, color=242424)
    embed.set_author(name='Axiom', url='https://github.com/Axioms', icon_url='https://avatars1.githubusercontent.com/u/15842624?s=400&u=1b28628ffc8782cb9ea538f3ac026af6a218af55&v=4')
    embed.set_timestamp()
    embed.add_embed_field(name='Weekly Cases', value=weekly_cases)
    embed.add_embed_field(name='Total Cases Since 2021', value=total_cases)
    embed.set_image(url=image_url)
    webhook.add_embed(embed)
    webhook.execute()
    
def detect_change(table, current_text):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    
    c.execute("SELECT string FROM " + table + " ORDER BY log DESC")
    data = c.fetchone()
    if data == None:
        text = ""
    else:
        text = data[0]
    conn.close()
    if current_text == text:
        return False
    
    return True

def get_school_data():
    result = poll_site()
    text = result
    result = result.split()
    start_date = create_date(result[4], int(result[5]))
    end_date = create_date(result[7], int(result[8].strip(",")))
    cases = int(result[11])
    
    return (start_date, end_date, cases, text)

def get_state_data():
    data = requests.get(STATE_URL)
    json_data = json.loads(data.text)
    year = int(json_data["date"]/10000)
    month = int((json_data["date"]/100)%100)
    day = int(json_data["date"]%100)
    start_date = date.date(year, month, day)
    cases = json_data["positiveIncrease"]
    text = json_data["hash"]
    data_quality = json_data["dataQualityGrade"]
    
    return (start_date, cases, text, data_quality)

def main():
    while True:
        print("retrieving data from servers...")
        school_data = get_school_data()
        state_data = get_state_data()
        school_data_changed = detect_change(table_school, school_data[3])
        state_data_changed = detect_change(table_state, state_data[2])
        
        print("Logging data...")
        log(table_school, school_data[0], school_data[1], school_data[2], school_data[3])
        log(table_state, state_data[0], state_data[0], state_data[1], state_data[2])
        
        print("Sendeding data to discord if needed...")
        if school_data_changed:
            discord_school_hook()
        
        if state_data_changed:
            discord_state_hook(state_data[3], state_data[0])
        
        print("waiting for a day...")
        time.sleep(wait_time)

init_db()
main()
