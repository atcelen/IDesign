from IDesign import IDesign

i_design = IDesign(no_of_objects = 15, 
                   user_input = "A creative vibrant livingroom", 
                   room_dimensions = [4.0, 4.0, 2.5])

i_design.create_initial_design()
i_design.correct_design()
i_design.refine_design(verbose=True)
i_design.create_object_clusters(verbose=False)
i_design.backtrack(verbose=True)
i_design.to_json()
