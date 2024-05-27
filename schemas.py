initial_schema = {
    "type" : "object",
    "properties":{
        "objects_in_room" : {
                "type" : "array",
                "items" : {
                    "type" : "object",
                    "properties" : {
                        "new_object_id": {
                            "type": "string",
                            "description" : "The id of the object, e.g. chair_1, table_1, bed_1, etc."
                        },
                        "style" : {
                            "type" : "string",
                            "description" : "Architectural Style of the object"
                        },
                        "material" : {
                            "type" : "string",
                            "description" : "The material that this object is made of"
                        },
                        "size_in_meters" : {
                            "type": "object",
                            "properties": {
                                "length": {
                                    "type": "number"
                                },
                                "width": {
                                    "type": "number"
                                },
                                "height": {
                                    "type": "number"
                                }
                            },
                            "required" : ["length", "width", "height"]
                        },
                        "is_on_the_floor" : {
                            "type"  : "boolean",
                            "description" : "Whether the this object is touching the floor"
                        },
                        "facing" : {
                            "type" : "string",
                            "description" : "The id of the object is this object facing, this has to be an object_id! Ex. west_wall, bookshelf_1, desk_1..."
                        },
                        "placement" : {
                            "type" : "object",
                            "description" : "The placement of the object in the room as a scene graph",
                            "properties" : {
                                "room_layout_elements" : {
                                    "type" : "array",
                                    "description" : "Scene Graph with the room layout elements such as walls, floor or ceiling. Ex. The desk is centered on the south wall, the chair is in the south-west corner...",
                                    "items" : {
                                        "type" : "object",
                                        "properties" : {
                                            "layout_element_id" : {
                                                "type" : "string",
                                                "description" : "The id of the layout element that this object is connected to, ex. south_wall, west_wall, ceiling...",
                                                "enum" : ["south_wall", "north_wall", "west_wall", "east_wall", "ceiling", "middle of the room"]
                                            },
                                            "preposition" : {
                                                "type" : "string",
                                                "description" : "The preposition that connects this object and the layout element, ex. on the west wall, in the corner...",
                                                "enum" : ["on", "in the corner"]
                                            }
                                        },
                                        "required" : ["layout_element_id", "preposition"]
                                    }
                                },
                                "objects_in_room" : {
                                    "type" : "array",
                                    "description" : "Scene Graph with the other placed objects in the room. Ex. The chair is in front of the desk, the plant is right of the bookshelf...",
                                    "items" : {
                                        "type" : "object",
                                        "properties" : {
                                            "object_id" : {
                                                "type" : "string",
                                                "description" : "The id of the object that this object is connected to, ex. bookshelf_1, plant_1..."
                                            },
                                            "preposition" : {
                                                "type" : "string",
                                                "description" : "The preposition that connects this object and the connected object. 'new_object_id' is 'preposition' 'object_id' . Ex. lamp_1 is left of desk_1, table_1 is behind the bed_1, rug_1 is under desk_1 (a rug is never 'on' or 'above' another object)...",
                                                "enum" : ["on", "left of", "right of", "in front", "behind", "under", "above"]
                                            },
                                            "is_adjacent" : {
                                                "type" : "boolean",
                                                "description" : "Whether this object and the connected object are adjacent to each other, ex. an object on the desk is adjacent to the desk."
                                            }
                                        }
                                    }
                                }
                            },
                            "required" : ["room_layout_elements", "objects_in_room"]
                        }
                    },
                    "required" : ["new_object_id", "style", "material", "size_in_meters", "is_on_the_floor", "facing", "placement"]
                }
            }
        },
        "required" : ["objects_in_room"]
}

interior_designer_schema = """
{
    "Objects" : {
        "type" : "array",
        "items" : {
            "type" : "object",
        },
    "required" : ["Objects"]
}
"""

interior_architect_schema = """
{
    "Placements" : {
        "type" : "array",
        "items" : {
            "type" : "object",
        },
    "required" : ["Placements"]
}
"""

engineer_schema = """
{
        "objects_in_room" : {
            "type" : "array",
            "items" : {
                "type" : "object",
                "properties" : {
                    "new_object_id": {
                        "type": "string",
                        "description" : "The lower-case id of the object, e.g. chair_1, table_1, bed_1, etc."
                    },
                    "style" : {
                        "type" : "string",
                        "description" : "Architectural Style of the object"
                    },
                    "material" : {
                        "type" : "string",
                        "description" : "The material that this object is made of"
                    },
                    "size_in_meters" : {
                        "type": "object",
                        "properties": {
                            "length": {
                                "type": "number"
                            },
                            "width": {
                                "type": "number"
                            },
                            "height": {
                                "type": "number"
                            }
                        },
                        "required" : ["length", "width", "height"]
                    },
                    "is_on_the_floor" : {
                        "type"  : "boolean",
                        "description" : "Whether the this object is touching the floor"
                    },
                    "facing" : {
                        "type" : "string",
                        "description" : "The id of the object is this object facing, this has to be an object_id! Ex. west_wall, bookshelf_1, desk_1..."
                    },
                    "placement" : {
                        "type" : "object",
                        "description" : "The placement of the object in the room as a scene graph",
                        "properties" : {
                            "room_layout_elements" : {
                                "type" : "array",
                                "description" : "Scene Graph with the room layout elements such as walls, floor or ceiling. Ex. The desk is on the south wall, the chair is in the south-west corner...",
                                "items" : {
                                    "type" : "object",
                                    "properties" : {
                                        "layout_element_id" : {
                                            "type" : "string",
                                            "description" : "The id of the layout element that this object is connected to, ex. south_wall, west_wall, ceiling...",
                                            "enum" : ["south_wall", "north_wall", "west_wall", "east_wall", "ceiling", "middle of the room"]
                                        },
                                        "preposition" : {
                                            "type" : "string",
                                            "description" : "The preposition that connects this object and the layout element, ex. on the west wall, in the south-west corner... For corners, both walls are included!",
                                            "enum" : ["on", "in the corner"]
                                        },
                                    },
                                    "required" : ["layout_element_id", "preposition"]
                                }
                            },
                            "objects_in_room" : {
                                "type" : "array",
                                "description" : "Scene Graph with the other placed objects in the room. Ex. The chair is in front of the desk, the plant is right of the bookshelf...",
                                "items" : {
                                    "type" : "object",
                                    "properties" : {
                                        "object_id" : {
                                            "type" : "string",
                                            "description" : "The id of the object that this object is connected to, ex. bookshelf_1, plant_1..."
                                        },
                                        "preposition" : {
                                            "type" : "string",
                                            "description" : "The preposition that connects the new_object_id and object_id objects in the following format: "new_object_id" is "preposition" "object_id". Ex. lamp_1 is left of desk_1, table_1 is behind the bed_1, rug_1 is under desk_1...",
                                            "enum" : ["on", "left of", "right of", "in front", "behind", "under"]
                                        },
                                        "is_adjacent" : {
                                            "type" : "boolean",
                                            "description" : "Whether this object and the connected object are adjacent to each other, ex. an object on the desk is adjacent to the desk."
                                        }
                                    }
                                }
                            }
                        },
                        "required" : ["room_layout_elements", "objects_in_room"]
                    }
                },
                "required" : ["object_id", "style", "material", "size_in_meters", "is_on_the_floor", "facing", "placement"]
            }
        }
    },
    "required" : ["objects_in_room"]
}

"""

layout_corrector_schema = {
    "corrected_object" : {
        "type" : "object",
        "properties" : {
            "new_object_id": {
                "type": "string",
                "description" : "The id of the object, e.g. chair_1, table_1, bed_1, etc."
            },
            "is_on_the_floor" : {
                "type"  : "boolean",
                "description" : "Whether the this object is touching the floor"
            },
            "facing" : {
                "type" : "string",
                "description" : "The id of the object is this object facing, this has to be an object_id! Ex. west_wall, bookshelf_1, desk_1..."
            },
            "placement" : {
                "type" : "object",
                "description" : "The placement of the object in the room as a scene graph",
                "properties" : {
                    "room_layout_elements" : {
                        "type" : "array",
                        "description" : "Scene Graph with the room layout elements such as walls, floor or ceiling. Ex. The desk is centered on the south wall, the chair is in the south-west corner...",
                        "items" : {
                            "type" : "object",
                            "properties" : {
                                "layout_element_id" : {
                                    "type" : "string",
                                    "description" : "The id of the layout element that this object is connected to, ex. south_wall, west_wall, ceiling...",
                                    "enum" : ["south_wall", "north_wall", "west_wall", "east_wall", "ceiling", "middle of the room"]
                                },
                                "preposition" : {
                                    "type" : "string",
                                    "description" : "The preposition that connects this object and the layout element, ex. on the west wall, in the corner...",
                                    "enum" : ["on", "in the corner"]
                                }
                            },
                            "required" : ["layout_element_id", "preposition"]
                        }
                    },
                    "objects_in_room" : {
                        "type" : "array",
                        "description" : "Scene Graph with the other placed objects in the room. Ex. The chair is in front of the desk, the plant is right of the bookshelf...",
                        "items" : {
                            "type" : "object",
                            "properties" : {
                                "object_id" : {
                                    "type" : "string",
                                    "description" : "The id of the object that this object is connected to, ex. bookshelf_1, plant_1..."
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
                            }
                        }
                    }
                },
                "required" : ["room_layout_elements", "objects_in_room"]
            }
        }    
    }
}

deletion_schema = {
    "object_to_delete" : "desk_1"
}

layout_refiner_schema = {
    "type" : "object",
    "properties":{
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
    },
    "required" : ["children_objects"]
}