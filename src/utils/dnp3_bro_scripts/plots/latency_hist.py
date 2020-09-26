import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
import sys
import json

x = []
with open(sys.argv[1], "r") as infile:
    for l in infile.readlines():
        bro_dict = json.loads(l)
        x.append(bro_dict['latency']*1000)

# the histogram of the data
n, bins, patches = plt.hist(x, 50, facecolor='green', alpha=0.75)


print("Mean Latency:", np.mean(x)) 
print("Stdev Latency:", np.std(x)) 

plt.xlabel('Latency')
plt.ylabel('Frequency')
plt.title('Frequency of Transaction Latency in milliseconds')
plt.grid(True)
plt.yticks(rotation=45)
plt.show()
