from Server import Server
from Client import Client

threads = []

# Create new threads
thread1 = Server(1, "Thread-1", 1)
thread2 = Client(2, "Thread-2", 2)

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