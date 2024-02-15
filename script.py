import csv
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


email = ""
password = ""

driver = webdriver.Chrome()

# Constants
Time = 5
loading_time = 10
attempts = 3

url = "https://codeforces.com/contest/1927/standings/friends"
# iadon

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
    print("----->")


def getTitleNumProbStandings():
    contest_title = driver.find_element(By.XPATH, ".//div[@style='margin:0.5em auto;']"). \
        find_element(By.TAG_NAME, "a").text
    print("Contest Title: ", contest_title)
    standings = driver.find_element(By.TAG_NAME, "tbody").find_elements(By.TAG_NAME, 'tr')
    standings = standings[1:]

    global letters_size  # Declare letters_size as a global variable

    WebDriverWait(driver, 1).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'standings'))
    )

    table_headers = driver.find_elements(By.XPATH, "//table[@class='standings']//th[contains(@class, 'top')]/a")
    letters = [th.text.strip() for th in table_headers]
    letters_string = ', '.join(letters)
    letters_size = len(letters)  # Update the global variable letters_size
    print('Problems:', letters_string)

    numOfProblems = len(letters)

    # subtract 4 cuz there is some cells that doesn't represent questions (score, hacks, leaderboard, ..)
    print("Number of problems: ", numOfProblems)
    print("----->")
    return contest_title, numOfProblems, standings

def extractParticipants(standings):
    # dict = {name : {from 1 - len of problems}}
    Results = {}
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
        i = 1
        for problem in problems:
            try:
                found = (problem.get_attribute("problemid") is not None)
                if found:
                    try:
                        x = (problem.get_attribute("acceptedsubmissionid") is not None)
                        if x:
                            if problem.text.find(":") != -1:
                                Results[name][i] = 2
                                # print(f"{name} solved problem {i}")
                            else:
                                # print("been here")
                                if i not in Results[name].keys():
                                    Results[name][i] = 1
                                    # print(f"{name} upsolved problem {i}")
                                elif Results[name][i] == 0:
                                    Results[name][i] = 1
                    except:
                        if i not in Results[name]:
                            Results[name][i] = 0
                    i += 1
            except:
                print("")

    return Results


def storeData(Results, numOfProblems):
    ResultsCount = []
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

    keys = list(ResultsCount[0].keys())  # getting the head of the File
    with open('file.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, keys)
        writer.writeheader()

        for result in ResultsCount:
            writer.writerow(result)


def main():
    prevResults = {}
    try:
        Login()
    except Exception:
        print(f"Problem while logging in {Exception}")

    Results = title = numOfProblems = standings = 0

    pages = int(input("Enter the number of pages to scrape: "))
    for page in range(1, pages+1):
        time.sleep(loading_time)
        print(f"Page number {page}")
        driver.get(url+f"/page/{page}")

        if page == 1:
            print("Extracting Title | Number Of Problems | Standing")
            try:
                title, numOfProblems, standings = getTitleNumProbStandings()
                print("Title | Number Of Problems | Standing Extracted Successfully!")
            except Exception:
                print(f"Error On Title | numOfProblems | standings:: {Exception}")

            if not title and not numOfProblems and not standings:
                break

        try:
            Results = extractParticipants(standings)
            print("Participants extracted successfully!")
        except Exception:
            print(f"Error while Extracting Participants:: {Exception}")

        if not Results:
            break

        if Results == prevResults:
            print("No more pages to scrape")
            break

        prevResults = Results

    print("Preparing to write on file...")
    try:
        storeData(Results, numOfProblems)
        print("Database Updated!")
    except Exception:
        print(f"Couldn't store data due to {Exception}")

    print("DONE")
    time.sleep(Time)
    driver.quit()


if __name__ == "__main__":
    main()