# Simple python data processing pipeline #

Example usage:

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


Make chart with graphviz:

    dot -Tpng example_flow.dot -O

![Pipeline example](example_flow.dot.png)


## License ##

MIT license
