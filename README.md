# IDesign
This is the official Github Repo for [*I-Design: Personalized LLM Interior Designer*](https://atcelen.github.io/I-Design/)

## Requirements
Install the requirements
```bash
conda create -n idesign python=3.9
pip install -r requirements.txt
```
Create the "OAI_CONFIG_LIST.json" file
```json
[
    {
        "model": "gpt-4",
        "api_key": "YOUR_API_KEY"
    },
    {
        "model": "gpt-4-1106-preview",
        "api_key": "YOUR_API_KEY"
    },
    {
        "model": "gpt-3.5-turbo-1106",
        "api_key": "YOUR_API_KEY",
        "api_version": "2023-03-01-preview"
    }
]
```
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
