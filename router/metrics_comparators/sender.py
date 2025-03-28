from .abstract_comparator import BaseComparator

class SenderComparator(BaseComparator):
    def compare(self, value, message):
        #implement here the comparator for the specific key 
        #the file must be named as the KEY from the RULES message

        #no checks are performed on the sender key
        return True
        
comparator = SenderComparator()
