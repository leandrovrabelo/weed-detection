#!/usr/bin/python3

import numpy as np

def find_values_to_adjust(base_map, 
                        spray_map, 
                        range_photo_basis=0, 
                        photo_resized_param=0,
                        phis_dist=0):
    
    '''Printing starts from below, so if the real spray starts at index -3 and base spray map 
    starts at -2, there is a delay of 1 index to be adjusted on the base spray.
    
    The base spray should start at -1 to spray correctly at -2 (which is correct compared 
    to the suposed base map).
    
    When we talk about stop spraying, when the base map stops at -3 and the real spray 
    stops at -4 there is a delay in stop spraying.
    
    The base spray should stop spraying at -2 to spray correctly at -3 (which is correct 
    compared to the suposed base map).
    
    The problem is that the stop system has to filter each non zero number to stop spraying 
    correctly each square in each line.
    
    I'm considering the first value for the start and stop in each line as a basis for
    other values in the same line.'''

    # Creating a lower and upper band to compare the infer photo with the check photo (by index)
    upper_level = int(range_photo_basis * photo_resized_param)
    lower_level = int((range_photo_basis - 1) * photo_resized_param)

    # Where spray first appears
    start_base = []
    start_spray = []
    
    # Where spray stops
    end_base = []
    end_spray = []
    
    sprayers = len(base_map[0,:])
    
    # I'm considering the first value of each sprayer as a basis for everything
    # it starts counting for the last value until the first.
    for sprayer in range(sprayers):
        if len(np.where(base_map[lower_level : upper_level, sprayer] != 0)[0]) == 0:
            start_base.append(0)
            end_base.append(0)
        else:
            start_base.append((np.where(base_map[lower_level : upper_level, sprayer] != 0)[0][-1]))
            end_base.append((np.where(base_map[lower_level : upper_level, sprayer] != 0)[0][0]))
            
        if len(np.where(spray_map[lower_level + phis_dist : upper_level + phis_dist, ] != 0)[0]) == 0:
            start_spray.append(0)
            end_spray.append(0)
        else:
            start_spray.append((np.where(spray_map[lower_level + phis_dist: upper_level + phis_dist, sprayer] != 0)[0][-1]))
            end_spray.append((np.where(spray_map[lower_level + phis_dist: upper_level + phis_dist, sprayer] != 0)[0][0]))
    
    start_base = np.array(start_base)
    start_spray = np.array(start_spray)
    
    # if positive the spray began later
    diff_start = start_base - start_spray
    
    end_base = np.array(end_base)
    end_spray = np.array(end_spray)
    
    # if positive the spray stopped later
    diff_end = end_base - end_spray

    # To get the correct difference on DIFF_END I have to correct it 
    # with the DIFF_START to put it on the same basis
    diff_end -= diff_start 

    print('[WEEDS] Calibration to START spraying:', diff_start)
    print('[WEEDS] Calibration to FINISH spraying', diff_end)
    
    return diff_start, diff_end    


def find_values_to_adjust_by_index(base_map, 
                                spray_map, 
                                range_photo_basis=0, 
                                photo_resized_param=0,
                                phis_dist=0):

    # Creating a lower and upper band to compare the infer photo with the check photo (by index)
    upper_level = int(range_photo_basis * photo_resized_param)
    lower_level = int((range_photo_basis - 1) * photo_resized_param)
    
    # Creating the basis to extract the indexes with values different than 0 on the
    # base and spray maps
    spray_array = np.array([0])
    base_array = np.array([0])

    for sprayer in range(len(spray_map[0,:])):
        spray_array = np.append(spray_array,(np.where(spray_map[lower_level + phis_dist: upper_level + phis_dist, sprayer] != 0)[0]))
        base_array = np.append(base_array,(np.where(base_map[lower_level : upper_level, sprayer] != 0)[0]))
    
    # Taking the first and last values for each column with values different than 0 on the SPRAY map  
    end_spray = [spray_array[0]]
    start_spray = [spray_array[-1]]

    for idx, valor in enumerate(spray_array):
        if idx+1 == len(spray_array):
            break
        if spray_array[idx+1] < spray_array[idx]:
            end_spray.append(spray_array[idx+1])
            start_spray.append(spray_array[idx])

    # Getting its mean
    end_spray = np.mean(end_spray)
    start_spray = np.mean(start_spray)
    
    # Taking the first and last values for each column with values different than 0 on the BASE map
    end_base = [base_array[0]]
    start_base = [base_array[-1]]

    for idx, valor in enumerate(base_array):
        if idx+1 == len(base_array):
            break
        if base_array[idx+1] < base_array[idx]:
            end_base.append(base_array[idx+1])
            start_base.append(base_array[idx])

    # Getting its mean
    end_base = np.mean(end_base)
    start_base = np.mean(start_base)
 
    # Taking the differences, this is going to be the basis to correct the process of sprays
    dif_end = int(round(end_base - end_spray,0))
    dif_start = int(round(start_base - start_spray,0))

    # Creating arrays with equal values
    start = np.full((len(base_map[0,:]),), dif_start)
    end = np.full((len(base_map[0,:]),), dif_end)

    print('[WEEDS] Calibration to START spraying:', start)
    print('[WEEDS] Calibration to FINISH spraying', end)
    
    return start, end

    
def turn_on(bbox_map, 
            start_diff=0):
    '''This function transforms the extracted bounding box from the photo and corrects
    the map with previous difference captured from other photos.
    
    It will correct each individual sprayer according to its difference between the original
    map and the sprayed.
    
    paramns:
    -----------
    
    bbox_map: Original map created from the bounding boxes extracted from the inference.
    start_diff: The difference captured from other photos (real x sprayed).
    
    Returns:
    -----------
    
    New map with the adjustments.'''
    
    sprayers = len(bbox_map[0,:])
    
    # Transforming in list to add and remove lines easier
    new_bbox = []
    for i in range(sprayers):
        new_bbox.append(bbox_map[:,i])

    # Adding values to correct the delay in printing in each column
    for i in range(sprayers):
        
        if start_diff[i] >= 0:
        
            # I have to insert ZEROS from the beggining to correct delays
            new_bbox[i] = np.insert(new_bbox[i], 0, np.zeros(start_diff[i]))
        
            # And after that I also have to delete the same quantity of lines
            # from the last values.
            new_bbox[i] = np.delete(new_bbox[i], slice((len(new_bbox[i])-start_diff[i]),
                                                       len(new_bbox[i])))
        
        else:
            new_bbox[i] = np.delete(new_bbox[i], np.zeros_like(np.abs(start_diff[i]), dtype=np.int32))
            new_bbox[i] = np.insert(new_bbox[i], start_diff[i], np.zeros(np.abs(start_diff[i])))
        
    new_bbox = np.array(new_bbox).T
    return new_bbox


def turn_off(bbox_map, 
            end_diff=0):
    '''This function is executed after the function TURN ON, it deletes values that are supposed
    to print more than it should.
    
    paramns:
    -----------
    
    bbox_map: The map created after the TURN ON FUNCTION from the bounding boxes extracted 
    from the inference.
    end_diff: The difference captured from other photos (real x sprayed).
    
    Returns:
    -----------
    
    New map with the adjustments.
    '''
    # These are the indices that are non-zero, we will use it as basis to ZERO values sprayed more than it should
    sprayers = len(bbox_map[0,:])
    
    non_zero = []
    for sprayer in range(sprayers):
        if sum(bbox_map[:,sprayer]) == 0:
            non_zero.append([x+1 for x in range(len(bbox_map[sprayer,:]))])
        else:
            non_zero.append(np.array(np.where(bbox_map[:,sprayer] != 0))[0].tolist())
    
    # Creating a index basis to exclude the values
    base_total = []

    # I'm considering just the first non zero index of each square, it will be the basis
    # to turn off the sprayers X dots before it should.
    for sprayer in range(sprayers):
        base_total.append([])
        lenght_line = len(non_zero[sprayer])
        
        for value in range(lenght_line):
            if (non_zero[sprayer][value] - non_zero[sprayer][value-1]) != 1:
                base_total[sprayer].append(non_zero[sprayer][value])

    # This is the adjusted bbox map (with the turn of function) that will be the basis to make the
    # final adjustment
    new_bbox_map = bbox_map.copy()

    for column in range(sprayers):
        for sprayer in base_total[column]:
            new_bbox_map[sprayer:sprayer+end_diff[column], column] = 0
    
    return new_bbox_map

def calibrate(base_map, 
            start, 
            end):
    '''It adjusts the values to be sprayed on the field according to the
    errors captures in earlier sprays.'''
    initial_bbox = turn_on(base_map, start)
    final_bbox = turn_off(initial_bbox, end)
    
    return final_bbox
