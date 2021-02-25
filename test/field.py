import os
import asyncio

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from bs4 import BeautifulSoup
import pickle

url = "https://tw.beanfun.com/MapleStory/"
pickl = "PIK.dat"
NEWS_Update = list() # new list
NEWS_Array = list() # pickled list

def print_NEWS(ob):
    print (ob[0], ob[1])
    print (ob[2])
    print (ob[3])

def save_p():
    with open(pickl, "wb") as p:
        for i in NEWS_Array[:5]:
            pickle.dump(i, p)

def load_p():
    global NEWS_Array
    with open(pickl, "rb") as p:
        try:
            for n in range(5):
                NEWS_Array.append(pickle.load(p))
        except EOFError:
            return

def fetch_site():
    global NEWS_Array
    mainpage = "main?section=mBulletin"
    DRIVER_PATH =  "/Users/ba/Documents/chromedriver"
    options = Options()
    options.headless = True
    options.add_argument("--window-size=1920,1200")
    driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)

    # load pickle
    load_p()

    # Driver read and setup
    driver.get(url+mainpage)
    soup = BeautifulSoup(driver.page_source, "lxml")
    mBulletin = soup.find_all("a", class_="mBulletin-items-link")

    # Iterate uBulletin
    for item in mBulletin:
        href = str(item['href'])
        date = str(item.find(class_="mBulletin-items-date").contents[0])
        cate = str(item.find(class_="mBulletin-items-cate").contents[0])
        title = str(item.find(class_="mBulletin-items-title").contents[0])
        n = (cate, title, date, url+href)
        if n not in NEWS_Array:
            NEWS_Update.append(n)
        else:
            break

    # Close driver
    driver.quit()

def run():
    fetch_site()
    if len(NEWS_Update) != 0:
        for item in NEWS_Update[::-1]:
            print_NEWS(item)
            NEWS_Array.insert(0, item)
    save_p()

if __name__ == "__main__":
    run()


