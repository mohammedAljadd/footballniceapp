from django.shortcuts import render, redirect, get_object_or_404
from .models import Match, PlayerEntry, ActionLog
from django.utils import timezone
from django.contrib import messages


from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from .models import ActionLog

from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from .models import ActionLog, Match  # Import Match to get list of matches

@staff_member_required
def action_log(request):
    match_id = request.GET.get('match_id')
    logs = ActionLog.objects.select_related('match').order_by('-timestamp')

    if match_id:
        logs = logs.filter(match_id=match_id)

    matches = Match.objects.order_by('date', 'time')  # For dropdown filter

    context = {
        'logs': logs,
        'matches': matches,
        'selected_match_id': int(match_id) if match_id else None,
    }
    return render(request, 'matches/action_log.html', context)



def match_list(request):
    matches = Match.objects.order_by('date')
    return render(request, 'matches/match_list.html', {'matches': matches})

def match_detail(request, match_id):
    match = get_object_or_404(Match, pk=match_id)
    players = match.players.filter(removed=False).order_by('added_at')

    user_entry = None
    if request.user.is_authenticated:
        user_entry = players.filter(user=request.user).first()

    context = {
        'match': match,
        'players': players,
        'user_entry': user_entry,
    }
    return render(request, 'matches/match_detail.html', context)

""" 
def add_player(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    name = request.POST.get('player_name', '').strip()

    if not name:
        messages.error(request, "Name cannot be empty.")
        return redirect('match_detail', match_id=match_id)

    existing = PlayerEntry.objects.filter(match=match, player_name__iexact=name, removed=False)
    if existing.exists():
        messages.warning(request, "You’re already on the list.")
    elif match.players.filter(removed=False).count() >= match.max_players:
        messages.error(request, "Sorry, the list is full.")
    else:
        PlayerEntry.objects.create(match=match, player_name=name)
        ActionLog.objects.create(match=match, player_name=name, action='added')
        messages.success(request, "You’ve been added!")

    return redirect('match_detail', match_id=match_id)

def remove_player(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    name = request.POST.get('player_name', '').strip()

    try:
        entry = PlayerEntry.objects.get(match=match, player_name__iexact=name, removed=False)
        entry.removed = True
        entry.removed_at = timezone.now()
        entry.save()
        ActionLog.objects.create(match=match, player_name=name, action='removed')
        messages.success(request, "You’ve been removed.")
    except PlayerEntry.DoesNotExist:
        messages.error(request, "Name not found on the list.")

    return redirect('match_detail', match_id=match_id) """


from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from .models import Match, PlayerEntry
from django.contrib import messages

@login_required
def toggle_participation(request, match_id):
    match = get_object_or_404(Match, pk=match_id)
    user = request.user
    entry = PlayerEntry.objects.filter(match=match, user=user).first()

    from .models import ActionLog

    if entry:
        if entry.removed:
            # Re-add player
            entry.removed = False
            entry.removed_at = None
            entry.save()
            ActionLog.objects.create(match=match, player_name=user.username, action='added')
            messages.success(request, "You have been added back to the list.")
        else:
            # Remove player
            entry.removed = True
            entry.removed_at = timezone.now()
            entry.save()
            ActionLog.objects.create(match=match, player_name=user.username, action='removed')
            messages.success(request, "You have been removed from the list.")
    else:
        # Add new player entry
        PlayerEntry.objects.create(user=user, match=match)
        ActionLog.objects.create(match=match, player_name=user.username, action='added')
        messages.success(request, "You have been added to the list.")


    return redirect('match_detail', match_id=match.id)

