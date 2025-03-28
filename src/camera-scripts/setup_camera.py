import os 
import numpy as np 
import omni 
import omni.replicator.core as rep 
from omni.isaac.sensor import Camera
from omni.isaac.core.utils.rotations import look_at
from omni.isaac.core.utils.numpy.rotations import matrix_to_quaternion
from pxr import UsdGeom

class CameraSetup:
    def __init__(self, repo_path=None):
        # determine repository path
        if repo_path is None:
            # try getting it from current stage
            stage_path = omni.usd.get_context().get_stage_url()
            if "/scenes/" in stage_path:
                repo_path = stage_path.split("/scenes/")[0]
            else:
                repo_path = os.getcwd()
                print(f"Warning: Could not determine repo path --> using current directory: {repo_path}")

        # set up paths
        self.repo_path = repo_path
        self.output_dir = os.path.join(repo_path, "outputs", "rendered_images")
        os.makedirs(self.output_dir, exist_ok=True)

        # camera parameters
        self.resolution = (1920, 1080)
        self.camera_path = "/World/RenderCamera"
        self.camera = None

        print(f"Camera setup initialized with repository at: {repo_path}")
        print(f"Images will be saved to: {self.output_dir}")

    def create_camera(self):
        ''' 
        create a camera in the scene aimed at the mussel
        '''

        print("Setting up camera...")

        try:
            # create camera with initial position
            self.camera = Camera(
                prim_path=self.camera_path,
                position=np.array([0.5, 0.5, 0.5]),  # starting position
                frequency=30,
                resolution=self.resolution,
            )
            self.camera.initialize()

            # find the object position
            stage = omni.usd.get_context().get_stage()
            obj_prim = stage.GetPrimAtPath("/World/clean_object")

            if obj_prim.IsValid():
                # get the bounding box center of the object 
                bbox = UsdGeom.BBoxCache(0, includedPurposes=[UsdGeom.Tokens.default_]).ComputeWorldBound(obj_prim)
                center = bbox.GetRange().GetMidpoint()
                target = np.array([center[0], center[1], center[2]])
                
                # adjust camera distance based on object size
                size = bbox.GetRange().GetSize()
                max_dim = max(size[0], size[1], size[2])
                camera_distance = max(max_dim * 3, 0.5)  # At least 3x the object's largest dimension
                
                # position camera relative to object
                position = target + np.array([camera_distance, camera_distance, camera_distance/2])
                self.camera.set_world_pose(position=position)

            else:
                # fallback to origin if object can't be found
                target = np.array([0.0, 0.0, 0.0])
                print("Warning: Could not find clean_object, aiming at origin instead")

            # set up direction and orientation
            up = np.array([0.0, 0.0, 1.0]) # Z-up

            # calculate rotation to look at the target 
            rotation_matrix = look_at(self.camera.get_world_pose()[0], target, up)
            orientation = matrix_to_quaternion(rotation_matrix)

            # update camera orientation
            self.camera.set_world_pose(position=self.camera.get_world_pose()[0], orientation=orientation)

            print(f"Camera set up successfully! pointing at {target}")
            return True
        except Exception as e:
            print(f"Error setting up camera: {str(e)}")
            return False

    def get_camera(self):
        '''
        returns the camera object or none if not created
        '''
        return self.camera

if __name__ == "__main__":
    # create and set up camera
    setup = CameraSetup
    setup.create_camera()