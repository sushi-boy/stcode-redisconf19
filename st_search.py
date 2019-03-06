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
    pre_str = morton_code[:split_precision]
    suf_str = morton_code[split_precision:]    
    return pre_str, suf_str


#search to redis by using ST-code as a key of sorted set
def search(longitude, latitude, time):
    validate_latitude(latitude)
    validate_longitude(longitude)
    validate_time(time)
    
    #calculate base length of bit code by dividing search precision by 3(number of dimensions) 
    base_exp = search_precision/3
    lon_exp = base_exp
    lat_exp = base_exp
    time_exp = base_exp
    
    #create ST-code
    lon_bin_code = create_longitude_binary_code(longitude, int(lon_exp))
    lat_bin_code = create_latitude_binary_code(latitude, int(lat_exp))
    time_bin_code = create_time_binary_code(time, int(time_exp))
    morton_code = create_morton_code(lon_bin_code, lat_bin_code, time_bin_code, int(base_exp))
    
    #split ST-code
    code_common, code_vary = set_split_precision(morton_code, split_precision)

    #range of "score" for searching sorted set
    if(not code_vary):
        code_vary_min =  -2**63
        code_vary_max = 2**63-1
    else:
        shift_bits = max_precision - search_precision
        code_vary_min = int(code_vary, 2) << shift_bits
        code_vary_max = int(code_vary, 2)+1 << shift_bits

    #search to redis server
    insert_node_number_list = [i for i in range(0, all_nodes)]
    
    reply = []    
    for i in range(0, all_nodes):
        node_number = insert_node_number_list[i]                
        pool = redis.ConnectionPool(host=REDIS_SRV_IPS[node_number], port=PORT, db=0)
        r = redis.StrictRedis(connection_pool=pool)
        key = code_common
        reply.append(r.zrangebyscore(key, code_vary_min, code_vary_max))
    return reply


if __name__ == "__main__":
    #test
    print(search(135, 35, 5))

