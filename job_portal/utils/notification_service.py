from utils.rabbitmq_operations import send_rabbitmq_message


class NotificationServiceOperation:

    def __init__(self):
        self.QUEUE_NAME = "notification_queue"

    def send_user_registration_data(self, user):
        message = {
            "user_id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "operation": "user_register",
        }
        send_rabbitmq_message(queue_name=self.QUEUE_NAME, message=message)

    def send_tokens_to_notification_service(self, request):
        try:
            token = request.auth
            token_payload = {
                "token": str(token),
                "operation": "tokens",
            }
            send_rabbitmq_message(queue_name=self.QUEUE_NAME, message=token_payload)
        except Exception as e:
            print(f"Error while sending tokens to notification service: {e}")

    # def new_job_create_data(self, job):
    #     message = {
    #         "user_id": user.id,
    #         "email": user.email,
    #         "first_name": user.first_name,
    #         "last_name": user.last_name,
    #         "operation": "user_register",
    #     }
    #     send_rabbitmq_message(queue_name=self.QUEUE_NAME, message=message)
