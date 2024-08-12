import numpy as np
import csv
import matplotlib.pyplot as plt
import logging


def descrete_dist_to_corresponding_force(dist: np.array, force: np.array) -> tuple:
    """Algorithm to correlate series of discrete distances to force
    
    Since the distance sensor only samples in terms of 1mm resolution
    we need to bin and average force measurements that correspond to
    1mm increments. For example, there is no differentiation between 
    .1mm and .9mm. To compensate for this we take the second 
    half of force values for dist x-1 and first half of forces
    for x and average them. This gives us a range corresponding to 
    forces for a distance range of x - .5mm to x + .5mm. Credits
    to Steven Waal for working with me to choose this algorithm

    Args:
        dist (np.array): array of uint8 distances < 11
        force (np.array): continious force measurements (np.float)

    Returns:
        tuple: distance array, force array for each unique dist value
        between 0 and 10mm
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    console_handler  = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    
    unique_dists = np.sort(np.unique(dist))
    aggregate_dist = np.zeros(len(unique_dists))
    aggregate_force = np.zeros(len(unique_dists))
    for i in range(len(unique_dists)):
        if i == 0:  # first item should just be 0
            aggregate_dist[i] = unique_dists[i]
            aggregate_force[i] = 0
            continue
        if i == len(unique_dists):
            break
            
        # find indexes where dist match x - .5mm
        mask = (dist == unique_dists[i - 1])
        dist_indexes = np.where(mask)[0]
        first_split = dist_indexes[int(len(dist_indexes) / 2)]

        # now find the second half of x + .5mm force measurements
        upper_mask = (dist == unique_dists[i])
        dist_indexes = np.where(upper_mask)[0]
        second_split = dist_indexes[int(len(dist_indexes) / 2)]

        # handle edge case where i == last element
        if i == 1:
            aggregate_force[i] = np.mean(force[dist_indexes[0]:second_split])
            aggregate_dist[i] = unique_dists[i]
            if np.isnan(aggregate_force[i]):
                logger.info(f"Addressing the Runtime Error by make for sample at dist {unique_dists[i]} = np.mean(force at that dist)")
                aggregate_force[i] = np.mean(force[dist_indexes])
                aggregate_dist[i] = unique_dists[i]  
            continue
        aggregate_force[i] = np.mean(force[first_split:second_split])
        aggregate_dist[i] = unique_dists[i]
        if np.isnan(aggregate_force[i]):
            logger.info(f"Addressing the Runtime Error by make for sample at dist {unique_dists[i]} = np.mean(force at that dist)")
            aggregate_force[i] = np.mean(force[dist_indexes])
            aggregate_dist[i] = unique_dists[i]  

    mask = aggregate_dist <= 10
    aggregate_dist = aggregate_dist[mask]
    aggregate_force = aggregate_force[mask]
    return (aggregate_dist, aggregate_force)

if __name__ == "__main__":

    dist = []
    force = []
    with open("src/fake_data.csv") as f:
        for i in csv.reader(f):
            dist.append(int(i[0]))
            force.append(int(i[1]))
            
    dist = np.array(dist)
    dist = dist.astype("uint8")
    force = np.array(force)
    
    alg_dist, alg_force = descrete_dist_to_corresponding_force(dist, force)
    
    fig, ax = plt.subplots()
    ax.plot(alg_dist, alg_force, label="Algorithm")
    ax.scatter(dist, force, c='orange', alpha=.3, linewidths=.2, label="fake_data")
    ax.legend()
    ax.set_xlabel("Distance (mm)")
    ax.set_ylabel("Force")
    ax.set_title("Spot Checking Algorithm Against Handmade Data")
    # plt.show()