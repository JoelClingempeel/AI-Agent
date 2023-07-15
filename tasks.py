from bs4 import BeautifulSoup
import os
import requests

from utils import *

GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]
GOOGLE_SE_ID = os.environ["GOOGLE_SE_ID"]
BASE_SEARCH_URL = f"https://www.googleapis.com/customsearch/v1?key={GOOGLE_API_KEY}&cx={GOOGLE_SE_ID}&q="


### SEARCH TASKS ###

PRE_SEARCH_PROMPT = """
Given a web searching objective, what terms should be entered into a search engine.

Objective:  %s

Just give the search terms and nothing else.
"""

POST_SEARCH_PROMPT = """
Given a task, does the text contain the needed information.
If yes, please respond with it.
If no, please answer INSUFFICIENT.

Task:
%s

Text:
%s
"""

def format_query(query):
    return "".join([char if char.isalnum() else "%20" for char in query])

def search(query):
    search_results = requests.get(BASE_SEARCH_URL + format_query(query)).json()
    return [search_result["link"] for search_result in search_results["items"]]

def get_web_content(url, max_size=4000):
    raw_html = requests.get(url).text
    return BeautifulSoup(raw_html, "html.parser").getText()[:max_size]

def search_task(task, context):
    search_query = ask_chatgpt(PRE_SEARCH_PROMPT % task)
    search_results = search(search_query)
    for url in search_results:
        data = get_web_content(url)
        if "INSUFFICIENT" not in ask_chatgpt(POST_SEARCH_PROMPT % (task, data)):
            return (data, url)
    return ("Task could not be completed.", "")

SEARCH_TASK_DATA = ("[search]",
                    "The [search] tag if the text involves searching the web for text.",
                    search_task)


### TEXT TASKS ###

TEXT_PROMPT = """
Please complete the following task given context.

Task:
%s

Context:
%s
"""

def text_task(task, context):
    return (ask_chatgpt(TEXT_PROMPT % (task, context)), "")

TEXT_TASK_DATA = ("[text]",
                  "The [text] tag if the task involves writing text",
                  text_task)


### USER INPUT TASKS ###

def input_task(task, context):
    print("User input is required. Please do the following.")
    print(task)
    return (input("Input: "), "")


INPUT_TASK_DATA = ("[input]",
                   "The [input] tag if input from the user is required. (Use this sparingly.)",
                   input_task)
