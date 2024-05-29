# IDesign
This is the official Github Repo for [*I-Design: Personalized LLM Interior Designer*](https://atcelen.github.io/I-Design/)

## Requirements
Install the requirements
```bash
conda create -n idesign python=3.9
conda activate idesign
pip install -r requirements.txt
conda install pytorch==1.12.1 torchvision==0.13.1 torchaudio==0.12.1 cudatoolkit=11.3 -c pytorch
pip install -U git+https://github.com/NVIDIA/MinkowskiEngine
conda install -c dglteam/label/cu113 dgl
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
Create the scene graph and allocate coordinate positions
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
i_design.to_json()
```

Retrieve the 3D assets from Objaverse using OpenShape
```bash
git clone https://huggingface.co/OpenShape/openshape-demo-support
cd openshape-demo-support
pip install -e .
cd ..
python retrieve.py
```

Place the assets using the Blender Scripting Module using the script in the *place_in_blender.py* file

## Evaluation
After creating scene renders in Blender, you can use the GPT-V evaluator to generate grades for evaluation. Fill in the necessary variables denoted with TODO and run the script
```bash
python gpt_v_as_evaluator.py
```

## Results
![gallery](imgs/gallery.jpg)