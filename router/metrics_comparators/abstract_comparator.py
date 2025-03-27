from abc import ABC, abstractmethod

class BaseComparator(ABC):
    """Base class comparator"""
    
    @abstractmethod
    def compare(self, value):
        """Comparator method to be implemented"""
        pass
