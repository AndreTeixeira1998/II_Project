import numpy
from heapq import *


def heuristic(a, b):
    return (b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2

def astar(array, start, goal):

    neighbors = [ (-1,0),(0,1),(0,-1), (1,0),]

    close_set = set()
    came_from = {}
    gscore = {start:0}
    fscore = {start:heuristic(start, goal)}
    oheap = []

    heappush(oheap, (fscore[start], start))
    
    while oheap:

        current = heappop(oheap)[1]

        if current == goal:
            data = []
            while current in came_from:
                data.append(current)
                current = came_from[current]
            return data

        close_set.add(current)
        for i, j in neighbors:
            neighbor = current[0] + i, current[1] + j            
            tentative_g_score = gscore[current] + heuristic(current, neighbor)
            if 0 <= neighbor[1] < array.shape[1]:
                if 0 <= neighbor[0] < array.shape[0]:                
                    if array[neighbor[0]][neighbor[1]] == 1:
                        continue
                else:
                    # array bound y walls
                    continue
            else:
                # array bound x walls
                continue
                
            if neighbor in close_set and tentative_g_score >= gscore.get(neighbor, 0):
                continue
                
            if  tentative_g_score < gscore.get(neighbor, 0) or neighbor not in [i[1]for i in oheap]:
                came_from[neighbor] = current
                gscore[neighbor] = tentative_g_score
                fscore[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                heappush(oheap, (fscore[neighbor], neighbor))
                
    return False

'''
   astar(array, start, destination)
   astar function returns a list of points (shortest path)

'''

""" 
nmap = numpy.array([
    [0,0,0,0,0,0,0,0,0],
    [1,1,0,1,0,1,0,0,1],
    [1,0,0,0,0,0,0,0,0],
    [1,0,0,0,0,0,0,0,0],
    [1,0,0,0,0,0,0,0,0],
    [1,1,0,1,0,1,0,0,1],
    [0,0,0,0,0,0,0,0,0]])
 """
 
nmap = numpy.array([
    [0,0,0,0,0,0,0,0,0],
    [1,1,0,1,0,1,0,0,1],
    [1,0,0,0,0,0,0,0,0],
    [1,0,0,0,0,0,0,0,0],
    [1,0,0,0,0,0,0,0,0],
    [1,1,0,1,0,1,0,0,1],
    [0,0,0,0,0,0,0,0,0]])

start=(0,0)

opt= {"A1": (2,1), "A2": (3,1), "A3": (4,1) }

finish= opt["A2"]

route= astar(nmap, start, finish)

#route = route + [start]

route = route[::-1]

print("## PATH: ", route)


""" 
char = [  1,  3,  8, 15, 20, 27, 32, 39, 40,
         99, 99,  9, 99, 21, 99, 33, 41, 99,
         99,  4, 10, 16, 22, 28, 34, 42, 48,
         99,  5, 11, 17, 23, 29, 35, 43, 49,
         99,  6, 12, 18, 24, 30, 36, 44, 50,
         99, 99, 13, 99, 25, 99, 37, 45, 99,
          2,  7, 14, 19, 26, 31, 38, 46, 47]
 """

char = [  1,  3,  8, 15, 20, 27, 32, 39, 40,
         99, 99,  9, 99, 21, 99, 33, 41, 99,
         99,  4, 10, 16, 22, 28, 34, 42, 48,
         99,  5, 11, 17, 23, 29, 35, 43, 49,
         99,  6, 12, 18, 24, 30, 36, 44, 50,
         99, 99, 13, 99, 25, 99, 37, 45, 99,
          2,  7, 14, 19, 26, 31, 38, 46, 47]


rangox=9
rangoy=7

vec_=[]
for pri in range(rangoy):
    for sec in range(rangox):
        vec_.append((pri,sec))

print("\n\n")

#for n in range(rangoy):       #debug
#    print(vec_[n*rangox:n*rangox+rangox])
#print("\n\n")





#print(decoding)       #debug
decoding = dict(zip(vec_, char))

output=[decoding[C] for C in route]

print("PATH to send: ", output)



print("\n\n") ### Visualization of result init


for r in route:
    nmap[r]=2


nmap[finish]=9

print(nmap) ### Visualization of result end



encoding = dict(zip(char, vec_))

print("\n\n")

print("outputing coordinates of conveyor (#1):", encoding[1])

