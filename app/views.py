from django.shortcuts import render, redirect, get_object_or_404
from .models import Player, Game, GameScore, History, ScoreRecord
from .forms import PlayerForm, GameForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import google.oauth2.credentials
from googleapiclient.discovery import build
from allauth.socialaccount.models import SocialToken
import ast

def home(request):
    games = Game.objects.all()
    return render(request, 'app/home.html', {'games': games})

@login_required
def create_player(request):
    if request.method == 'POST':
        form = PlayerForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('player_list')
    else:
        form = PlayerForm()
    return render(request, 'app/player_form.html', {'form': form})

@login_required
def player_list(request):
    players = Player.objects.all()
    return render(request, 'app/player_list.html', {'players': players})

@login_required
def edit_player(request, player_id):
    player = get_object_or_404(Player, id=player_id)
    if request.method == 'POST':
        form = PlayerForm(request.POST, request.FILES, instance=player)
        if form.is_valid():
            form.save()
            messages.success(request, f"玩家 {player.name} 的資料已更新。")
            return redirect('player_list')
    else:
        form = PlayerForm(instance=player)
    return render(request, 'app/player_form.html', {'form': form, 'edit_mode': True})

@login_required
def create_game(request):
    if request.method == 'POST':
        form = GameForm(request.POST)
        if form.is_valid():
            game = form.save()
            selected_players = request.POST.getlist('players')
            for player_id in selected_players:
                player = Player.objects.get(id=player_id)
                GameScore.objects.create(game=game, player=player, score=player.starting_score)
            return redirect('game_detail', game_id=game.id)
    else:
        form = GameForm()
    players = Player.objects.all()
    return render(request, 'app/game_form.html', {'form': form, 'players': players})

#@login_required
def game_list(request):
    games = Game.objects.all().order_by('-date')
    return render(request, 'app/game_list.html', {'games': games})

#@login_required
def game_detail(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    return render(request, 'app/game_detail.html', {'game': game})

@login_required
def edit_game(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    if request.method == 'POST':
        form = GameForm(request.POST, instance=game)
        if form.is_valid():
            form.save()
            # 更新玩家列表
            selected_players = request.POST.getlist('players')
            # 清除旧的玩家
            game.players.clear()
            # 添加新的玩家并创建或获取对应的 GameScore
            for player_id in selected_players:
                player = Player.objects.get(id=player_id)
                GameScore.objects.get_or_create(game=game, player=player, defaults={'score': player.starting_score})
            messages.success(request, f"比賽 {game.name} 的資料已更新。")
            return redirect('game_list')
    else:
        form = GameForm(instance=game)
    players = Player.objects.all()
    selected_player_ids = game.players.values_list('id', flat=True)
    return render(request, 'app/game_form.html', {
        'form': form,
        'players': players,
        'selected_player_ids': selected_player_ids,
        'edit_mode': True,
    })

@login_required
def update_score(request, game_id, player_id, action):
    game = get_object_or_404(Game, id=game_id)
    game_score = get_object_or_404(GameScore, game=game, player_id=player_id)
    
    if request.method == 'POST':
        reason = request.POST.get('reason', '')
        if action == 'increment':
            score_change = game_score.player.increment
        elif action == 'decrement':
            score_change = -game_score.player.increment
        else:
            messages.error(request, '無效的操作。')
            return redirect('game_detail', game_id=game_id)
        
        ScoreRecord.objects.create(
            game_score=game_score,
            score_change=score_change,
            reason=reason
        )
        
        messages.success(request, '分數已成功更新。')
    
    return redirect('game_detail', game_id=game_id)

# 其他视图，如更新分数、计算器、历史记录等，需进一步实现

@login_required
def export_to_sheets(request, game_id):
    game = Game.objects.get(id=game_id)
    # 获取用户的 Google 凭证
    token = SocialToken.objects.get(account__user=request.user, account__provider='google')
    credentials = google.oauth2.credentials.Credentials(token.token)
    service = build('sheets', 'v4', credentials=credentials)
    
    # 构建要写入的数据
    game_scores = GameScore.objects.filter(game=game)
    data = [
        ['玩家', '分数']
    ]
    for score in game_scores:
        data.append([score.player.name, score.score])
    
    # 写入到 Google Sheets
    spreadsheet_body = {
        'properties': {
            'title': f"{game.name} 分数表"
        }
    }
    spreadsheet = service.spreadsheets().create(body=spreadsheet_body, fields='spreadsheetId').execute()
    spreadsheet_id = spreadsheet.get('spreadsheetId')
    
    range_ = 'Sheet1!A1'
    value_range_body = {
        'values': data
    }
    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=range_,
        valueInputOption='RAW',
        body=value_range_body
    ).execute()
    
    return redirect('game_detail', game_id=game.id)

def calculator(request):
    result = None
    if request.method == 'POST':
        expression = request.POST.get('expression')
        try:
            # 使用安全的计算方法
            result = eval_expression(expression)
        except Exception as e:
            result = f"错误：{e}"
    return render(request, 'app/calculator.html', {'result': result})

def eval_expression(expr):
    # 安全地解析和计算表达式
    node = ast.parse(expr, mode='eval')
    for subnode in ast.walk(node):
        if not isinstance(subnode, (ast.Expression, ast.BinOp, ast.Num, ast.UnaryOp,
                                    ast.operator, ast.unaryop)):
            raise ValueError("不支持的表达式")
    return eval(compile(node, '<string>', 'eval'))

@login_required
def edit_score_record(request, record_id):
    record = get_object_or_404(ScoreRecord, id=record_id)
    if request.method == 'POST':
        old_score_change = record.score_change
        new_score_change = int(request.POST.get('score_change'))
        record.score_change = new_score_change
        record.reason = request.POST.get('reason')
        record.save()
        
        # 更新 GameScore
        game_score = record.game_score
        game_score.score += (new_score_change - old_score_change)
        game_score.save()
        
        messages.success(request, '分數記錄已成功更新。')
        return redirect('score_records', game_id=record.game_score.game.id)
    
    return render(request, 'app/edit_score_record.html', {'record': record})

def score_records(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    records = ScoreRecord.objects.filter(game_score__game=game).order_by('-timestamp')
    return render(request, 'app/score_records.html', {'game': game, 'records': records})
