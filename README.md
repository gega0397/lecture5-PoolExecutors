# lecture5-PoolExecutors

both main.py and main1.py utilize same overall logic, main() function executes _executor(), which is responsible to spawn new processes using ProcessPoolExecutor and split load on all process evenly.
Each process execute process_requests(), which spawns new threads using ThreadPoolExecutor and calls get_product(), which is responsible to make request and retrieve data.

the different lies in the error handling, if requests are rejected due to ovewhelming requests to the endpoint, main.py runs process_requests() recursively and spawns new threads for failed requests, this time using
threading.Semaphore to limit request limit. Parameter "max_rec" is decremented with each recursion to avoid overflow.
In case of main1.py, all failed requests are passed to _executor, which spawns new processes for failed requests and distributes load on each process evenly.
e.g.: for main.py if 20 requests fail on one process and rest finish successfully, 20 requests will be recusively requested on 1 thread, for main1.py failed requyests will be passed to parent and it will again redistribute 20 requests separate processes.

To do: Housekeeping logic in case of reaching max recursion.
