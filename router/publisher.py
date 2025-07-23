import pika
import time
import utils

class Publisher:
    def __init__(self, exchange):

        self.exchange = exchange
        self.connection = None
        self.channel = None
        self.connect()

    def connect(self):
        """Connects to channel."""
        while True:
            try:
                print("[@] Connecting to RabbitMQ...")
                self.connection = pika.BlockingConnection(utils.connection_params)
                self.channel = self.connection.channel()
                print("[@] Connected and channel ready.")
                break
            except Exception as e:
                print(f"[!] Connection/channel failed: {e}")
                time.sleep(5)

    def publish(self, routing_key, body, properties=None, max_retries=3):
        """Publish with reconnection."""
        for attempt in range(1, max_retries + 1):
            try:
                if self.connection is None or self.connection.is_closed:
                    print("[!] Connection is closed. Reconnecting...")
                    self.connect()
                if self.channel is None or self.channel.is_closed:
                    print("[!] Channel is closed. Reconnecting...")
                    self.connect()
                self.channel.basic_publish(
                    exchange=self.exchange,
                    routing_key=routing_key,
                    body=body,
                    properties=properties
                )
                print(f"[@] Message published")
                return True
            except Exception as e:
                print(f"[!] Publish failed (attempt {attempt}): {e}")
                time.sleep(2)
                self.connect()
        print("[!] Max retries exceeded. Giving up.")
        return False
