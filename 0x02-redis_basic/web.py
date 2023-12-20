#!/usr/bin/env python3
"""
Implementing an expiring web cache and tracker
using a get_page function
(prototype: def get_page(url: str) -> str:).
"""

import requests
import time
from functools import wraps
import redis

# Global Redis connection
REDIS_CLIENT = redis.StrictRedis(host='localhost', port=6379, db=0)

def cache_and_count(func):
    '''
    A decorator that caches the result of a function with an expiration time of 10 seconds
    and keeps track of the access count for a particular URL using Redis.

    Parameters:
        func (callable): The function to be decorated.

    Returns:
        callable: The decorated function.
    '''
    @wraps(func)
    def wrapper(url):
        '''
        Wrapper function that adds caching and counting functionality.

        Parameters:
            url (str): The URL to fetch the content from.

        Returns:
            str: The content of the URL.
        '''
        cache_key = f'count:{url}'

        # Check if content is in the Redis cache and not expired
        cached_data = REDIS_CLIENT.get(cache_key)
        if cached_data and float(cached_data.decode('utf-8').split(',')[0]) + 10 > time.time():
            # Increment the access count and return the cached content
            access_count = int(cached_data.decode('utf-8').split(',')[1]) + 1
            REDIS_CLIENT.set(cache_key, f"{time.time()},{access_count}")
            return REDIS_CLIENT.get(cache_key).decode('utf-8').split(',')[2]

        # Fetch the content from the original function
        content = func(url)

        # Update the Redis cache with the new content, access count, and timestamp
        access_count = 1
        REDIS_CLIENT.set(cache_key, f"{time.time()},{access_count},{content}")

        return content

    return wrapper

@cache_and_count
def get_page(url: str) -> str:
    '''
    Fetches the HTML content of a URL and applies caching and counting using Redis.

    Parameters:
        url (str): The URL to fetch the content from.

    Returns:
        str: The content of the URL.
    '''
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        return f"Error: {response.status_code}"

if __name__ == "__main__":
    # Example usage
    slow_url = "http://slowwly.robertomurray.co.uk/delay/5000/url/http://www.google.com"
    
    for _ in range(3):
        content = get_page(slow_url)
        access_count = REDIS_CLIENT.get(f'count:{slow_url}').decode('utf-8').split(',')[1]
        print(f"Content:\n{content}\nAccess Count: {access_count}\n")

    fast_url = "http://www.google.com"
    
    for _ in range(3):
        content = get_page(fast_url)
        access_count = REDIS_CLIENT.get(f'count:{fast_url}').decode('utf-8').split(',')[1]
        print(f"Content:\n{content}\nAccess Count: {access_count}\n")
