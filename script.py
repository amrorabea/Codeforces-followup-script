import csv
import os
import time

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By

load_dotenv()

email = os.getenv('HANDLE')
password = os.getenv('PASSWORD')

driver = webdriver.Chrome()

# Constants
Time = 5
loading_time = 10
attempts = 3

url = os.getenv('URL')

Results = {}
ResultsCount = []


# ================================================================
def Login():  # LOGIN FIRST

    try:
        driver.get("https://codeforces.com/enter?back=%2F")
        email_ = driver.find_element(By.XPATH, ".//input[@id='handleOrEmail']")
        email_.send_keys(email)
        password_ = driver.find_element(By.XPATH, ".//input[@id='password']")
        password_.send_keys(password)
        login = driver.find_element(By.XPATH, ".//input[@class='submit']")
        login.click()
        print("Logged in!")
    except:
        print("Logging in error")

    time.sleep(loading_time)
    driver.get(url)
    time.sleep(loading_time)

    contest_title = driver.find_element(By.XPATH, ".//div[@class='contest-name title']"). \
        find_element(By.TAG_NAME, "a").text
    print("Contest Title: ", contest_title)
    standings = driver.find_element(By.TAG_NAME, "tbody").find_elements(By.TAG_NAME, 'tr')
    standings = standings[1:]

    numOfProblems = standings[0].find_elements(By.TAG_NAME, "td")
    numOfProblems = len(numOfProblems) - 4  # this is our range now
    # subtract 4 cuz there is some cells that doesn't represent questions (score, hacks, leaderboard, ..)
    print("Number of problems: ", numOfProblems)
    print("-------------------")
    # dict = {name : {from 1 - len of problems}}
    for participant in standings:
        # first we want the name of the participant
        # then we get the problems
        name = ''
        flag = 0
        for attempt in range(attempts):
            try:
                name = str(participant.find_element(By.TAG_NAME, "a").text.strip())
                break
            except:
                time.sleep(Time)
                name = ''
        # print(name)
        if name not in Results:
            Results[name] = {}
        problems = participant.find_elements(By.TAG_NAME, "td")
        if '*' in problems[1].text:
            flag = 1  # if we have the flag equal to 1 then we put 1 if not we put 2
        problems = problems[4:]
        for i in range(numOfProblems):
            try:
                x = problems[i].find_element(By.XPATH, ".//span[@class='cell-passed-system-test']")
                if flag != 1:
                    Results[name][i] = 2
                else:
                    if Results[name][i] != 2:
                        Results[name][i] = 1
            except:
                if i not in Results[name]:
                    Results[name][i] = 0

    print("Participants extracted successfully...")
    for name, values in Results.items():
        solved = 0
        upSolved = 0
        for inner_key, value in values.items():
            if value == 2:
                solved += 1
            elif value == 1:
                upSolved += 1
        ResultsCount.append({"NAME": name,
                             "Solved": solved,
                             "UpSolved": upSolved,
                             "Score": f"{round(((solved + upSolved / 2) / numOfProblems) * 100)}%"
                             })

    print("Preparing to write on file...")
    keys = list(ResultsCount[0].keys())  # getting the head of the File
    with open('file.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, keys)
        writer.writeheader()

        for result in ResultsCount:
            writer.writerow(result)
        print("Database Updated!")


def main():
    Login()
    time.sleep(Time)
    driver.quit()


if __name__ == "__main__":
    main()
