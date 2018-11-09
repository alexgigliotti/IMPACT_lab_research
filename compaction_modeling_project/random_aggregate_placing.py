# Import libraries
import bge
import numpy as np
#import random
#import linecache

# Some references
cont = bge.logic.getCurrentController() # Logic for each object.
own = cont.owner # Blender shortcut to owner of script
scene = bge.logic.getCurrentScene() # Reference to Blender scene

if scene.objects['Empty']["num_agg_total"] >= 1:
    # Get global values from Blender
    agg_total = scene.objects['Empty']["num_agg_total"]
    agg_shape_list = scene.objects['Empty']["shape_list"] # List of sticky aggregates
    ###agg_size_list = [19.1, 15, 12.5, 9.53, 5] JUST USE SCALE FACTORS SAVED ABOVE
    agg_location_list = ["Empty", "Empty.001", "Empty.002", "Empty.003", "Empty.004" , "Empty.005" , "Empty.006", "Empty.007", "Empty.008"] # List of "Empty" names

    # Choose random numbers for aggregate size, shape, and location
    #agg_size_rand = np.random.randint(len(agg_size_totals))
    location_rand = np.random.randint(len(agg_location_list))

    # If a randomly selected size is already completely used, pick another until it works
    #while agg_size_totals[agg_size_rand] <= 0:
    #    agg_size_rand = np.random.randint(len(agg_size_totals))

    # Objects being added must be in an inactive layer! Deselect the base object layer in Blender before running
    scene.addObject(agg_shape_list[agg_total-1], agg_location_list[location_rand], 0)

    # Give placed aggregate correct properties
    #added_obj_name = scene.objects[-1]

    # Decrease size count and total count
    #agg_size_totals[agg_size_rand] -= 1
    agg_total -= 1

    # Send globals back to Blender for next iteration
    scene.objects['Empty']["num_agg_total"] = agg_total

    #print(agg_size_totals)
    #print(agg_total)

else:
    pass