# Environment  

- Ubuntu 18.04.1 LTS  
- Python3.6.5  
- pymmh3 (https://github.com/wc-duck/pymmh3)  
- redis5.0.3 (https://redis.io/)  
- PyPIredis3.2.0 (https://pypi.org/project/redis/)

# Motivation  

Learn how to use ST(Spatiotemporal)-code for in-memory KVS redis.  
1. How to insert ST-code with value using sorted set.  
2. How to search value using ST-code.  

## 1. How insert works  

Insertion is conducted by using ZADD command available for redis.  
ZADD can be used to KEY and SCORE for secondary indexing.  
When using ZADD, we apply...  
- KEY : PRE-code of ST-code defined via "split-precision"   
- SCORE : SUF-code of ST-code defined via "split-precision"  
- VALUE : any value you want to store  

<img src="https://github.com/sushi-boy/stcode-redisconf19/blob/master/img/insert.PNG" width="720">

## 2. How search works  
