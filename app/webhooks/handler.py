import hmac
import hashlib
import json
import requests
from threading import Thread
from queue import Queue

class WebhookHandler:
    """Handles webhook event dispatching"""
    
    def __init__(self):
        self.webhooks = {}
        self.event_queue = Queue()
        self._start_worker()
    
    def register_webhook(self, url, events, secret=None):
        """Register a new webhook endpoint"""
        webhook_id = hashlib.md5(url.encode()).hexdigest()
        self.webhooks[webhook_id] = {
            'url': url,
            'events': events,
            'secret': secret
        }
        return webhook_id
    
    def trigger_event(self, event_type, payload):
        """Trigger a webhook event"""
        self.event_queue.put({
            'type': event_type,
            'payload': payload
        })
    
    def _start_worker(self):
        """Start the webhook worker thread"""
        def worker():
            while True:
                event = self.event_queue.get()
                self._process_event(event)
                self.event_queue.task_done()
        
        thread = Thread(target=worker, daemon=True)
        thread.start()
    
    def _process_event(self, event):
        """Process and dispatch webhook event"""
        for webhook in self.webhooks.values():
            if event['type'] in webhook['events']:
                self._send_webhook(webhook, event)
    
    def _send_webhook(self, webhook, event):
        """Send webhook request to endpoint"""
        payload = json.dumps(event['payload'])
        headers = {
            'Content-Type': 'application/json'
        }
        
        if webhook['secret']:
            signature = hmac.new(
                webhook['secret'].encode(),
                payload.encode(),
                hashlib.sha256
            ).hexdigest()
            headers['X-Webhook-Signature'] = signature
        
        try:
            requests.post(webhook['url'], 
                         data=payload,
                         headers=headers,
                         timeout=5)
        except requests.exceptions.RequestException:
            # Log error and potentially retry
            pass