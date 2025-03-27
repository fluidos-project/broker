from .abstract_comparator import BaseComparator

class DefaultComparator(BaseComparator):
    def compare(self, *args, **kwargs):
        return False

comparator = DefaultComparator()
