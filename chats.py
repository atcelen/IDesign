from autogen.agentchat.groupchat import GroupChat
from autogen.agentchat.agent import Agent
from autogen.agentchat.assistant_agent import AssistantAgent

class GroupChat(GroupChat):
    def __init__(self, agents, messages, max_round=15):
        super().__init__(agents, messages, max_round)
        self.previous_speaker = None  # Keep track of the previous speaker
        self.counter = 0

    def select_speaker(self, last_speaker: Agent, selector: AssistantAgent):
        # Check if last message suggests a next speaker or termination
        last_message = self.messages[-1] if self.messages else None
        last_speaker_name = last_speaker.name if last_speaker else None

        self.previous_speaker = last_speaker

        if last_speaker_name == "Admin":
            return self.agent_by_name("Interior_designer")
        elif last_speaker_name == "Interior_designer":
            return self.agent_by_name("Interior_architect")
        elif last_speaker_name == "Interior_architect":
            return self.agent_by_name("Admin")
            
class ChatWithEngineer(GroupChat): 
    def __init__(self, agents, messages, max_round=15):
        super().__init__(agents, messages, max_round)
        self.previous_speaker = None  # Keep track of the previous speaker
        self.counter = 0

    def select_speaker(self, last_speaker: Agent, selector: AssistantAgent):
        # Check if last message suggests a next speaker or termination
        last_message = self.messages[-1] if self.messages else None
        last_speaker_name = last_speaker.name if last_speaker else None

        self.previous_speaker = last_speaker

        if last_speaker_name == "Admin":
            return self.agent_by_name("Engineer")
        elif last_speaker_name == "Engineer":
            return self.agent_by_name("Json_schema_debugger")
        elif last_speaker_name == "Json_schema_debugger":
            return self.agent_by_name("Engineer")

class LayoutCorrectorGroupChat(GroupChat):
    def __init__(self, agents, messages, max_round=15):
        super().__init__(agents, messages, max_round)
        self.previous_speaker = None
    
    def select_speaker(self, last_speaker: Agent, selector: AssistantAgent):
        last_message = self.messages[-1] if self.messages else None
        last_speaker_name = last_speaker.name if last_speaker else None

        self.previous_speaker = last_speaker

        if last_speaker_name == "Admin":
            return self.agent_by_name("Spatial_corrector_agent")
        elif last_speaker_name == "Spatial_corrector_agent":
            return self.agent_by_name("Json_schema_debugger")
        elif last_speaker_name == "Json_schema_debugger":
            if "SUCCESS" not in last_message["content"]:
                return self.agent_by_name("Spatial_corrector_agent")
            else:
                return self.agent_by_name("Admin")

class ObjectDeletionGroupChat(GroupChat):
    def __init__(self, agents, messages, max_round=15):
        super().__init__(agents, messages, max_round)
        self.previous_speaker = None
    
    def select_speaker(self, last_speaker: Agent, selector: AssistantAgent):
        last_message = self.messages[-1] if self.messages else None
        last_speaker_name = last_speaker.name if last_speaker else None

        self.previous_speaker = last_speaker

        if last_speaker_name == "Admin":
            return self.agent_by_name("Object_deletion_agent")
        elif last_speaker_name == "Object_deletion_agent":
            return self.agent_by_name("Object_deletion_agent")

class LayoutRefinerGroupChat(GroupChat):
    def __init__(self, agents, messages, max_round=15):
        super().__init__(agents, messages, max_round)
        self.previous_speaker = None  # Keep track of the previous speaker
        self.counter = 0

    def select_speaker(self, last_speaker: Agent, selector: AssistantAgent):
        # Check if last message suggests a next speaker or termination
        last_message = self.messages[-1] if self.messages else None
        last_speaker_name = last_speaker.name if last_speaker else None

        self.previous_speaker = last_speaker

        if last_speaker_name == "Admin":
            return self.agent_by_name("Layout_refiner")
        elif last_speaker_name == "Layout_refiner":
            return self.agent_by_name("Json_schema_debugger")
        elif last_speaker_name == "Json_schema_debugger":
            if "SUCCESS" not in last_message["content"]:
                return self.agent_by_name("Layout_refiner")
            else:
                return self.agent_by_name("Admin")