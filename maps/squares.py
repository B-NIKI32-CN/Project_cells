import numpy as np
map = np.zeros([64,64], int)
poses = []
for i in range(4):
    for j in range(4):
        poses.append([i*16,j*16])
# print(poses)
for pos in poses:
    map[pos[0]:pos[0]+7, pos[1]] = 1
    map[pos[0]+9:pos[0]+16, pos[1]] = 1
    map[pos[0]:pos[0]+7, pos[1]+15] = 1
    map[pos[0]+9:pos[0]+16, pos[1]+15] = 1

    map[pos[0], pos[1]:pos[1]+7] = 1
    map[pos[0], pos[1]+9:pos[1]+16] = 1
    map[pos[0]+15, pos[1]:pos[1]+7] = 1
    map[pos[0]+15, pos[1]+9:pos[1]+16] = 1


# print(map)