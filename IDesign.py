from autogen import GroupChatManager
import json
import re
import networkx as nx

from agents import create_agents
from agents import is_termination_msg, gpt4_config
from corrector_agents import get_corrector_agents
from refiner_agents import get_refiner_agents

from chats import GroupChat, ChatWithEngineer, LayoutCorrectorGroupChat, ObjectDeletionGroupChat, LayoutRefinerGroupChat 

from utils import get_room_priors, extract_list_from_json
from utils import preprocess_scene_graph, build_graph, remove_unnecessary_edges, handle_under_prepositions, get_conflicts, get_size_conflicts, get_object_from_scene_graph
from utils import get_object_from_scene_graph, get_rotation, get_cluster_objects, clean_and_extract_edges
from utils import get_cluster_size
from utils import get_possible_positions, is_point_bbox, calculate_overlap, get_topological_ordering, place_object, get_depth, get_visualization

class IDesign:
    def __init__(self, no_of_objects, user_input, room_dimensions):
        self.no_of_objects = no_of_objects
        self.user_input = user_input
        self.room_dimensions = room_dimensions
        self.room_priors = get_room_priors(self.room_dimensions)
        self.scene_graph = None

    def create_initial_design(self):
        user_proxy, json_schema_debugger, interior_designer, interior_architect, engineer = create_agents(self.no_of_objects)
        
        groupchat = GroupChat(
            agents=[user_proxy, interior_designer, interior_architect],
            messages=[],
            max_round=15
        )

        chat_with_engineer = ChatWithEngineer(
            agents  =[user_proxy, engineer, json_schema_debugger],
            messages=[],
            max_round=15
        )

        manager = GroupChatManager(groupchat=groupchat, llm_config=gpt4_config, is_termination_msg=is_termination_msg)
        user_proxy.initiate_chat(
            manager,
            message=f"""
            The room has the size {self.room_dimensions[0]}m x {self.room_dimensions[1]}m x {self.room_dimensions[2]}m
            User Preference (in triple backquotes):
            ```
            {self.user_input}    
            ```
            Room layout elements in the room (in triple backquotes):
            ```
            ['south_wall', 'north_wall', 'west_wall', 'east_wall', 'middle of the room', 'ceiling']
            ```
            json
            """,
        )

        designer_response = json.loads(groupchat.messages[-2]["content"])
        architect_response = json.loads(groupchat.messages[-1]["content"])

        blocks_designer, blocks_architect = extract_list_from_json(designer_response), extract_list_from_json(architect_response)
        print("Lengths: ", len(blocks_designer), len(blocks_architect))
        json_data = None

        for d_block, a_block in zip(blocks_designer, blocks_architect):
            engineer.reset(), json_schema_debugger.reset()
            prompt = str(d_block) + "\n" + str(a_block)

            object_ids = [item["new_object_id"] for item in json_data["objects_in_room"]] if json_data is not None else []

            manager = GroupChatManager(groupchat=chat_with_engineer, 
                                       llm_config=gpt4_config, 
                                       human_input_mode="NEVER", 
                                       is_termination_msg=is_termination_msg)
            user_proxy.initiate_chat(
                manager,
                message=f"""
                Room layout elements in the room (in triple backquotes):
                ```
                ['south_wall', 'north_wall', 'west_wall', 'east_wall', 'middle of the floor', 'ceiling']
                ```
                Array of objects in the room (in triple backquotes):
                ```
                {object_ids}
                ```
                Objects to be placed in the room (in triple backquotes):
                ```
                {prompt}
                ```
                json
                """,
            )
            if json_data is None:
                json_data = json.loads(chat_with_engineer.messages[-2]["content"])
            else:
                json_data["objects_in_room"] += json.loads(chat_with_engineer.messages[-2]["content"])["objects_in_room"]
            
        self.scene_graph = json_data

    def correct_design(self, verbose=False, auto_prune=True):
        # Correct Spatial Conflicts
        scene_graph = preprocess_scene_graph(self.scene_graph["objects_in_room"])
        G = build_graph(scene_graph)
        G = remove_unnecessary_edges(G)
        G, scene_graph = handle_under_prepositions(G, scene_graph)

        conflicts = get_conflicts(G, scene_graph)

        if verbose:
            print("-------------------CONFLICTS-------------------")
            for conflict in conflicts:
                print(conflict)
                print("\n\n")

        user_proxy, spatial_corrector_agent, json_schema_debugger, object_deletion_agent = get_corrector_agents()

        while len(conflicts) > 0:
            spatial_corrector_agent.reset(), json_schema_debugger.reset()
            groupchat = LayoutCorrectorGroupChat(
                agents  =[user_proxy, spatial_corrector_agent, json_schema_debugger],
                messages=[],
                max_round=15
            )
            manager = GroupChatManager(groupchat=groupchat, llm_config=gpt4_config, is_termination_msg=is_termination_msg)
            user_proxy.initiate_chat(
                manager,
                message=f"""
                {conflicts[0]}
                """,
            )
            correction = groupchat.messages[-2]
            pattern = r'```json\s*([^`]+)\s*```' # Match the json object
            match = re.search(pattern, correction["content"], re.DOTALL).group(1)
            correction_json = json.loads(match)
            corr_obj = get_object_from_scene_graph(correction_json["corrected_object"]["new_object_id"], scene_graph)
            corr_obj["is_on_the_floor"] = correction_json["corrected_object"]["is_on_the_floor"]
            corr_obj["facing"] = correction_json["corrected_object"]["facing"]
            corr_obj["placement"] = correction_json["corrected_object"]["placement"]
            G = build_graph(scene_graph)
            conflicts = get_conflicts(G, scene_graph)

        if auto_prune:
            size_conflicts = get_size_conflicts(G, scene_graph, self.user_input, self.room_priors, verbose)

            if verbose:
                print("-------------------SIZE CONFLICTS-------------------")
                for conflict in size_conflicts:
                    print(conflict)
                    print("\n\n")

            while len(size_conflicts) > 0:
                object_deletion_agent.reset()
                groupchat = ObjectDeletionGroupChat(
                    agents  =[user_proxy, object_deletion_agent],
                    messages=[],
                    max_round=2
                )
                manager = GroupChatManager(groupchat=groupchat, llm_config=gpt4_config, is_termination_msg=is_termination_msg)
                user_proxy.initiate_chat(
                    manager,
                    message=f"""
                    {size_conflicts[0]}
                    """,
                )
                correction = groupchat.messages[-1]
                correction_json = json.loads(correction["content"])
                object_to_delete = correction_json["object_to_delete"]
                descendants = nx.descendants(G, object_to_delete)
                objs_to_delete = descendants.union({object_to_delete})
                print("Objs to Delete: ", objs_to_delete)
                scene_graph = [x for x in scene_graph if x["new_object_id"] not in objs_to_delete]
                for obj in objs_to_delete:
                    G.remove_node(obj)

                size_conflicts = get_size_conflicts(G, scene_graph, self.user_input, self.room_priors, verbose)
        self.scene_graph["objects_in_room"] = scene_graph

    def refine_design(self, verbose=False):
        cluster_dict = get_cluster_objects(self.scene_graph["objects_in_room"])

        inputs = []
        for key, value in cluster_dict.items():
            key = list(key)
            if len(key[0]) == 2:
                parent_id = key[0][0][1]
                prep = key[0][1][1]
            elif len(key[0]) == 3:
                parent_id = key[0][1][1]
                prep = key[0][2][1]
            objs = value

            inputs.append((parent_id, prep, objs))

        if verbose:
            for parent_id, prep, objs in inputs:
                print(f"Parent Object : {parent_id}")
                print(f"Children Objects : {objs}")
                print(f"The children objects are '{prep}' the parent object")
                print("\n")


        for parent_id, prep, obj_names in inputs:
            objs = [get_object_from_scene_graph(obj, self.scene_graph["objects_in_room"]) for obj in obj_names]
            objs_rot = [get_rotation(obj, self.scene_graph["objects_in_room"]) for obj in objs]

            parent_obj = get_object_from_scene_graph(parent_id, self.scene_graph["objects_in_room"])
            if parent_obj is None:
                parent_obj = [prior for prior in self.room_priors if prior.get("new_object_id") == parent_id][0]
            parent_obj_rot = get_rotation(parent_obj, self.scene_graph["objects_in_room"])

            rot_diffs = [obj_rot - parent_obj_rot for obj_rot in objs_rot]
            direction_check = lambda diff, prep: (diff % 180 == 0 and prep in ["left of", "right of"]) or (diff % 180 != 0 and prep in ["in front", "behind"]) or (diff % 180 != 0 and prep == "on")
            possibilities_str = "Constraints:\n" + '\n'.join(["\t" + f"Place objects {'behind or in front' if direction_check(diff, prep) else 'left or right'} of {name}!" for name, diff in zip(obj_names, rot_diffs)])

            user_proxy, layout_refiner, json_schema_debugger = get_refiner_agents()

            layout_refiner.reset(), json_schema_debugger.reset()
            groupchat = LayoutRefinerGroupChat(
                agents  =[user_proxy, layout_refiner, json_schema_debugger],
                messages=[],
                max_round=15
            )
            manager = GroupChatManager(groupchat=groupchat, llm_config=gpt4_config, is_termination_msg=is_termination_msg)
            user_proxy.initiate_chat(
                manager,
                message=f"""
                Parent Object : {parent_id}
                Children Objects : {obj_names}

                {possibilities_str}

                The children objects are '{prep}' the parent object
                """,
            )

            new_relationships = json.loads(groupchat.messages[-2]["content"])
            # Check whether the relationships are valid
            invalid_name_ids = []
            for child in new_relationships["children_objects"]:
                for other_child in child["placement"]["children_objects"]:
                    other_child_rot = get_rotation(get_object_from_scene_graph(other_child["name_id"], self.scene_graph["objects_in_room"]), self.scene_graph["objects_in_room"])
                    if direction_check(other_child_rot - parent_obj_rot, prep) and other_child["preposition"] not in ["in front", "behind"]:
                        invalid_name_ids.append(child["name_id"])
                    elif not direction_check(other_child_rot - parent_obj_rot, prep) and other_child["preposition"] not in ["left of", "right of"]:
                        invalid_name_ids.append(child["name_id"])

            if verbose:
                print("Invalid name IDs: ", invalid_name_ids)
            new_relationships["children_objects"] = [child for child in new_relationships["children_objects"] if child["name_id"] not in invalid_name_ids]         

            edges, edges_to_flip = clean_and_extract_edges(new_relationships, parent_id)

            prep_correspondences ={
                "left of" : "right of",
                "right of" : "left of",
                "in front" : "behind",
                "behind" : "in front",
            }


            for obj in new_relationships["children_objects"]:
                name_id = obj["name_id"]
                rel = obj["placement"]["children_objects"]
                for r in rel:
                    if (name_id, r["name_id"]) in edges:
                        to_flip = edges_to_flip[(name_id, r["name_id"])]
                        if to_flip:
                            corr_obj = get_object_from_scene_graph(r["name_id"], self.scene_graph["objects_in_room"])
                            corr_prep = prep_correspondences[r["preposition"]]
                            corr_obj["placement"]["objects_in_room"].append({"object_id" : name_id, "preposition" : corr_prep, "is_adjacent" : r["is_adjacent"]})
                        else:
                            corr_obj = get_object_from_scene_graph(name_id, self.scene_graph["objects_in_room"])
                            corr_obj["placement"]["objects_in_room"].append({"object_id" : r["name_id"], "preposition" : r["preposition"], "is_adjacent" : r["is_adjacent"]})

    def create_object_clusters(self, verbose=False):
        # Assign the rotations
        for obj in self.scene_graph["objects_in_room"]:
            rot = get_rotation(obj, self.scene_graph["objects_in_room"])
            obj["rotation"] = {"z_angle" : rot}
        
        ROOM_LAYOUT_ELEMENTS = ["south_wall", "north_wall", "west_wall", "east_wall", "ceiling", "middle of the room"]

        G = build_graph(self.scene_graph["objects_in_room"])
        nodes = G.nodes()

        # Create clusters
        for node in nodes:
            if node not in ROOM_LAYOUT_ELEMENTS:
                cluster_size, children_objs = get_cluster_size(node, G, self.scene_graph["objects_in_room"])
                if verbose:
                    print("Node: ", node)
                    print("Cluster size: ", cluster_size)
                    print("Children: ", children_objs)
                    print("\n")
                node_obj = get_object_from_scene_graph(node, self.scene_graph["objects_in_room"])
                cluster_size = {"x_neg" : cluster_size["left of"], "x_pos" : cluster_size["right of"], "y_neg" : cluster_size["behind"], "y_pos" : cluster_size["in front"]}
                node_obj["cluster"] = {"constraint_area" : cluster_size}

    def backtrack(self, verbose=False):
        self.scene_graph = self.scene_graph["objects_in_room"] + self.room_priors
        prior_ids = ["south_wall", "north_wall", "east_wall", "west_wall", "ceiling", "middle of the room"]
        
        point_bbox = dict.fromkeys([item["new_object_id"] for item in self.scene_graph], False)
        
        # Place the objects that have an absolute position
        for item in self.scene_graph:
            if item["new_object_id"] in prior_ids:
                continue
            possible_pos = get_possible_positions(item["new_object_id"], self.scene_graph, self.room_dimensions)
            # Determine the overlap based on the possible positions
            overlap = None
            if len(possible_pos) == 1:
                overlap = possible_pos[0]
            elif len(possible_pos) > 1:
                overlap = possible_pos[0]
                for pos in possible_pos[1:]:
                    overlap = calculate_overlap(overlap, pos)
            # If the overlap is a point bbox, assign the position
            if overlap is not None and is_point_bbox(overlap) and len(possible_pos) > 0:
                item["position"] = {"x" : overlap[0], "y" : overlap[2], "z" : overlap[4]}
                point_bbox[item["new_object_id"]] = True
        
        scene_graph_wo_layout = [item for item in self.scene_graph if item["new_object_id"] not in prior_ids]
        object_ids = [item["new_object_id"] for item in scene_graph_wo_layout]
        # Get depths
        depth_scene_graph = get_depth(scene_graph_wo_layout)
        max_depth = max(depth_scene_graph.values())
        
        if verbose:
            print("Max depth: ", max_depth)
            print("Depth scene graph: ", depth_scene_graph)
            print("Point BBox: ", [key for key, value in point_bbox.items() if value])
            get_visualization(self.scene_graph, self.room_priors)
            for obj in scene_graph_wo_layout:
                if "position" in obj.keys():
                    print(obj["new_object_id"], obj["position"])
        
        topological_order = get_topological_ordering(scene_graph_wo_layout)
        topological_order = [item for item in topological_order if item not in prior_ids]
        if verbose:
            print("Topological order: ", topological_order)
        
        d = 1
        while d <= max_depth:   
            if verbose:
                print("Depth: ", d)
            error_flag = False
            
            # Get nodes at the current depth
            nodes = [node for node in topological_order if depth_scene_graph[node] == d]
            if verbose:
                print(f"Nodes at depth {d}:", nodes)
            
            errors = {}
            for node in nodes:
                if point_bbox[node]:
                    continue
                
                # Find the object corresponding to the current node
                obj = next(item for item in scene_graph_wo_layout if item["new_object_id"] == node)
                errors = place_object(obj, self.scene_graph, self.room_dimensions, errors={})
                if verbose:
                    print(f"Errors for {obj['new_object_id']}:", errors)

                if errors:
                    if d > 1:
                        d -= 1
                        if verbose:
                            print("Reducing depth to: ", d)
                    
                    error_flag = True
                    # Delete positions for objects at or beyond the current depth
                    for del_item in scene_graph_wo_layout:
                        if depth_scene_graph[del_item["new_object_id"]] >= d:
                            if "position" in del_item.keys() and not point_bbox[del_item["new_object_id"]]:
                                if verbose:
                                    print("Deleting position for: ", del_item["new_object_id"])
                                del del_item["position"]
                    errors = {}
                    break
                            
            if not error_flag:
                d += 1
        
        get_visualization(self.scene_graph, self.room_priors)
    
    def to_json(self):
        # Save the scene graph to a json file
        with open("scene_graph.json", "w") as file:
            json.dump(self.scene_graph, file, indent=4)