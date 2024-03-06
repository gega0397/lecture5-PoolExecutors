import concurrent.futures
import time
import os
import threading
import requests
import json


def split_requests(count_requests=None, splits=0):
    if isinstance(count_requests, int):
        s = 1
        while splits:
            incr = count_requests // splits
            count_requests -= incr
            e = s + incr
            yield list(range(s, e))
            s = e
            splits -= 1

    elif isinstance(count_requests, list):
        s = 0
        l = len(count_requests)
        incr = l // splits
        while splits:
            e = s + incr if splits > 1 else max(s + incr, l)
            yield count_requests[s:s + incr]
            s = e
            splits -= 1


def timeis(func):
    # Decorator that reports the execution time.
    def wrap(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()

        print(func.__name__, end - start)
        return result

    return wrap


def get_product(id, semaphore=None):
    result, error = None, None
    url = f"https://dummyjson.com/products/{id}"
    try:
        if semaphore:
            with semaphore:
                print(f'Requesting id {id}')
                response = requests.get(url)
        else:
            print(f'Requesting id {id}')
            response = requests.get(url)
    except requests.exceptions.RequestException as e:
        print(f"exception was raised on id {id}: {e}")
        error = id
        return (result, error)

    if response.status_code == 200:
        result = response.json()
    elif response.status_code == 429:
        print(f"failed to fetch product #{id}")
        error = id
    else:
        result = response.json()
        print(f"Unsuccessful request for #{id}, {response.status_code}")
    return (result, error)


def process_requests(_list, _semaphore=None):
    max_workers = len(_list)
    semaphore = None
    if _semaphore:
        semaphore = threading.Semaphore(_semaphore)

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(get_product, i, semaphore) for i in _list]

        result = [future.result()[0] for future in concurrent.futures.as_completed(futures)
                  if future.result()[0] is not None]
        error = [future.result()[1] for future in concurrent.futures.as_completed(futures)
                 if future.result()[1] is not None]

    # if len(failed_ids) > 0:
    #     if _semaphore is None:
    #         _semaphore = 10
    #     results.extend(process_requests(failed_ids, _semaphore=_semaphore))

    return (result, error)


def _executor(max_workers, requests, semaphore=None, max_rec=10):
    i = split_requests(requests, max_workers)
    print(sum(len(output) for output in split_requests(requests, max_workers)))
    data = []
    errors = []
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as e:
        future = [e.submit(process_requests, _list, semaphore) for _list in i]

        for future in concurrent.futures.as_completed(future):
            data.extend(future.result()[0])
            errors.extend(future.result()[1])

    if len(errors) > 0:
        if max_rec:
            semaphore = max(semaphore - 5, 1) if semaphore else 5
            data.extend(_executor(max_workers, errors, semaphore=semaphore, max_rec=max_rec - 1))
        else:
            pass

    return data


@timeis
def main():
    count_cpu = os.cpu_count()
    count_requests = 100
    semaphore = 7
    data = _executor(os.cpu_count() - 1, count_requests, semaphore)
    print(len(data))
    with open("response.json", "w") as f:
        json.dump(data, f)


if __name__ == "__main__":
    main()
