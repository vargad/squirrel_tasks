#!/usr/bin/env python3

task_results = {}

def task_deps(task):
    if getattr(task, "requires", None) != None:
        return task.requires().items()
    return []

def run_task(task):
    global task_results
    input_params = {}
    for key, dep_task in task_deps(task):
        if getattr(dep_task, "params", None) != None:
            result_key = (type(dep_task), dep_task.params())
        else:
            result_key = type(dep_task)
        if result_key not in task_results:
            result = run_task(dep_task)
            input_params[key] = result
        else:
            input_prams[key] = task_results[result_key]
    if getattr(task, "params", None) != None:
        print("Running task", type(task).__name__, "with params", task.params())
    else:
        print("Running task", type(task).__name__)
    return task.run(input_params)

def data_flow_graph(tasks_to_chart, label="Data flow graph"):
    dot = "digraph {\n"

    dot += f'\trankdir="LR"; ranksep="1.5"; label="{label}"; labelloc="top"\n'

    dot_nodes = []
    dot_edges = []

    tasks = set()
    not_sink = set()
    sources = set()
    visited_dep = set()

    def task_chart(task):
        task_name = type(task).__name__
        tasks.add(task_name)
        has_deps = False
        for key, dep_task in task_deps(task):
            has_deps = True
            dep_name = type(dep_task).__name__
            not_sink.add(dep_name)
            task_chart(dep_task)
            if getattr(dep_task, "params", None) != None:
                dep_label = f"{key} [{dep_task.params()}]"
            else:
                dep_label = key
            dep_key = (dep_name, task_name, dep_label)
            if dep_key not in visited_dep:
                dot_edges.append(f'\t{dep_name} -> {task_name} [label="{dep_label}"]')
            visited_dep.add(dep_key)
        if not has_deps:
            sources.add(task_name)

    for task in tasks_to_chart:
        task_chart(task)

    for task_name in tasks:
        shape = "cylinder" if (task_name not in not_sink) or (task_name in sources) else "box"
        dot_nodes.append(f"\t{task_name} [shape={shape}]")

    chart_header = f'digraph {{\n\trankdir="LR"; ranksep="1.5"; label="{label}"; labelloc="top"\n'
    return chart_header+"\n".join(dot_nodes)+"\n"+"\n".join(dot_edges)+"\n}"


if __name__ == "__main__":
    import random
    import statistics

    class FunnyNums(object):
        def run(self, input_params):
            print("Squirrels gather some nutts (sic!)")
            return [random.randint(0,100) for _ in range(10)]

    class DivisableNumbersTask(object):

        def __init__(self, divisor, limit=100):
            self.divisor = divisor
            self.limit = limit

        def params(self):
            return (self.divisor, self.limit)

        def run(self, input_params):
            return [i for i in range(self.limit) if i % self.divisor == 0]

    class MultiplyNums(object):

        def requires(self):
            return {
                    "random_nums": FunnyNums(),
                    "div3": DivisableNumbersTask(3,100),
                    "div4": DivisableNumbersTask(4,100)
                }

        def run(self, input_params):
            r = input_params["random_nums"][-1]
            return {
                    "div3": [r*n for n in input_params["div3"]],
                    "div4": [r*n for n in input_params["div4"]],
                }

    class AnalyzeNums(object):
        def requires(self):
            return {
                    "nums": FunnyNums()
                }

        def run(self, input_params):
            return statistics.mean(input_params["nums"])

    class MyInterestingMainTask(object):
        def requires(self):
            return {
                    "num_result": AnalyzeNums(),
                    "mul": MultiplyNums(),
                    "div3": DivisableNumbersTask(3,100),
                }

        def run(self, input_params):
            print(input_params)
            return input_params["num_result"]+sum(input_params["mul"]["div4"])+sum(input_params["div3"])

    print("result: ", run_task(MyInterestingMainTask()))

    with open("example_flow.dot", "w") as file:
        file.write(data_flow_graph([MyInterestingMainTask()]))
