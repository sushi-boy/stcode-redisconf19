import redis
import glob
import csv
import random
import sys
import copy
from operator import mul
from functools import reduce

try:
    import mmh3
except ImportError:
    import pymmh3.pymmh3 as mmh3

"""
Initialize parameters
"""
#Maximum number of precision bits
max_precision = 96

#Where you split the ST-code into PRE-code and SUF-code
split_precision = 45

#The precision that you want to search in default
search_precision = 48

#Number of nodes
all_nodes = 2

#set IP address of redis    
REDIS_SRV_IPS = [
    'ip1',
    'ip2'    
]

#set port number
PORT = 6379

#set input data path
DATAPATH = 'set path of input data'+'*'

#max and minimum of latitude, longitude, and time
lat_maxmin = (-90.0, 90.0)
lon_maxmin = (-180.0, 180.0)
time_maxmin = (0.0, 2018304000.0)

#function for creating morton-code for each dimension
def create_bin(input_val, maxmin, precision):
    tmp = (input_val - maxmin[0]) / (maxmin[1] - maxmin[0]) * (2**precision)
    return format(int(tmp), '0' + str(precision) + 'b')

#merge all morton-code obtained from each dimension
def merge_bin(*binaries):
    return ''.join((''.join(tuple) for tuple in zip(*binaries)))

#validations
def validate_latitude(latitude):
    if(latitude < lat_maxmin[0] or latitude > lat_maxmin[1]):
        print("latitude is not valid")
        sys.exit()
def validate_longitude(longitude):
    if(longitude < lon_maxmin[0] or longitude > lon_maxmin[1]):
        print("longitude is not valid")
        sys.exit()
def validate_time(time):
    if(time < time_maxmin[0] or time > time_maxmin[1]):
        print("time is not valid")
        sys.exit()

#create ST-code from longitude, latitude, and time        
def create_longitude_binary_code(v, exp):
    return create_bin(v, lon_maxmin, exp)
def create_latitude_binary_code(v, exp):
    return create_bin(v, lat_maxmin, exp)
def create_time_binary_code(v, exp):
    return create_bin(v, time_maxmin, exp)
def create_morton_code(lon_bin_code, lat_bin_code, time_bin_code, base_exp):
    return  merge_bin(lon_bin_code, lat_bin_code, time_bin_code)

#split ST-code depending on split_precision
def set_split_precision(morton_code, split_precision):
    pre_code = morton_code[:split_precision]
    suf_code = morton_code[split_precision:]    
    return pre_code, suf_code


"""
 @prams:
  longitude in degrees(DOUBLE),
  latitude in degrees(DOUBLE),
  time in timestamp(INT),
  value(STRING)
"""

#insert ST-code to redis by using sorted set
def insert(longitude, latitude, time, value):
    validate_latitude(latitude)
    validate_longitude(longitude)
    validate_time(time)
    
    #calculate base length of bit code by dividing max precision by 3(number of dimensions) 
    base_exp = max_precision/3
    lon_exp = base_exp
    lat_exp = base_exp
    time_exp = base_exp
        
    #create ST-code
    lon_bin_code = create_longitude_binary_code(longitude, int(lon_exp))
    lat_bin_code = create_latitude_binary_code(latitude, int(lat_exp))
    time_bin_code = create_time_binary_code(time, int(time_exp))
    morton_code = create_morton_code(lon_bin_code, lat_bin_code, time_bin_code, int(base_exp))

    #split ST-code
    PRE_code, SUF_code = set_split_precision(morton_code, split_precision)

    node_number = 0


    print("Dest:"+REDIS_SRV_IPS[node_number])
    pool = redis.ConnectionPool(host=REDIS_SRV_IPS[node_number], port=PORT, db=0)
    r = redis.StrictRedis(connection_pool=pool)
    key = str(PRE_code)
    print("set key:"+key+" sorted-key:"+str(int(SUF_code,2))+" value:"+value)
    dict = {}
    dict[value] = int(SUF_code,2)
    # ZADD Changed since v3.2.0 !
    r.zadd(key, dict)
    return morton_code
    
#decode ST-code for confirmation
def decoder(code):
    lng_interval = (-180.0, 180.0)
    lat_interval = (-90.0, 90.0)
    time_interval = (0.0, 2018304000.0)

    precision = len(code)
    for i in range(precision):
        remain = i % 3
        if remain == 0: 
            mid_lng_interval = (lng_interval[1] + lng_interval[0]) / 2.0
            if code[i] == '0':
                lng_interval = (lng_interval[0], mid_lng_interval)
            else:
                lng_interval = (mid_lng_interval, lng_interval[1])
        elif remain == 1:
            mid_lat_interval = (lat_interval[1] + lat_interval[0]) / 2.0
            if code[i] == '0':
                lat_interval = (lat_interval[0], mid_lat_interval)
            else:
                lat_interval = (mid_lat_interval, lat_interval[1])
        else:
            mid_time_interval = (time_interval[1] + time_interval[0]) / 2.0
            if code[i] == '0':
                time_interval = (time_interval[0], mid_time_interval)
            else:
                time_interval = (mid_time_interval, time_interval[1])

    lat_val = (lat_interval[0] + lat_interval[1]) / 2.0
    lng_val = (lng_interval[0] + lng_interval[1]) / 2.0
    time_val = (time_interval[0] + time_interval[1]) / 2.0
    return lng_val, lat_val, time_val

if __name__ == "__main__":

    #test
    morton_code = insert(135, 35, 5, '[value]test,135,35,5')
    print(decoder(morton_code))
    
    

                
