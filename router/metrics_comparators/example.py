from .abstract_comparator import BaseComparator

class ExampleComparator(BaseComparator):
    def compare(self, value, message):
        #implement here the comparator for the specific key 
        #the file must be named as the KEY from the RULES message

        #if example key is not found in message, .get() returns value
        #so comparator always returns True
        return value == message.get('example', value)

comparator = ExampleComparator()