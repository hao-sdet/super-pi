# Estimating integrals using the trapezoidal rule with MPI
# Source: http://www.acme.byu.edu/wp-content/uploads/2015/10/Lab13.pdf

# Usage:
# $ mpiexec -n 4 python trapezodial_parallel.py

from mpi4py import MPI
import numpy as np

# An arbitrarily function
def function(x):
    return x * x

#  Integrates the function f using the trapezoid rule
def integrate_range(f, a, b, n):
    endpoints = np.linspace(a, b, n+1)
    integral = sum(f(x) for x in endpoints)
    integral -= (f(a) + f(b))/2
    integral *= (b - a)/n

    return integral

# mpi4py
comm = MPI.COMM_WORLD
rank = comm.rank
size = comm.size

a, b = 0.0, 1.0         # evaluate from 0 -> 1 
n = 10000               # subintervals
h = (b - a) / n         # step size
trapezoids = n / size   # trapezoids per process

# Start and end of this process' integration range
start = a + rank * trapezoids * h
end = start + trapezoids * h

integral = np.zeros(1)
buffer = np.zeros(1)

# Perform local computation, each process integrates its own interval
integral[0] = integrate_range(function, start, end, trapezoids)

# master node
if rank == 0:
    total = integral[0]
    process = 1
    while process < size:
        buffer = comm.recv(source=MPI.ANY_SOURCE, tag=1)
        total += buffer[0]
        process += 1

    print('With {0} trapezoids, the estimate of the integral of x^2 from {1} to {2} is: \n\t{3}'.format(n, a, b, total))

# worker nodes
else:
    comm.send(integral, dest=0, tag=1)
