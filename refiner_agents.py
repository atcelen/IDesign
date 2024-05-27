import autogen
from autogen.agentchat.groupchat import GroupChat
from autogen.agentchat.agent import Agent
from autogen.agentchat.user_proxy_agent import UserProxyAgent
from autogen.agentchat.assistant_agent import AssistantAgent
from copy import deepcopy
from jsonschema import validate
import json

from schemas import layout_refiner_schema
from agents import is_termination_msg

class JSONSchemaAgent(UserProxyAgent):
    def __init__(self, name : str, is_termination_msg):
        super().__init__(name, is_termination_msg=is_termination_msg)

    def get_human_input(self, prompt: str) -> str:
        message = self.last_message()
        preps_layout = ["left-side", "right-side", "in the middle"]
        preps_objs = ['on', 'left of', 'right of', 'in front', 'behind', 'under', 'above']

        json_obj_new = json.loads(message["content"])

        is_success  = False
        try:
            validate(instance=json_obj_new, schema=layout_refiner_schema)
            is_success = True
        except Exception as e:
            feedback = str(e.message)
            if e.validator == "enum":
                if str(preps_objs) in e.message:
                    feedback += f"Change the preposition {e.instance} to something suitable with the intended positioning from the list {preps_objs}"
                elif str(preps_layout) in e.message:
                    feedback += f"Change the preposition {e.instance} to something suitable with the intended positioning from the list {preps_layout}"
        if is_success:
            return "SUCCESS"
        return feedback

config_list_gpt4 = autogen.config_list_from_json(
    "OAI_CONFIG_LIST.json",
    filter_dict={
        "model": ["gpt-4-1106-preview"],
    },
)

gpt4_config = {
    "cache_seed": 42,
    "temperature": 0.0,
    "config_list": config_list_gpt4,
    "timeout": 600,
}
gpt4_json_config = deepcopy(gpt4_config)
gpt4_json_config["config_list"][0]["response_format"] = { "type": "json_object" }

def get_refiner_agents():
    user_proxy = autogen.UserProxyAgent(
        name="Admin",
        system_message = "A human admin.",
        is_termination_msg = is_termination_msg,
        human_input_mode = "NEVER",
        code_execution_config=False
    )

    json_schema_debugger = JSONSchemaAgent(
        name = "Json_schema_debugger",
        is_termination_msg = is_termination_msg,
    )

    layout_refiner = autogen.AssistantAgent(
        name = "Layout_refiner",
        llm_config = gpt4_json_config,
        is_termination_msg = is_termination_msg,
        human_input_mode = "NEVER",
        system_message = """ Layout Refiner. Every time when the Admin speaks; you will look at the parent object and children objects, the first  
        preposition that connects these objects and find a second suitable relative placement for the children objects whilst considering the initial positioning of the object. 
        Give the relative placement of the children objects with each other and with the parent object! For example, if there are five children objects that are 'on' the parent
        object, give the relative positions of the children objects to one another and the second preposition to the the parent object ('on' is the first preposition).

        Use only the following JSON Schema to save the JSON object:
        {
            "children_objects" : {
                "type" : "array",
                "items" : {
                    "type" : "object",
                    "properties" : {
                        "name_id" : {
                            "type" : "string"
                        },
                        "placement" : {
                            "type" : "object",
                            "properties" : {
                                "children_objects" : {
                                    "type" : "array",
                                    "items" : {
                                        "type" : "object",
                                        "properties" : {
                                            "name_id" : {
                                                "type" : "string",
                                                "description" : "The name_id of the other child object"
                                            },
                                            "preposition" : {
                                                "type" : "string",
                                                "description" : "The preposition that connects this object and the connected object, ex. left of the desk, behind the plant, the rug is under the desk...",
                                                "enum" : ["on", "left of", "right of", "in front", "behind", "under", "above"]
                                            },
                                            "is_adjacent" : {
                                                "type" : "boolean",
                                                "description" : "Whether this object and the connected object are adjacent to each other, ex. an object on the desk is adjacent to the desk."
                                            }
                                        },
                                        "required" : ["name_id", "preposition", "is_adjacent"]
                                    }
                                }
                            },
                            "required" : ["children_objects"]
                        }
                    },
                    "required" : ["name_id", "placement"]
                }
            },
        }
        """
    )

    return user_proxy, json_schema_debugger, layout_refiner