# IDesign
This is the official Github Repo for [*I-Design: Personalized LLM Interior Designer*](https://atcelen.github.io/I-Design/)

## Requirements

## Inference
```python
from IDesign import IDesign

i_design = IDesign(no_of_objects = 15, 
                   user_input = "A creative livingroom", 
                   room_dimensions = [4.0, 4.0, 2.5])

# Interior Designer, Interior Architect and Engineer 
i_design.create_initial_design()
# Layout Corrector
i_design.correct_design()
# Layout Refiner
i_design.refine_design()
# Backtracking Algorithm
i_design.create_object_clusters(verbose=False)
i_design.backtrack()
```
## Results
