#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 16 10:00:59 2024

@author: stevenwaal
"""






def mix_list(list_to_mix, mixing_index):
    '''
    A function that mixes lists. It is best described by an example:
        
        Example:
        list_to_mix = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14]
        mixing_index = 4
            
        The function first slices list_to_mix into 'mixing_index' number of
        semi-equal length lists. In this case, we divide list_to_mix into 4
        lists: three of legnth 4, one of lenght 3:
            
        sliced_lists: (number of sliced lists = mixing_index)
            [ 0,  1,  2,  3]
            [ 4,  5,  6,  7]
            [ 8,  9, 10, 11]
            [12, 13, 14]
        
        The sliced lists are then combined in alternating order: first element
        of the first list, first element of the second list, and so on. The
        final output is:
            
            Output: [0, 4, 8, 12, 1, 5, 9, 13, 2, 6, 10, 14, 3, 7, 11]

    Parameters
    ----------
    list_to_mix : list
        The list that you want to mix up.
    mixing_index : int
        An integer describing how much to mix the list. The function will break
        up list_to_mix into 'mixing_index' number of semi-equal chunks, and
        then add them together.
        
        Limits: 0 < mixing_index < ????? (definitely can't be longer than the
                                          list length, but I don't know exactly
                                          know what the upper bound should be)

    Returns
    -------
    mixed_list : list
        The mixed list.

    '''
    
    if mixing_index <=0:
        raise Exception('ERROR: mixing_index out of range. Choose a value on the interval 0 < mixing_index < ??')
    if type(mixing_index) != int:
        raise Exception('ERROR: mixing_index must be an integer. Choose a value on the interval 0 < mixing_index < ??')
    
    # Create list of lengths
    list_length = len(list_to_mix)
    lengths = []
    remainder = list_length%mixing_index
    divide = int(list_length/mixing_index)
    
    for i in range(mixing_index):
        if remainder != 0:
            lengths.append(divide+1)
            remainder = remainder - 1
        else:
            lengths.append(divide)
    
    # Slice list_to_mix using list_length values
    sliced_lists = []
    start = 0
    stop = 0
    step = 1
    for value in lengths:
        start = stop
        stop = stop + value
        sliced_lists.append(list_to_mix[start:stop:step])

    # Mix sliced_lists together to create mix_list
    mixed_list = []
    for j in range(len(sliced_lists[0])):
        for i in range(len(sliced_lists)):
            try:
                mixed_list.append(sliced_lists[i][j])
            except:
                # Index out of range
                pass
    
    return mixed_list
    
if __name__ == '__main__':
    
    mixing_index = 2
    list_to_mix = [0,1,2,3,4]
    output = mix_list(list_to_mix, mixing_index)
    print(f'mixing_index: {mixing_index}')
    print(f'list_to_mix:  {list_to_mix}')
    print(f'Output:       {output}')
    assert output == [0,3,1,4,2]