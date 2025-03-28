from .abstract_comparator import BaseComparator

class LocationsComparator(BaseComparator):
    def compare(self, value, message):
        #implement here the comparator for the specific key 
        #the file must be named as the KEY from the RULES message
    
        for loc in value:
            if loc==message.get("location"):
                return True
        return False
        
comparator = LocationsComparator()
