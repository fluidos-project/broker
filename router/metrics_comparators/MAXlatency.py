from .abstract_comparator import BaseComparator

class LatencyComparator(BaseComparator):
    def compare(self, value, message):
        #implement here the comparator for the specific key the file must be named as the KEY from the RULES message, 
        #update the message (announcement) key to compare
        return value >= int(message['latency'])
        
comparator = LatencyComparator()
