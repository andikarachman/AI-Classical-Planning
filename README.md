
## Classical Planning

Planning is an important topic in AI because intelligent agents are expected to automatically plan their own actions in uncertain domains. Planning and scheduling systems are commonly used in automation and logistics operations, robotics and self-driving cars, and for aerospace applications like the Hubble telescope and NASA Mars rovers.

This project is split between implementation and analysis. First, we will combine symbolic logic and classical search to implement an agent that performs progression search to solve planning problems. Then, we will experiment with different search algorithms and heuristics, and use the results to answer questions about designing planning systems.

**NOTE:** This project is based on the book "Artificial Intelligence: A Modern Approach" 3rd edition chapter 10 *or* 2nd edition Chapter 11 on Planning, available [on the AIMA book site](http://aima.cs.berkeley.edu/2nd-ed/newchap11.pdf).

![Progression air cargo search](images/Progression.PNG)


## Getting Started

**NOTE:** You are _strongly_ encouraged to install pypy 3.5 (download [here](http://pypy.org/download.html)) for this project. Pypy is an alternative to the standard cPython runtime that tries to optimize and selectively compile your code for improved speed, and it can run 2-10x faster for this project. There are binaries available for Linux, Windows, and OS X. Simply download and run the appropriate pypy binary installer (make sure you get version 3.5) or use the package manager for your OS. When properly installed, any `python` commands can be run with `pypy` instead. (You may need to specify `pypy3` on some OSes.)

- Activate the aind environment (OS X or Unix/Linux users use the command shown; Windows users only run `activate aind`)
```
$ source activate aind
```

## The Project

1. Run the example problem (based on the cake problem from Fig 10.7 in Chapter 10.3 of AIMA ed3). The script will print information about the problem domain and solve it with several different search algorithms.
```
$ python example_have_cake.py
```

2. The `my_planning_graph.py` script refer to chapter 10 of AIMA 3rd edition or chapter 11 of AIMA 2nd edition (available [on the AIMA book site](http://aima.cs.berkeley.edu/2nd-ed/newchap11.pdf)) and the detailed instructions inline with each comment in the script. You can test the code for this module by running:
```
$ python -m unittest -m unittest -v
```

3. We experiment with different search algorithms using the `run_search.py` script. (See example usage below.) The goal of the experiment is to understand the tradeoffs in speed, optimality, and complexity of progression search as problem size increases. We record our results in a report.

  - Run the search experiment manually (you will be prompted to select problems & search algorithms)
```
$ python run_search.py -m
```

  - You can also run specific problems & search algorithms - e.g., to run breadth first search and UCS on problems 1 and 2:
```
$ python run_search.py -p 1 2 -s 1 2
```

## Experiment Details

The `run_search.py` script allows you to choose any combination of eleven search algorithms (three uninformed and eight with heuristics) on four air cargo problems. The cargo problem instances have different numbers of airplanes, cargo items, and airports that increase the complexity of the domains.

- You can also run **all** of the search algorithms on the first two problems and record the following information for each combination:
    - number of actions in the domain
    - number of new node expansions
    - time to complete the plan search

