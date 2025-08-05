from django.shortcuts import render, redirect, get_object_or_404
from .models import Match, PlayerEntry, ActionLog, MatchComment, PlayerStats
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from .forms import MatchForm, PlayerNotesForm, MatchCommentForm
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.db.models import Count, Q
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from io import BytesIO

def match_list(request):
    # Get today's date
    today = timezone.now().date()
    
    # Filter matches to show only future matches (date >= today)
    matches = Match.objects.filter(date__gte=today).order_by('date', 'time')
    
    return render(request, 'matches/match_list.html', {'matches': matches})

def match_detail(request, match_id):
    match = get_object_or_404(Match, pk=match_id)
    players = match.players.filter(removed=False).order_by('added_at')
    comments = match.comments.all()

    user_entry = None
    if request.user.is_authenticated:
        user_entry = players.filter(user=request.user).first()

    # Handle comment form
    comment_form = MatchCommentForm()
    if request.method == 'POST' and request.user.is_authenticated:
        if 'add_comment' in request.POST:
            comment_form = MatchCommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.match = match
                comment.user = request.user
                comment.save()
                messages.success(request, "Comment added successfully!")
                return redirect('match_detail', match_id=match.id)

    context = {
        'match': match,
        'players': players,
        'user_entry': user_entry,
        'comments': comments,
        'comment_form': comment_form,
    }
    return render(request, 'matches/match_detail.html', context)

@login_required
def toggle_participation(request, match_id):
    match = get_object_or_404(Match, pk=match_id)
    user = request.user
    entry = PlayerEntry.objects.filter(match=match, user=user).first()

    if request.method == 'POST':
        notes = request.POST.get('notes', '').strip()
        
        if entry:
            if entry.removed:
                # Re-add player
                entry.removed = False
                entry.removed_at = None
                entry.notes = notes
                entry.save()
                ActionLog.objects.create(match=match, user=user, player_name=user.username, action='added')
                messages.success(request, "You have been added back to the list.")
            else:
                # Remove player
                entry.removed = True
                entry.removed_at = timezone.now()
                entry.save()
                ActionLog.objects.create(match=match, user=user, player_name=user.username, action='removed')
                messages.success(request, "You have been removed from the list.")
        else:
            # Add new player entry
            PlayerEntry.objects.create(user=user, match=match, notes=notes)
            ActionLog.objects.create(match=match, user=user, player_name=user.username, action='added')
            messages.success(request, "You have been added to the list.")
        
        # Update player stats
        PlayerStats.update_stats_for_user(user)

    return redirect('match_detail', match_id=match.id)

@login_required
def update_player_notes(request, match_id):
    """AJAX endpoint to update player notes"""
    if request.method == 'POST':
        match = get_object_or_404(Match, pk=match_id)
        entry = get_object_or_404(PlayerEntry, match=match, user=request.user, removed=False)
        
        notes = request.POST.get('notes', '').strip()
        entry.notes = notes
        entry.save()
        
        return JsonResponse({'success': True, 'message': 'Notes updated successfully!'})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})

def stats_page(request):
    """Display player statistics"""
    # Update all user stats first
    for user in User.objects.all():
        PlayerStats.update_stats_for_user(user)
    
    # Get all player stats
    stats = PlayerStats.objects.select_related('user').order_by('-matches_attended', '-matches_joined')
    
    # Get some additional statistics
    total_matches = Match.objects.filter(date__lt=timezone.now().date()).count()
    total_players = User.objects.count()
    
    # Most active players (top 10)
    top_players = stats[:10]
    
    # Recent activity (last 30 days)
    thirty_days_ago = timezone.now().date() - timezone.timedelta(days=30)
    recent_matches = Match.objects.filter(date__gte=thirty_days_ago, date__lt=timezone.now().date()).count()
    
    context = {
        'stats': stats,
        'total_matches': total_matches,
        'total_players': total_players,
        'top_players': top_players,
        'recent_matches': recent_matches,
    }
    
    return render(request, 'matches/stats.html', context)

@login_required
def delete_comment(request, comment_id):
    """Delete a comment (only by the author or staff)"""
    comment = get_object_or_404(MatchComment, pk=comment_id)
    
    if request.user == comment.user or request.user.is_staff:
        match_id = comment.match.id
        comment.delete()
        messages.success(request, "Comment deleted successfully!")
    else:
        messages.error(request, "You can only delete your own comments.")
    
    return redirect('match_detail', match_id=comment.match.id)

@login_required
def toggle_theme(request):
    """Toggle dark mode theme"""
    if request.method == 'POST':
        # Store theme preference in session
        current_theme = request.session.get('theme', 'light')
        new_theme = 'dark' if current_theme == 'light' else 'light'
        request.session['theme'] = new_theme
        
        return JsonResponse({'success': True, 'theme': new_theme})
    
    return JsonResponse({'success': False})

@staff_member_required
def create_match(request):
    if request.method == 'POST':
        form = MatchForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Match created successfully!')
            return redirect('match_list')
    else:
        form = MatchForm()
    
    return render(request, 'matches/create_match.html', {'form': form})

@staff_member_required
def edit_match(request, match_id):
    match = get_object_or_404(Match, pk=match_id)
    
    if request.method == 'POST':
        form = MatchForm(request.POST, instance=match)
        if form.is_valid():
            form.save()
            messages.success(request, 'Match updated successfully!')
            return redirect('match_detail', match_id=match.id)
    else:
        form = MatchForm(instance=match)
    
    return render(request, 'matches/edit_match.html', {'form': form, 'match': match})

@staff_member_required
def delete_match(request, match_id):
    match = get_object_or_404(Match, pk=match_id)
    
    if request.method == 'POST':
        match.delete()
        messages.success(request, 'Match deleted successfully!')
        return redirect('match_list')
    
    return render(request, 'matches/delete_match.html', {'match': match})

@staff_member_required
def manage_matches(request):
    show_all = request.GET.get('show_all', False)
    today = timezone.now().date()
    
    if show_all:
        # Show all matches (including past ones)
        matches = Match.objects.order_by('-date', '-time')
    else:
        # Show only upcoming matches
        matches = Match.objects.filter(date__gte=today).order_by('date', 'time')
    
    return render(request, 'matches/manage_matches.html', {
        'matches': matches,
        'show_all': show_all,
        'today': today
    })

@staff_member_required
def action_log(request):
    match_id = request.GET.get('match_id')
    player_name = request.GET.get('player_name', '').strip()
    
    logs = ActionLog.objects.select_related('match').order_by('-timestamp')

    # Filter by match if selected
    if match_id:
        logs = logs.filter(match_id=match_id)
    
    # Filter by player name if provided
    if player_name:
        logs = logs.filter(player_name__icontains=player_name)

    # Get all matches for dropdown
    matches = Match.objects.order_by('date', 'time')
    
    # Get unique player names for dropdown (from action logs)
    player_names = ActionLog.objects.values_list('player_name', flat=True).distinct().order_by('player_name')

    context = {
        'logs': logs,
        'matches': matches,
        'player_names': player_names,
        'selected_match_id': int(match_id) if match_id else None,
        'selected_player_name': player_name,
    }
    return render(request, 'matches/action_log.html', context)

def export_match_pdf(request, match_id):
    """Export match details and player list to PDF"""
    match = get_object_or_404(Match, pk=match_id)
    players = match.players.filter(removed=False).order_by('added_at')
    
    # Create the HttpResponse object with PDF headers
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="match_{match.day}_{match.date}.pdf"'
    
    # Create PDF document
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=18)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Get styles
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    heading_style = styles['Heading2']
    normal_style = styles['Normal']
    
    # Title
    title = Paragraph("FootyPoll Match Details", title_style)
    elements.append(title)
    elements.append(Spacer(1, 12))
    
    # Match Information
    match_info = f"""
    <b>Match Day:</b> {match.day}<br/>
    <b>Date:</b> {match.date.strftime('%B %d, %Y')}<br/>
    <b>Time:</b> {match.time.strftime('%H:%M')}<br/>
    <b>Location:</b> <link href="{match.location_url}">View on Map</link><br/>
    <b>Maximum Players:</b> {match.max_players}<br/>
    <b>Registered Players:</b> {players.count()}
    """
    
    match_para = Paragraph(match_info, normal_style)
    elements.append(match_para)
    elements.append(Spacer(1, 20))
    
    # Player List Section
    player_heading = Paragraph("Player List", heading_style)
    elements.append(player_heading)
    elements.append(Spacer(1, 12))
    
    if players.exists():
        # Create table data
        table_data = [['#', 'Player Name', 'Notes', 'Joined At']]
        
        for i, player in enumerate(players, 1):
            notes = player.notes[:50] + "..." if player.notes and len(player.notes) > 50 else (player.notes or "")
            table_data.append([
                str(i),
                player.user.username,
                notes,
                player.added_at.strftime('%m/%d/%Y %H:%M')
            ])
        
        # Create table
        table = Table(table_data, colWidths=[0.5*inch, 2*inch, 2.5*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        
        elements.append(table)
    else:
        no_players = Paragraph("No players registered for this match yet.", normal_style)
        elements.append(no_players)
    
    elements.append(Spacer(1, 20))
    
    # Footer
    footer_text = f"Generated on {timezone.now().strftime('%B %d, %Y at %H:%M')}"
    footer = Paragraph(footer_text, normal_style)
    elements.append(footer)
    
    # Build PDF
    doc.build(elements)
    
    # Get PDF data and return response
    pdf_data = buffer.getvalue()
    buffer.close()
    response.write(pdf_data)
    
    return response