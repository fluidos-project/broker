from .abstract_comparator import BaseComparator

class LatencyComparator(BaseComparator):
    def compare(self, value, message):
        #implement here the comparator for the specific key 
        #the file must be named as the KEY from the RULES message

        return value >= int(message.get("latency",10000))
        
comparator = LatencyComparator()
