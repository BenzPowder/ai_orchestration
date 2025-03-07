class Webhook:
    def __init__(self, id=None, name=None, description=None, url_path=None, agent_id=None, is_active=True, secret_key=None):
        self.id = id
        self.name = name
        self.description = description
        self.url_path = url_path
        self.agent_id = agent_id
        self.is_active = is_active
        self.secret_key = secret_key

class WebhookLog:
    def __init__(self, id=None, webhook_id=None, request_data=None, response_data=None, created_at=None):
        self.id = id
        self.webhook_id = webhook_id
        self.request_data = request_data
        self.response_data = response_data
        self.created_at = created_at
