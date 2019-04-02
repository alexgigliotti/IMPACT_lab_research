# Import libraries
import bge
# For Linux add Anaconda 'site-packages' folder so Blender can use installed modules in conda environment
import sys
sys.path.append('/home/alexgigliotti/Programs/conda/miniconda3/envs/blender_env/lib/python3.6/site-packages')
import numpy as np


class ForcesModel():

    def __init__(self):

        # General properties, constants, and references
        # Some references
        self.cont = bge.logic.getCurrentController()  # Logic for each object. This is where "Sticky" property is stored
        self.own = self.cont.owner  # Blender shortcut
        self.scene = bge.logic.getCurrentScene()  # Reference to Blender scene
        self.step = 1/24  # Bullet physics time step

        # Binder Properties
        self.eta = 1.2  # Viscosity
        self.sig = 2.5*10**-4  # Binder surface tension, N/cm

        # General Dimensions
        self.y = 0.08  # cm, collision margin set in Blender is 0.4 mm. For a collision the total gap would be 0.8 mm.

        # Model Constants
        self.c = 100  # 7000 # Constant from normal force/surface tension model

        self.check_collisions()

        return

    def check_collisions(self):

        own = self.own

        # Double check that own object has "Sticky" property
        if 'Sticky' in own and own['Sticky'] is True:

            # Check if object is colliding with anything
            if own.sensors["CheckCollision"].positive:
                collision_list = own.sensors["CheckCollision"].hitObjectList  # Generate list of collisions for each object

                for collision_obj in collision_list:

                    # Need to check if collision object has "Sticky" property, otherwise skip it
                    if 'Sticky' in collision_obj and collision_obj['Sticky'] is True:

                        # Get current aggregate data from Blender
                        collision_obj_mass = collision_obj.mass
                        collision_obj_mass_surface_area = collision_obj["surface_area"]

                        # Assign sticky surface area based on smallest aggregate in collision list
                        surface_area_check_list = [objt.get('surface_area') for objt in collision_list]
                        surface_area_check_list.append(collision_obj.get("surface_area"))
                        sticky_surf_area = min(float(area) for area in surface_area_check_list)

                        # Apply cohesive forces
                        self.cohesive_force(sticky_surf_area, collision_obj)

                        # Apply viscous damping forces
                        time_step = collision_obj['Timer']  # Iteration counter/time step from Blender Logic Editor, updated later so it is remembered on each iteration
                        self.viscous_force(collision_obj_mass, collision_obj_mass_surface_area, time_step, collision_obj)

                        # Update contact-time time step
                        time_step += 1
                        collision_obj["Timer"] = time_step

                    else:
                        pass

            else:
                # If not colliding with anything, set contact-time to 0
                time_step = 0
                own["Timer"] = time_step

        else:
            raise ValueError('Object ' + str(own.name) + " has forces script applied with no 'Sticky' property.")

        return

    def cohesive_force(self, surface_area, obj):
        # Function: cohesive forces function
        # Called from "main" function. Applies binder-to-binder cohesive forces based on dimensional analysis
        own = self.own
        d_vec = obj.worldPosition - own.worldPosition  # Distance away from 2 objects in vector form
        d_rel = np.sqrt(d_vec[0] ** 2 + d_vec[1] ** 2 + d_vec[2] ** 2)  # Magnitude of distance
        unit_vec = d_vec / d_rel  # Normed distance

        force_sticky = -self.c * ((surface_area / 2) ** 0.5) * self.sig * unit_vec  # Calculate sticky force; add the negative so that the force points towards the object!
        obj.applyForce(force_sticky, 0)  # Apply the force to the center of mass of object

        return

    def viscous_force(self, m, surface_area, t_step, obj):
        # Function: viscous damping function
        # Called from the "main" function. Applies linear and angular damping based on viscous resistance derivation
        t = t_step * self.step  # Calculate contact time
        alpha = self.eta * surface_area / self.y

        # Set linear damping
        vo = obj.getLinearVelocity(False)
        v = vo * np.exp(-t * alpha / m)  # Apply linear damping factor
        obj.setLinearVelocity(v, False)

        # Set angular damping
        wo = obj.getAngularVelocity(False)
        w = wo * np.exp(-t * alpha / m)  # Apply angular damping factor
        obj.setAngularVelocity(w, False)

        return


ForcesModel()
