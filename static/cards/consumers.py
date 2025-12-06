import json
import random
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync
from .models import Winner
from .utils import generate_90ball_ticket, check_90ball_status
from decimal import Decimal
from bingo_project.settings import ROOM_CONFIG, STRIPE_SECRET_KEY
import stripe

stripe.api_key = STRIPE_SECRET_KEY

# Global state
GAME_STATE = {}
BANNED_USERS = set()
MUTED_USERS = {}
MOD_ACTIVITY_LOG = []

class BingoConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name'].lower()
        self.room_group_name = f"bingo_{self.room_name}"
        query = self.scope["query_string"].decode()
        params = dict(p.split('=') for p in query.split('&') if '=' in p)

        if self.room_name not in GAME_STATE:
            GAME_STATE[self.room_name] = {"called": [], "players": {}, "revenue": 0, "paid_players": set()}

        room_upper = self.room_name.upper()
        config = ROOM_CONFIG.get(room_upper, {})

        # Permission check
        if params.get("key") == config.get("hostkey"):
            self.role = "host"
        elif params.get("mod") == config.get("modkey"):
            self.role = "moderator"
        elif params.get("pw") == config.get("pw"):
            self.role = "player"
        else:
            await self.close(code=4001)
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        if self.role == "host":
            await self.send_host_full_state()

    async def receive(self, text_data):
        data = json.loads(text_data)
        state = GAME_STATE[self.room_name]
        room_upper = self.room_name.upper()
        config = ROOM_CONFIG.get(room_upper, {})

        if self.role in ["host"] and data.get("type") == "call_number":
            available = [n for n in range(1,91) if n not in state["called"]]
            if available:
                num = random.choice(available)
                state["called"].append(num)
                await self.channel_layer.group_send(self.room_group_name, {"type": "number_called", "number": num})
                await self.send_host_full_state()

        elif data.get("type") == "join":
            username = data["username"]
            ticket = generate_90ball_ticket()
            state["players"][username] = {"ticket": ticket, "marked": [[False]*9 for _ in range(3)]}
            if config.get("paid") and username not in state["paid_players"]:
                state["paid_players"].add(username)
                state["revenue"] += config.get("price", 500) / 100

            await self.channel_layer.group_send(self.room_group_name, {
                "type": "player_joined", "username": username, "ticket": ticket
            })
            await self.channel_layer.group_send(self.room_group_name, {
                "type": "win_confetti", "win_type": "welcome", "winner": username
            })

        elif data.get("type") == "mark_number":
            username = data["username"]
            r, c = data["row"], data["col"]
            if username in state["players"]:
                state["players"][username]["marked"][r][c] = True
                win_type = check_90ball_status(state["players"][username]["marked"])
                if win_type != "none":
                    Winner.objects.create(
                        room=room_upper,
                        username=username,
                        prize_type=win_type,
                        prize_description="Full House" if win_type == "full_house" else win_type.replace('_', ' ').title(),
                        amount_gbp = config.get("price", 500) / 100 * 0.8
                    )
                    await self.channel_layer.group_send(self.room_group_name, {
                        "type": "win_confetti", "win_type": win_type, "winner": username
                    })

        # Add mod commands, bans, etc. from previous messages if needed

    async def number_called(self, event):
        await self.send(text_data=json.dumps({"type": "number", "number": event["number"]}))

    async def win_confetti(self, event):
        await self.send(text_data=json.dumps({"type": "win_confetti", "win_type": event["win_type"], "winner": event["winner"]}))

    async def send_host_full_state(self):
        # Full host view code from previous messages
        pass
