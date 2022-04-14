import numpy as np
fname = '.tempdata.dat'
#with open(fname) as f
data = np.genfromtxt(fname)
t = (data.transpose()[-1])
x = np.linspace(0, 1, len(t))
print(x)

import matplotlib.pyplot as plt
plt.plot(x, t, '-b')
plt.show()
