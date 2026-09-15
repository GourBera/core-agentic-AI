# Target Interface
class Notification:
    def send(self, message):
        pass


# Concrete implementation for email notifications
class EmailNotification(Notification):
    def send(self, message):
        return f"Sending Email: {message}"


# Concrete implementation for SMS notifications
class SMSNotification(Notification):
    def send(self, message):
        return f"Sending SMS: {message}"


# Concrete implementation for push notifications
class PushNotification(Notification):
    def send(self, message):
        return f"Sending Push Notification: {message}" k