# Import libraries
import bge
import numpy as np

''' General properties, constants, and references '''
# Some references
cont = bge.logic.getCurrentController() # Logic for each object. This is where "Sticky" property is stored
own = cont.owner # Blender shortcut
step = 1/24 # Bullet physics time step

# Binder Properties
eta = 1.5 # Viscosity
Gs = 0.1 #25 # Shear relaxation modulus
tau = 0.1 #0.3  # Characteristic time constant; the binder's elastic "memory"
sig = 2.5*10**-4 # Binder surface tension, N/cm

# General Dimensions
y = 0.08 # cm, collision margin set in Blender is 0.4 mm. For a collision the total gap would be 0.8 mm.
tol_rel = 2 # Sticky margin/ relative tolerance in cm(?). Aggregate collision margins are 4 mm.

# Model Constants
c = 100 #7000 # Constant from normal force/surface tension model


''' Function: main '''
# Function applies the cohesive and viscous forces to the object
def main():

    # Double check that own object has "Sticky" property
    if 'Sticky' in own and own['Sticky'] is True:

        # Check if object is colliding with anything
        if own.sensors["CheckCollision"].positive:
            collision_list = own.sensors["CheckCollision"].hitObjectList  # Generate list of collisions for each object

            for collision_obj in collision_list:

                # Need to check if collision object has "Sticky" property, otherwise skip it
                if 'Sticky' in collision_obj and collision_obj['Sticky'] is True:

                    # Get current aggregate data from Blender
                    aggregate_mass = collision_obj.mass
                    aggregate_surface_area = collision_obj["surface_area"]
                    # print(obj.name)
                    # print(aggregate_surface_area, "\n")

                    # Assign sticky surface area based on smallest aggregate in collision list
                    surface_area_check_list = [objt.get('surface_area') for objt in collision_list]
                    surface_area_check_list.append(collision_obj.get("surface_area"))
                    sticky_surf_area = min(float(area) for area in surface_area_check_list)

                    # Apply cohesive forces
                    cohesive_force(sticky_surf_area, collision_obj)

                    # Apply viscous damping forces
                    time_step = collision_obj['Timer']  # Iteration counter/time step from Blender Logic Editor, updated later so it is remembered on each iteration
                    viscous_force(aggregate_mass, aggregate_surface_area, time_step, collision_obj)

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
        raise ValueError('Object ', own.name, " has forces script applied with no 'Sticky' property.")

    return

'''Function: cohesive forces function'''
# Called from "main" function. Applies binder-to-binder cohesive forces based on dimensional analysis
def cohesive_force(surface_area, obj):
    d_vec = obj.worldPosition - own.worldPosition  # Distance away from 2 objects in vector form
    d_rel = np.sqrt(d_vec[0] ** 2 + d_vec[1] ** 2 + d_vec[2] ** 2)  # Magnitude of distance
    unit_vec = d_vec / d_rel  # Normed distance

    force_sticky = -c * ((surface_area / 2) ** 0.5) * sig * unit_vec  # Calculate sticky force; add the negative so that the force points towards the object!
    obj.applyForce(force_sticky, 0)  # Apply the force to the center of mass of object

    return

'''Function: viscous damping function'''
# Called from the "main" function. Applies linear and angular damping based on viscous resistance derivation
def viscous_force(m, surface_area, t_step, obj):
    t = t_step * step # Calculate contact time
    alpha = eta * surface_area / y

    # Set linear damping
    vo = obj.getLinearVelocity(False)
    v = vo * np.exp(-t * alpha / m) # Apply linear damping factor
    obj.setLinearVelocity(v, False)

    # Set angular damping
    wo = obj.getAngularVelocity(False)
    w = wo * np.exp(-t * alpha / m) # Apply angular damping factor
    obj.setAngularVelocity(w, False)

    return

''' Main Program '''
main()
