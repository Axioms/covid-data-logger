import matplotlib, os
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import datetime as date
from dotenv import load_dotenv

load_dotenv()
save_dir = os.getenv("SAVE_DIR")
server_address = os.getenv("SERVER_ADDRESS")


def graph(data, isState=True):
    # Data for plotting
    t = np.arange(0.0, 2.0, 0.01)
    s = 1 + np.sin(2 * np.pi * t)

    t = data[1]
    s = data[0]
    
    fig, ax = plt.subplots()
    ax.plot(t, s)
    
    ax.yaxis.grid()
    
    
    
    if isState:
        ax.set_xlabel("time (Days)", color="#ffffff")
        ax.set_title("Daily Infections", color="#ffffff")
    else:
        ax.set_xlabel("time (Weeks)", color="#ffffff")
        ax.set_title("Weekly Infections", color="#ffffff")

    plt.tick_params(axis='x', which='major', rotation=90)

    if isState:
        ax.set_ylim(0, max(s)+2000)
    ax.set_ylabel("New Cases", color="#ffffff")
    ax.tick_params(axis='x', colors='#ffffff')
    ax.tick_params(axis='y', colors='#ffffff')
    #plt.xticks([])
    ax.spines['bottom'].set_color('#ffffff')
    ax.spines['top'].set_alpha(0.0)
    ax.spines['right'].set_alpha(0.0)
    ax.spines['left'].set_alpha(0.0)
    
    if isState:
        ax.xaxis.set_major_locator(ticker.MultipleLocator(5))
        ax.xaxis.set_minor_locator(ticker.MultipleLocator(1))

    if isState:
        graphType = "State"
    else:
        graphType = "School" 
    
    file_name = date.datetime.now().strftime("%m-%d-%y") + "-" + graphType + ".png"
    
    fig.savefig( save_dir + file_name, transparent=True)
    hosting_url = server_address + file_name + "?v=" + date.datetime.now().strftime("%H")
    
    return hosting_url