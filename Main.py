#import pyLOUS
from Server import Server
from Client import Client
# Threads for Server and client
threads = []

# Create new threads, passing threadID, name, counter
thread1 = Server(1, "Thread-1", 1,1024,20,)
thread2 = Client(2, "Thread-2", 2,1024,0,0,StopWaitReceiver())

# Start new Threads
thread1.start()
thread2.start()

# Add threads to thread list
threads.append(thread1)
threads.append(thread2)

# Wait for all threads to complete
for t in threads:
    t.join()
print("Exiting Main Thread")
