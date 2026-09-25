import json

import redis

from app.core.config import settings


class PubSubManager:
    def __init__(self):
        self.redis_client = redis.from_url(
            settings.redis_url, encoding="utf-8", decode_responses=True
        )

    async def publish(self, user_id: str, data: dict):
        await self.redis_client.publish(f"user:{user_id}", json.dumps(data))

    async def subscribe(self, user_id: str):
        pubsub_obj = self.redis_client.pubsub()
        await pubsub_obj.subscribe(f"user:{user_id}")
        try:
            async for message in pubsub_obj.listen():
                if message["type"] == "message":
                    yield json.loads(message["data"])
        finally:
            await pubsub_obj.unsubscribe(f"user:{user_id}")
            await pubsub_obj.close()


pubsub_manager = PubSubManager()
