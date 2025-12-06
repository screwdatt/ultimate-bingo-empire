from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from datetime import timedelta
from collections import defaultdict
import csv
from .models import Winner
from .consumers import GAME_STATE
from bingo_project.settings import ROOM_CONFIG, ROOM_PRIZES

def room_status_api(request, room_name):
    room_name = room_name.lower()
    state = GAME_STATE.get(room_name, {"called": [], "players": {}, "revenue": 0})
    leaderboard = []
    for name, info in state["players"].items():
        marked = info["marked"]
        lines = sum(1 for r in marked if all(m or marked[marked.index(r)][c] is None for c,m in enumerate(r)))
        progress = {1:"One Line", 2:"Two Lines", 3:"FULL HOUSE!!!"}.get(lines, f"{sum(sum(1 for c in row if c) for row in marked)} marked")
        leaderboard.append({"name": name, "progress": progress})
    leaderboard.sort(key=lambda x: (x["progress"] == "FULL HOUSE!!!", x["progress"] == "Two Lines", x["progress"] == "One Line", x["name"]))

    return JsonResponse({
        "called": state["called"],
        "leaderboard": leaderboard[:10],
        "revenue": state["revenue"]
    })

def dashboard(request):
    rooms_data = {}
    total_players = total_money = 0
    for room, state in GAME_STATE.items():
        config = ROOM_CONFIG.get(room.upper(), {})
        rooms_data[room] = {
            "players": len(state["players"]),
            "revenue": f"{state['revenue']:.2f}",
            "called": len(state["called"]),
            "prizes": ROOM_PRIZES.get(room.upper(), ROOM_PRIZES["DEFAULT"]),
            "status": "In progress" if state["called"] else "Waiting",
            "pw": config.get("pw", ""),
            "hostkey": config.get("hostkey", "none"),
            "modkey": config.get("modkey", "none")
        }
        total_players += len(state["players"])
        total_money += state["revenue"]

    return render(request, "dashboard.html", {
        "rooms": rooms_data,
        "total_rooms": len(rooms_data),
        "total_players": total_players,
        "total_money": f"{total_money:.2f}"
    })

def winners_archive(request):
    all_winners = Winner.objects.all()[:500]
    daily = defaultdict(list)
    for w in all_winners:
        day = w.won_at.date()
        daily[day].append(w)

    return render(request, "winners.html", {
        "daily": dict(sorted(daily.items(), reverse=True)),
    })

# Export CSVs (optional)
def export_csv(request, kind):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{kind}.csv"'
    writer = csv.writer(response)
    if kind == "winners":
        writer.writerow(["Room", "Username", "Prize", "Amount", "Date"])
        for w in Winner.objects.all():
            writer.writerow([w.room, w.username, w.prize_description, w.amount_gbp, w.won_at])
    return response
