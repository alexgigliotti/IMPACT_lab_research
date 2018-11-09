# Import libraries
import bge
import numpy as np

''' General properties, constants, and references '''
# Some references
cont = bge.logic.getCurrentController() # Logic for each object. This is where "Sticky" property is stored
own = cont.owner # Blender shortcut
step = 1/60 # Bullet physics time step

# Binder Properties
eta = 1.5 # Viscosity
Gs = 0.1 #25 # Shear relaxation modulus
tau = 0.1 #0.3  # Characteristic time constant; the binder's elastic "memory"
sig = 2.5*10**-4 # Surface tension, N/cm

# General Dimensions
y = 0.08 # cm, collision margin set in Blender is 0.4 mm. For a collision the total gap would be 0.8 mm.
tol_rel = 2 # Sticky margin/ relative tolerance in cm(?). Aggregate collision margins are 4 mm.

# Model Constants
c = 100 #7000 # Constant from normal force/surface tension model


''' Function: sticky '''
# Function applies the sticky force and damping to sticky objects
def sticky():
    # Need to check if object has "Sticky" property
    if 'Sticky' in own and own['Sticky'] is True:
        scene = bge.logic.getCurrentScene() # Reference to Blender scene

        # Loop through all objects
        for obj in scene.objects:

            # If the object is not its self and it is a sticky object then check distance away
            if obj.name != own.name and 'Sticky' in obj and obj['Sticky'] is True:
                d_vec = obj.worldPosition - own.worldPosition # Distance away from 2 objects in vector form
                d_rel = np.sqrt(d_vec[0]**2 + d_vec[1]**2 + d_vec[2]**2) # Magnitude of distance
                unit_vec = d_vec/d_rel # Normed distance

                # Check if aggregates close enough to stick and have collided
                if obj.sensors["CheckCollision"].positive and d_rel < tol_rel:

                    # Get current aggregate data from globals
                    aggregate_mass = obj.mass
                    aggregate_surface_area = obj["surface_area"]
                    #print(obj.name)
                    #print(aggregate_surface_area, "\n")

                    # Assign sticky surface area based on smallest aggregate in collision list
                    collision_list = obj.sensors["CheckCollision"].hitObjectList  # Generate list of collisions for each object

                    surface_area_check_list = [i.get('surface_area') for i in collision_list]
                    surface_area_check_list.append(obj.get("surface_area"))


                    sticky_surf_area = min(float(area) for area in surface_area_check_list)

                    time_step = obj['Timer']  # Iteration counter/time step from Blender Logic Editor, updated later so it is remembered on each iteration

                    # Apply shear damping
                    damping(aggregate_mass, aggregate_surface_area, time_step, obj)

                    # Apply sticky force
                    force_sticky = -c * ((sticky_surf_area / 2) ** 0.5) * sig * unit_vec  # Calculate sticky force; add the negative so that the force points towards the object!
                    obj.applyForce(force_sticky, 0) # Apply the force to the center of mass of object

                    time_step += 1
                    obj["Timer"] = time_step

                else: # Not touching anything
                    force_sticky = np.zeros(3)  # Set Sticky force to zero
                    obj.applyForce(force_sticky, 0)  # Apply the force to the center of mass of objects
                    time_step = 0
                    obj["Timer"] = time_step

            else:
                pass
    else:
        pass


'''Function: damping'''
# Called from the "sticky" function. Applies linear and angular damping
def damping(m, surface_area, t_step, obj):
    t = t_step * step # Calculate time
    alpha = eta * surface_area / y

    # Set linear damping
    vo = obj.getLinearVelocity(False)
    v = vo * np.exp(-t * alpha / m) # Apply linear damping factor
    obj.setLinearVelocity(v, False)

    # Set angular damping
    wo = obj.getAngularVelocity(False)
    w = wo * np.exp(-t * alpha / m) # Apply angular damping factor
    obj.setAngularVelocity(w, False)


''' Main Program '''
sticky()