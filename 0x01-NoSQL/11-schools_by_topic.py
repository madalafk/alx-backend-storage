#!/usr/bin/env pytho
"""
Python function that returns the list of
school having a specific topic
"""
import pymongo


def schools_by_topic(mongo_collection, topic):
    """
    searching by topic
    """
    return mongo_collection.find({"topics": topic})
