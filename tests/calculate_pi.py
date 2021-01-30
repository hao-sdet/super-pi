# Calculating Pi with Leibniz Series
# 1 - (1/3) + (1/5) - (1/7) + ... = pi/4

# Source: https://gist.github.com/jcchurch/930276

from mpi4py import MPI

comm = MPI.COMM_WORLD
rank = comm.rank
size = comm.size

slice_size = 10000
total_slices = 100

def calculate_slice(n, size):
    i, value = 0, 0
    while i < size:
        k = n * size + i
        if i % 2 == 0:
            value += 1.0 / (2*k + 1)
        else:
            value -= 1.0 / (2*k + 1)
        i += 1

    return value

# master node
if rank == 0:
    pi = 0
    slice, process = 0, 1
    # Send the first batch of processes to the nodes.
    while process < size and slice < total_slices:
        comm.send(slice, dest=process, tag=1)
        slice += 1
        process += 1

    # Wait for worker nodes to return with result
    received_processes = 0
    while received_processes < total_slices:
        pi += comm.recv(source=MPI.ANY_SOURCE, tag=1)
        process = comm.recv(source=MPI.ANY_SOURCE, tag=2)
        received_processes += 1

        # continue sending the remaining slices, if any
        if slice < total_slices:
            comm.send(slice, dest=process, tag=1)
            slice += 1

    # Send the shutdown signal
    for process in range(1,size):
        comm.send(-1, dest=process, tag=1)

    print('PI = {0}'.format(4.0 * pi))

# Worker nodes
else:
    while True:
        message = comm.recv(source=0, tag=1)
        if message == -1: break

        # compute each slice
        s = message
        print('[Process#{0}]> Calculating slice {1}'.format(rank, s))
        value = calculate_slice(s, slice_size)

        # return slices value to master node
        comm.send(value, dest=0, tag=1)
        comm.send(rank, dest=0, tag=2)
