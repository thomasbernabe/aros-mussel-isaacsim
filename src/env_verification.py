import os 
import omni.usd 
import omni.timeline
import omni.kit.commands

def environment_verification():
    '''
    scripts verifies that the current isaac sim environment is 
    configured and reports correct paths to files and 
    '''

    # get current working directory 
    cwd = os.getcwd()
    print(f"Current working directory: {cwd}")

    # check if timeline is playing 
    timeline = omni.timeline.get_timeline_interface()
    is_playing = timeline.is_playing()
    print(f"Timeline is playing: {is_playing}")

    # get current stage path 
    stage = omni.usd.get_context().get_stage()

    if stage:
        stage_path = omni.usd.get_context().get_stage_url()
        print(f"Current USD stage: {stage_path}")

        # extract repo path from stage path
        if "/scenes" in stage_path:
            repo_path = stage_path.split("/scenes/")[0]
            print(f"Repository path: {repo_path}")

        else:
            print("Could not determine repository path from stage path")

        # check for key prims in scene
        object_path = "World/clean_mussel"
        ground_path = "World/GroundPlane"

        object_prim = stage.GetPrimAtPath(object_path)
        ground_prim = stage.GetPrimAtPath(ground_path)

        print(f"Object prim exists: {object_prim.IsValid()}")
        print(f"Ground plane prim exists: {ground_prim.IsValid()}")
    
    else:
        print("No stage is currently loaded")

if __name__ == "__main__":
    environment_verification()