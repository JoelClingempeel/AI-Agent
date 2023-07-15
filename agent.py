from bs4 import BeautifulSoup
import re

from utils import *


def ask_chatgpt(message, temperature=0):
    completion = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      messages=[
        {"role": "user", "content": message}
      ],
      temperature=temperature
    )
    return completion.choices[0].message.content


### TASK MANAGER ###

STEPS_PROMPT = """
Develop a series of steps for the following objective.
Each step should have the following format:

Step <number>: [step type] [Use output from: <previous step numbers>] <description>

Options for [step type]:
%s
  
The [Use output from] tag is optional, and if several outputs are present, they should be comma-separated.
  
For example:
Step 1: [search] Search for Italian restaurants in NYC.
Step 2: [text] [Use output from: 1] Write descriptions of several candidate restaurants for a party.
Step 3: [input] [Use output from: 2] Ask the user which one is best.
Step 4: [text] [Use output from: 3,4] Write an invitation for dinner at the restaurant chosen.

Please include one step per line.

Objective:  %s
"""

def parse_task(task):
    tags = re.findall("\[[^\[\]]*\]", task)
    if len(tags) > 1:
        prereqs = [int(j) for j in tags[1].split(" ")[-1][:-1].split(",")]
    else:
        prereqs = []
    core_task = re.sub("\[[^\[\]]*\]", "", task)
    return tags[0], prereqs, core_task

def get_tasks(instructions, objective):
    response = ask_chatgpt(STEPS_PROMPT % (instructions, objective))
    return [parse_task(task) for task in response.split("\n")]


class Agent:
    def __init__(self):
        self.task_fn_lookup = {}
        self.task_instructions = ""
        
    def register_task(self, task_data):
        task, instruction, task_fn = task_data
        self.task_fn_lookup[task] = task_fn
        self.task_instructions += "  * " + instruction + "\n"
        
    def complete_objective(self, objective):
        tasks = get_tasks(self.task_instructions, objective)
        task_results = []
        task_logged_results = []  # TODO Rename to be more general.

        for task_type, prereqs, task in tasks:
            context = "\n\n".join(task_results[j-1] for j in prereqs)
            task_result, task_logged_result = self.task_fn_lookup[task_type](task, context)

            task_results.append(task_result)
            task_logged_results.append(task_logged_result)

        task_outputs = [logged_result if logged_result != '' else result
                        for result, logged_result in zip(task_results, task_logged_results)]
        return [[*task, output]
                for task, output in zip(tasks, task_outputs)]