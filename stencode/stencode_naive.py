def stencode_naive(lon_input, lat_input, time_input, precision=90):
    lon_interval, lat_interval, time_interval = (-90.0, 90.0), (-180.0, 180.0), (0.0, 2018304000.0)
    st_code = ''
    loop = 0

    while len(st_code) < precision:
        if loop%3 ==0:
            mid = (lon_interval[0] + lon_interval[1]) / 2
            if lon_input > mid:
                lon_interval = (mid, lon_interval[1])
                st_code += '1'
            else:
                lon_interval = (lon_interval[0], mid)
                st_code += '0'
        elif loop%3 == 1:
            mid = (lat_interval[0] + lat_interval[1]) / 2
            if lat_input > mid:
                lat_interval = (mid, lat_interval[1])
                st_code += '1'
            else:
                lat_interval = (lat_interval[0], mid)
                st_code += '0'
        else :
            mid = (time_interval[0] + time_interval[1]) / 2
            if time_input > mid:
                time_interval = (mid, time_interval[1])
                st_code += '1'
            else:
                time_interval = (time_interval[0], mid)
                st_code += '0'
        loop += 1
    return st_code

print(stencode_naive(40.7212905884, -73.8441925049, 1451575386))
