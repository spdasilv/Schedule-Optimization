# Optimizing Travel Schedules

## Objective

* This objective of this project is to generate optimal schedules for a traveller moving between geographical points in a map. The problem studied is a variation of the well-known Travelling Salesman Problem. This variation includes the following new constraints and challenges:
* The traveller may transverse the region in a span of multiple days.
* The traveller must start and end each day.
* The traveller only has a limited amount of time allocated each day to travel.
* Each point visited by the salesman is only available for visitation at certain hours.
* Each point has a degree of preference (Weight Scores). Those degrees of preference are set by the traveller.
* Not all points must be visited, but each point may only be visited once.

Given the above set of constraints, the objective is to maximize the traveller trip gain in terms of how many places with a higher degree of preference it managed to visit. Thus, this main interest of this project is to find a way to generate a schedule that balances visits to point of higher importance to the traveller, while keeping in mind the travel time between points.
## Proposed Solutions

* **Genetic Algorithm:** The Genetic Algorithm is a good choice for solving complex problems where an approximate solution is accepted. For this specific problem, the GA would generate random solutions of varying “goodness”, only to mutate and evolve across multiple generations (the algorithm can determine points of optimal performance and uses them to breed selectively). This method would allow the team to avoid local maxima (instead of a true maximum) and is scalable for a larger number of activities. However, it does run the risk of being time consuming and will realistically run slower than an LP when dealing with a smaller number of possible activities.
* **Custom Heuristic:**  The custom heuristic, which would signify the level of enjoyment derived by doing an activity, would be defined based on the time spent doing the activity versus the total time commuting to the activity. Each time an activity is be selected, a new list of possible activities to follow would be generated, and the heuristic would be used to determine which activity to choose based on the commute distance and the user-determined priority value/weight (gathered from user preferences). This method would generate routes which would provide users with as much enjoyment as possible while reducing undesirable travel time. 
* **LP Solver (Gurobi):** This approach would deliver the best possible solution, but is not scalable; the processing time faces exponential growth. The scalability issue, however, may not present itself as a major problem, given that users typically have a small set of desired attractions. It is reasonable to not expect a group list larger than a few dozen locations. However, the team discovered that the solver was unable to handle the massive amount of generated variables and could not run after a certain threshold (10 points). Also, Gurobi offers academic licenses only for academic IP addresses; commercial licenses are thousands of dollars per year. 

### Success Metrics

* **Processing time:** The processing time of the solution is dependent on the number of variables, but each method is sensitive to one particular variable. For example, the heuristic focuses on the number of days and number of activities, whereas the Genetic Algorithm is influenced by the chosen route. The processing time is inversely proportionate to the scalability of the method.

* **Score obtained:** Given that each activity has a score assigned by the user, the sum of scores represents the score of the trip; the higher the value, the higher the overall group satisfaction. It is also important that the algorithm cannot be stuck in local maxima or minima. 

* **Implementation:** How easy is it to implement this method as a web application? Can the team members learn the required technologies to an acceptable level of proficiency, given the time frame of the project? Is the implementation process reasonable?
 
* **Access to technology:** Does the team have easy and constant access to the technologies required to develop the solution? Can the technologies be used for a web application for multiple users? The development of the solution cannot be cost intensive and must be relatively cheap to maintain or upgrade.

### Requirements
To run all 3 solution you will need:
* Python 3.4+
* Pyomo - http://www.pyomo.org/
* Pandas - http://pandas.pydata.org/

To run the MIP solution open your command prompt and enter:
```
pyomo solve --solver=gurobi "Travel Solver.py"
```

## Authors

* **Stefanno Da Silva**
* **Julie Yu**
* **Tara Tsang**
* **Shivam Sharma**
