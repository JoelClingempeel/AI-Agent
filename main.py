import sys

from agent import *
from tasks import *

def show_results(query, results, log_file_path):
    with open(log_file_path, "w") as f:
        f.write(query + "\n\n\n")
        for task_type, prereqs, task, output in results:
            f.write(task_type + " " + task + "\n")
            prereqs_string = ",".join(str([prereq for prereq in prereqs]))
            f.write("Uses results from:\t" + prereqs_string + "\n")
            f.write(output + "\n\n\n")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python %s <log_file_path>" % sys.argv[0])
        exit()
        
    agent = Agent()
    for task_data in [TEXT_TASK_DATA, SEARCH_TASK_DATA, INPUT_TASK_DATA]:
        agent.register_task(task_data)

    query = input("Input: ")
    results = agent.complete_objective(query)
    show_results(query, results, sys.argv[1])
    print(results[-1][-1])
