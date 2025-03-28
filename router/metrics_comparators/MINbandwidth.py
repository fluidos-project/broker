from .abstract_comparator import BaseComparator

class BandwidthComparator(BaseComparator):
    def compare(self, value, message):
        #implement here the comparator for the specific key 
        #the file must be named as the KEY from the RULES message

        return value <= int(message.get('bandwidth', 0))
        
comparator = BandwidthComparator()
