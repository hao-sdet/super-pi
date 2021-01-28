#!/usr/bin/env python
import os
import time
import hashlib
from enum import Enum
from mpi4py import MPI

#TODO: At the current state of this script, it doesn't update the number of passwords cracked
# for the last password batch when the number of passwords in this batch 
# are less than the number of workers (see line 54, 59 and 70). 

# files
password_dictionary_file = '/home/pi/password_cracker/password_dictionary.txt'
sh256_encrypted_password_file = '/home/pi/password_cracker/sha256_hashed_passwords_2k.txt'

# mpi4py
comm = MPI.COMM_WORLD
rank = comm.rank
size = comm.size

def crack_encrypted_password(encrypted_password, dictionary_file):
    """
    Cracks sha256 encrypted password
    :return True if password is cracked and False otherwise
    """
    try:
        file = open(dictionary_file, 'r')
    except IOError:
        print('Could not open the dictionary file!')
    else:
        for password in file:
            hashed_password = hashlib.sha256(password.strip().encode('utf8')).hexdigest()
            if hashed_password == encrypted_password:
                print('Password for {1} is {2}'.format(rank, encrypted_password, password.strip()))
                return True
        else:
            print('Could not crack the encrypted password: {0}'.format(encrypted_password))
            return False
    finally:
        file.close()

# master node
if rank == 0:
    no_cracked_passwords = 0
    end_of_line_reached = False
    encrypted_password_file = open(sh256_encrypted_password_file, 'r')
    start_time = time.time()
    while True:
        # send the encrypted passwords worker nodes
        for process in range(1, size):
            line = encrypted_password_file.readline().strip()
            if line == '':
                end_of_line_reached = True
            else:
                comm.send(line, dest=process, tag=1)
        # wait for all processes to return with result
        received_processes = 1
        while received_processes < size and end_of_line_reached is False:
            process = comm.recv(source=MPI.ANY_SOURCE, tag=1)
            result = comm.recv(source=MPI.ANY_SOURCE, tag=2)
            if result:
                # keep track of the number of cracked passwords
                no_cracked_passwords += 1

            # repeat for the remaining processes
            received_processes += 1

        # check for EOL
        if end_of_line_reached:
            break

    # close the file
    encrypted_password_file.close()

    # shutdown all processes
    for process in range(1, size):
        comm.send(-1, dest=process, tag=1)

    # show the results
    print('------------------------------------')
    print('> Total passwords have cracked: {0}'.format(no_cracked_passwords))
    print('> Total time: {0} seconds'.format(round((time.time() - start_time), 2)))
    print('------------------------------------')

# worker nodes
else:
    # run until all passwords are cracked (signal by the master)
    while True:
        message = comm.recv(source=0, tag=1)
        if message == -1: break

        # encrypted password received from master
        encrypted_password = message

        # let the cracking begin!
        result = crack_encrypted_password(encrypted_password, password_dictionary_file)

        # send result to master
        comm.send(rank, dest=0, tag=1)
        comm.send(result, dest=0, tag=2)
