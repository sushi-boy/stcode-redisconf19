input = [40.7212905884, -73.8441925049, 1451575386]
maxmin = [(-90,90), (-180,180),(0,2018304000)]
precision = 90

def stencode_fast(input, maxmin,precision):
    bins=[]
    precision = int(precision/3)
    for (i, m) in zip (input, maxmin):
        tmp = (i-m[0])/(m[1]-m[0])*(2**precision)
        tmp = format(int(tmp),'b')
        n_lost = precision-len(tmp)
        bins.append('0' * n_lost + tmp)
    st_code = ''.join(b1+b2+b3 for b1,b2,b3 in zip(bins[0],bins[1],bins[2]))
    return st_code

# print
print(stencode_fast(input, maxmin,precision))
