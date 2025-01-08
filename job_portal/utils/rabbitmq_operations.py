import pika
import json


def send_rabbitmq_message(queue_name, message):
    """
    Utility function to send a message to RabbitMQ.

    :param queue_name: The name of the RabbitMQ queue.
    :param message: The message to send to the queue.
    """
    # Establish a connection to RabbitMQ server
    connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    channel = connection.channel()

    # Declare the queue
    channel.queue_declare(queue=queue_name)
    message_body = json.dumps(message)

    # Send the message
    channel.basic_publish(
        exchange="",
        routing_key=queue_name,
        body=message_body,
        properties=pika.BasicProperties(delivery_mode=2),  # The queue name
    )

    print(f" [x] Sent '{message}' to queue '{queue_name}'")

    # Close the connection
    connection.close()
