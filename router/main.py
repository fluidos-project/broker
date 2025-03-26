import threading
from routing_manager import RoutingManager
from rules_manager import RulesManager

if __name__ == "__main__":

    routing_manager = RoutingManager()
    rules_manager = RulesManager()

    routing_thread = threading.Thread(target=routing_manager.start)
    rules_thread = threading.Thread(target=rules_manager.start)

    routing_thread.start()
    rules_thread.start()

    routing_thread.join()
    rules_thread.join()

