from .abstract_comparator import BaseComparator

class DefaultComparator(BaseComparator):
    #if no file is found with a specific name corresponding to that key, False is returned as default
    def compare(self, *args, **kwargs):
        return False

comparator = DefaultComparator()
