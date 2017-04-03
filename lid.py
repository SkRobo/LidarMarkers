'''Animates distances using single measurment mode'''
from hokuyolx import HokuyoLX
import matplotlib.pyplot as plt
import numpy as np
import math
IMIN = 2000
IMAX = 4000
DMAX = 3000
NORM_LEN_OF_ONE_LINE = 70 #mm
NORM_DISTANCE_BTW_LINE = 40 #mm



def calculate_length_of_element(scan,startindex,endindex):
    square = scan[startindex,1]*scan[startindex,1] + scan[endindex,1]*scan[endindex,1] -2* (scan[startindex,1] * scan[endindex,1] * math.cos(scan[endindex,0] - scan[startindex,0]))
    if square > 0 :
        return math.sqrt(square)
    else:
        return -1
""" detects lens of boards, return len of boards as list in mm"""
def detect_boards(scan):
    i=0 
    lenght = []   
    if scan is not None:
        scan = np.insert(scan,len(scan)*3-1,scan[0,:])
        scan = scan.reshape(len(scan)/3,3)   
        for index in range(0,len(scan[:,0])):
                ## if it is one reflective line
                if (abs(scan[index,1] - scan[index-1,1])<100  ) and (abs(scan[index,0] - scan[index-1,0]))<0.1: 
                    i=i+1
                elif i!=0: ## if a reflective line ended
                    lenght.append(calculate_length_of_element(scan,index-1,index-i))
    return lenght



"""detects number of lines and zeros in board,
 returns in format 1010101 where 1 is line and 0 is zero(no line)  """
def get_params_of_board(scan,print_distbtwlines = False,print_distoflines = False):
    position = [0] #end position of reflective tape 
    dist_btw_lines=[]
    length_of_lines=[]
    if scan is not None:
        #calculate distance between reflective lines
        for line in range(len(scan[:,0])-2):
            if abs(scan[line+1,0] - scan[line,0]) > 0.005: # if line ended
                dist = calculate_length_of_element(scan,line+1,line)
                position.append(line)
                dist_btw_lines.append(dist) 
                dist = calculate_length_of_element(scan,position[len(position)-1],position[len(position)-2])
                length_of_lines.append(dist)
        position.append(len(scan[:,0])-1)
        dist = calculate_length_of_element(scan,position[len(position)-1],position[len(position)-2])
        length_of_lines.append(dist)
        if print_distbtwlines:
            print "dist_btw_lines    ", dist_btw_lines
        if print_distoflines:
            print "length_of_lines   " , length_of_lines
        return dist_btw_lines,length_of_lines

def detect_struct_len_of_element(real_length,Normal_length,tolerance = 0.49):
    temp = real_length//Normal_length
    if abs(real_length - ((temp+1)*Normal_length))<(tolerance * real_length):
        return temp + 1
    else: 
        return temp

def get_struct_of_board(scan,length_of_lines,dist_btw_lines,tolerance = 0.49):
    structure = []
    if len(length_of_lines)-len(dist_btw_lines) != 1:
        return -1
    else :
        total_length = len (length_of_lines)+len (dist_btw_lines)
        length_of_lines = length_of_lines[::-1]
        dist = length_of_lines.pop()
        structure.append(detect_struct_len_of_element(dist,NORM_LEN_OF_ONE_LINE-20))
        for length in dist_btw_lines:
            structure.append(detect_struct_len_of_element(length,NORM_DISTANCE_BTW_LINE))
            dist = length_of_lines.pop()
            structure.append(detect_struct_len_of_element(dist,NORM_LEN_OF_ONE_LINE))
        return structure


"""make filtration based on intensity of recieved signal and its angular position (in radians)"""
def filtrating(scan, limit = 3500,angle_min = -2.4,angle_max = 2.4): 
    t = np.nonzero (scan[:,2] > limit) #return indexes
    scan1=np.array([])
    for element in t[0]:
        if (scan[element,0] > angle_min) and (scan[element,0] < angle_max):
            scan1 = np.insert(scan1,len(scan1),scan[element,:])
    scan1 = scan1.reshape(len(scan1)/3,3)
    if len(scan1) == 0:
        scan1 = None
    #print "scan = ", scan1
    return scan1

def get_colors(intens):
    max_val = intens.max()
    return np.repeat(intens, 3).reshape((4,3))/max_val 

def update(laser, plot, text):
    timestamp, scan = laser.get_filtered_intens(dmax=DMAX)
    maximal_density = scan.max(0)[2]
    print "maximal_density ", maximal_density
    
    treshhold = maximal_density * 0.7
    print "treshhold ",treshhold
    scan = filtrating(scan, limit = treshhold, angle_min = 0, angle_max = 0.9)
    lens = detect_boards(scan)
    print lens

    if lens>0:
        [dist_btw_lines,length_of_lines] = get_params_of_board(scan,True,True)
        if len(length_of_lines)-len(dist_btw_lines) == 1:
            print get_struct_of_board(scan,length_of_lines,dist_btw_lines)
    
    if scan is not None:
        plot.set_offsets(scan[:, :2])
        plot.set_array(scan[:, 2])
        text.set_text('t: %d' % timestamp)
        plt.show()
        plt.pause(0.001)

def run():
    plt.ion()
    laser = HokuyoLX(tsync = False)
    laser.convert_time = False
    ax = plt.subplot(111, projection='polar')
    plot = ax.scatter([0, 1], [0, 1], s=5, c=[IMIN, IMAX], cmap=plt.cm.Reds, lw=0)
    text = plt.text(0, 1, '', transform=ax.transAxes)
    ax.set_rmax(DMAX)   
    ax.grid(True)
    plt.show()
    while plt.get_fignums():
        update(laser, plot, text)
    laser.close()

if __name__ == '__main__':
    run()





# def detect_board(scan):
#     if scan is not None:
#         lens = []
#         i=0
#         for index in range(1,len(scan[:,0])):
#             if (abs(scan[index,1] - scan[index-1,1])<100  ) and (abs(scan[index,0] - scan[index-1,0]))<0.1:
#                 if (index == len(scan[:,0])-1):
#                     square = scan[index,1]*scan[index,1] + scan[index-i,1]*scan[index-i,1] - 2 * (scan[index,1] * scan[index-i,1] * math.cos(scan[index-i,0] - scan[index,0]))
#                     if square>0:
#                         i =math.sqrt(square)
#                         lens.append(i)
#                         i = 0
#                 i=i+1
#             else:

#                 if (i != 0):
#                     square = scan[index,1]*scan[index,1] + scan[index-i,1]*scan[index-i,1] -2* (scan[index,1] * scan[index-i,1] * math.cos(scan[index-i,0] - scan[index,0]))
#                     if square>0:
#                         #if square > 400*400:
#                         i =math.sqrt(square)
                            
#                         lens.append(i)
#                         i = 0
#         print 'lens', (lens)

    # return lens

#     """delete tempororary elements"""
# def delete_nonrelevant(scan):
#     itemindex = []
#     #print "scan",scan
#     temp = np.where(abs(scan[:,0]) < 0.00001) # (array([37, 38, 39, 40, 41, 42, 43, 44]),)
#     #print "temp[0]",temp[0]
#     for index in temp[0]:  # temp[0] is [35 36 37 38 39 40 41 42] and index is number
#         itemindex.append(index)
#     newscan = np.ones((len(scan[:,0]) -len(itemindex),3))
#     #print "len(itemindex)",len(itemindex)
#     j = 0
#     for i in range(0,len(newscan[:,0])):
#         if i+j not in itemindex:
#             newscan[i] = scan[i+j]
#         else:
#             j=j+1
#     #print "(newscan) ", (newscan)

    
#     return newscan