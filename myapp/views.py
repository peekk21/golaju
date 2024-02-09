from django.shortcuts import render, redirect
from .models import User, Log, Output, Location, Golajum

from django.utils import timezone
from django.db.models import Avg, Count

import pandas as pd
from datetime import datetime
import random
import json
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from golaju_algorithm import golaju_content_init
from dalle import dalle
from chart import radar, dashboard_chart

# Create your views here.


def login_view(request): # 세션 정보 생성
    if request.method == 'POST':
        login_id = request.POST.get('login_id')
        login_pw = request.POST.get('login_pw')
        
        try:
            user = User.objects.get(login_id=login_id)
        except User.DoesNotExist:
            return render(request, 'myapp/login.html', {'error_message': '존재하지 않는 사용자입니다.'})
        
        # session_login_id = request.session.get('login_id', None)

        # if session_login_id is None:  # 기존 로그인 정보가 없음
        if user.login_pw == login_pw:  # 비밀번호가 맞음
            request.session['login_id'] = user.login_id
            return redirect('myapp:home')
        
        else:  # 비밀번호가 틀림
            return render(request, 'myapp/login.html', {'error_message': '비밀번호를 확인하세요.'})
        
        # else:
        #     return redirect('myapp:home')  # 이미 로그인함.. 세션에 저장은 되어있는데 밑에서 안불러와진다!?

    return render(request, 'myapp/login.html')




def home(request):
    login_id = request.session.get('login_id', None)
    user = User.objects.get(login_id=login_id)

    nav_img_home = '/static/myapp/base/home_clicked.png'
    nav_img_today = '/static/myapp/base/today.png'
    nav_img_dashboard = '/static/myapp/base/dashboard.png'
    
    log = Log.objects.filter(login_id=login_id).order_by('-date_golajum').first() # Log에서 가장 최근 추천술 불러옴 (name, date_golajum)
    detail = Output.objects.get(name=log.name) # Output에서 상세 정보 가져옴 (link_img)
    
    context = {'user':user, 'nav_img_home':nav_img_home, 'nav_img_today':nav_img_today, 'nav_img_dashboard':nav_img_dashboard, 'log':log, 'detail':detail}
    return render(request, 'myapp/home.html', context)



def today(request): # 가장 최신 log 불러오기 -> 상품명 세션 저장
    login_id = request.session.get('login_id', None)
    user = User.objects.get(login_id=login_id)
    
    log = Log.objects.filter(login_id=login_id).order_by('-date_golajum').first() # Log에서 가장 최근 추천술 불러옴 (name, date_golajum, rating)
    detail = Output.objects.get(name=log.name) # Output에서 상세 정보 가져옴 (link_img, alc_ab, ml, won, scent, sweet, sour, fizzy, body, strong, link_sale)
    request.session['productName'] = log.name # session에 저장해놨다가 이미지 보기 눌렀을 때 log 불러와
    
    # 추천 상세정보 확인일시 기록
    if log.date_checked == None:
        log.date_checked = timezone.now()
        log.save()
        
    # 판매처
    if detail.link_sale == None or detail.link_sale == '':
        if detail.name_sale == None or detail.name_sale == '':
            link_sale = "https://search.shopping.naver.com/search/all?query=" + detail.name
        else: link_sale = "https://search.shopping.naver.com/search/all?query=" + detail.name_sale
    else: link_sale = detail.link_sale
    
    # 단신청바
    dscb_name = ['단맛', '신맛', '청량감', '바디감', '향의 강도']
    dscb_field = ['sweet', 'sour', 'fizzy', 'body', 'strong']
    
    
    # 최초 가상술 좌표를 이용한 레이다 차트
    golajum = Golajum.objects.filter(login_id=login_id, golajum=log.name).first()
    radar_path = radar(golajum)
    
    
    # 별점 매기기
    if request.method == 'POST':
        rating = request.POST.get('rating', None)
        log.rating = rating
        log.date_rated = timezone.now()
        log.save()
        
        # 달리 소환 코드
        pose = ['looking at', 'drinking']
        emotion_prompt = {'1':'frowning facial expression', '2':'no facial expression', '3':'a slight smile', '4':'satisfied facial expression', '5':'a big smile'}
        alc_type_prompt = {'증류주':'colorless clear', '탁주':'ivory-colored non-clear', '약주':'yellow-colored clear', '과실주':'juicy'}
        
        if log.date_rated.hour > 6 and log.date_rated.hour < 18:
            time_section = 'day'
        else: time_section = 'night'
        
        prompt = f"""animation-style cartoon of a {user.age}s asian {user.sex}, {random.choice(pose)} a bottle of alcohol with {emotion_prompt[log.rating]}.
                    Neat style, winter outfit, has a big circle around the character on the background, at the {time_section} time.
                    The character has {user.hair_color}, {user.hair_style}, {user.hair_length} hair {user.hair_bangs} bangs, and {user.eyelids}, {user.glasses}.
                    The bottle has {alc_type_prompt[log.alc_type]} liquid in it."""
        print(prompt)
        
        date = log.date_rated.strftime('%Y-%m-%d %H-%M-%S')
        shot_name = log.login_id + '_' + log.name + '_' + str(log.rating) + '_' + date
    
        dalle(prompt, shot_name)

        script_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(script_dir,  '..', 'static', 'myapp', 'shots', shot_name) + '.jpg'
        
        if not os.path.isfile(path):
            log.rating = -1
            log.date_rated = None
            log.save() # 별점 다시 -1로 초기화하기
            print('파일 생성 오류')
            
        return redirect('myapp:today')
    
    # 네비게이션 바 이미지
    nav_img_home = '/static/myapp/base/home.png'
    nav_img_today = '/static/myapp/base/today_clicked.png'
    nav_img_dashboard = '/static/myapp/base/dashboard.png'
    
    
    context = {'user':user, 'log':log, 'detail':detail,
               'link_sale': link_sale, 'radar_chart':radar_path, 'dscb_name': dscb_name, 'dscb_field': dscb_field,
               'nav_img_home':nav_img_home, 'nav_img_today':nav_img_today, 'nav_img_dashboard':nav_img_dashboard}
    return render(request, 'myapp/today.html', context)



def dashboard(request):
    login_id = request.session.get('login_id', None)
    user = User.objects.get(login_id=login_id)
    
    log = Log.objects.filter(login_id=login_id) # 유저의 전체 log 가져옴 (date_golajum 순서로 정렬)
    log_rated = log.filter(date_rated__isnull=False)
    
    # 스탬프 보드
    log_rated_bydate = log_rated.order_by('date_rated') # 평가한 시간 순서대로 정렬한 리스트 출력
    stamp_list = [] # 보낼 스탬프 이미지 리스트
    log_rated_count = log_rated.count()
    
    if log_rated_count == 0: # 평가 이력 아예 없음 (0개)
        stamp_list = ['../../static/myapp/dashboard/stamp.png']*10
        chart_opened = False
        
    elif log_rated_count % 10 == 0: # 평가 10개 채움
        for i in range(10): # 0~9까지 카운트
            index = (log_rated_count//10 -1) * 10 + i
            login_id = log_rated_bydate[index].login_id
            name = log_rated_bydate[index].name
            rating = str(log_rated_bydate[index].rating)
            date = log_rated_bydate[index].date_rated.strftime('%Y-%m-%d %H-%M-%S')
            shot_name = login_id + '_' + name + '_' + rating + '_' + date
            path = '../../static/myapp/shots/'+shot_name+'.jpg'
            stamp_list.append(path)
            
        chart_opened = True
    
    else: # 평가 1개~9개 채우는 중임
        for i in range(log_rated_count % 10): # 13개 쌓인 경우, 1번, 2번, 3번 출력
            index = (log_rated_count//10) * 10 + i
            login_id = log_rated_bydate[index].login_id
            name = log_rated_bydate[index].name
            rating = str(log_rated_bydate[index].rating)
            date = log_rated_bydate[index].date_rated.strftime('%Y-%m-%d %H-%M-%S')
            shot_name = login_id + '_' + name + '_' + rating + '_' + date
            path = '../../static/myapp/shots/'+shot_name + '.jpg'
            stamp_list.append(path)
        
        for i in range(10 - log_rated_count % 10):
            stamp_list.append('../../static/myapp/dashboard/stamp.png')
            
        chart_opened = False
    
    
    # 추천/평가 이력 # 로그인 정보 받아서 기추천 리스트 보이기 (context로 줘야 함)
    log_names = log.order_by('-date_golajum').values_list('name', flat=True) # (내림차순) log에 있는 술 이름들 -> 리스트로 변환
    lists = Output.objects.filter(name__in=log_names) # output의 술 상세정보 모두 가져옴
    
    inputs = pd.DataFrame.from_records(log_names.values())
    lists = pd.DataFrame.from_records(lists.values())
    inputs['date_rated'] = inputs['date_rated'].fillna('미평가') # from_records 거치면서 null -> NaT로 바뀌어서 인식이 안되는 문제..

    merged = pd.merge(inputs, lists, how='inner', on='name') # alc_type이 겹쳐서 두개 생김
    merged.drop('alc_type_x', axis=1, inplace=True) # 제거
    merged.rename(columns={'alc_type_y': 'alc_type'}, inplace=True) # 이름 원래대로
    
    lists = merged.iterrows()
    
    # 특정 술 자세히보기 눌렀을 때
    if request.method == 'POST':
        name = request.POST.get('productName', None)
        request.session['productName'] = name # session에 저장해놨다가 이미지 보기 눌렀을 때 log 불러와
        return redirect('myapp:detail')    
    
    
    # 네비게이션 바 아이콘
    nav_img_home = '/static/myapp/base/home.png'
    nav_img_today = '/static/myapp/base/today.png'
    nav_img_dashboard = '/static/myapp/base/dashboard_clicked.png'
    
    
    context = {'user':user, 'nav_img_home':nav_img_home, 'nav_img_today':nav_img_today, 'nav_img_dashboard':nav_img_dashboard,
               'stamp_list':stamp_list, 'chart_opened':chart_opened, 'lists':lists}
    return render(request, 'myapp/dashboard.html', context)


def detail(request): # 세션 저장 상품명 불러오기 -> log 불러오기
    login_id = request.session.get('login_id', None)
    user = User.objects.get(login_id=login_id)
    
    name = request.session.get('productName', None)
    log = Log.objects.filter(login_id=login_id, name=name).first() # dashboard-detail 눌렀을 때 저장된 상품명을 기준으로 로그 불러옴
    detail = Output.objects.get(name=name)

    # 추천 상세정보 확인일시 기록
    if log.date_checked == None:
        log.date_checked = timezone.now()
        log.save()
        
    # 판매처
    if detail.link_sale == None or detail.link_sale == '':
        if detail.name_sale == None or detail.name_sale == '':
            link_sale = "https://search.shopping.naver.com/search/all?query=" + detail.name
        else: link_sale = "https://search.shopping.naver.com/search/all?query=" + detail.name_sale
    else: link_sale = detail.link_sale
    
    # 단신청바
    dscb_name = ['단맛', '신맛', '청량감', '바디감', '향의 강도']
    dscb_field = ['sweet', 'sour', 'fizzy', 'body', 'strong']

    # 최초 가상술 좌표를 이용한 레이다 차트
    golajum = Golajum.objects.filter(login_id=login_id, golajum=log.name).first()
    radar_path = radar(golajum)

    # 별점 매기기
    if request.method == 'POST':
        rating = request.POST.get('rating', None)
        log.rating = rating
        log.date_rated = timezone.now()
        log.save()
        
        # 달리 소환 코드
        pose = ['looking at', 'drinking']
        emotion_prompt = {'1':'frowning facial expression', '2':'no facial expression', '3':'a slight smile', '4':'satisfied facial expression', '5':'a big smile'}
        alc_type_prompt = {'증류주':'colorless clear', '탁주':'ivory-colored non-clear', '약주':'yellow-colored clear', '과실주':'juicy'}
        
        if log.date_rated.hour > 6 and log.date_rated.hour < 18:
            time_section = 'day'
        else: time_section = 'night'
        

        prompt = f"""animation-style cartoon of a {user.age}s asian {user.sex}, {random.choice(pose)} a bottle of alcohol with {emotion_prompt[log.rating]}.
                    Neat style, winter outfit, has a big circle around the character on the background, at the {time_section} time.
                    The character has {user.hair_color}, {user.hair_style}, {user.hair_length} hair {user.hair_bangs} bangs, and {user.eyelids}, {user.glasses}.
                    The bottle has {alc_type_prompt[log.alc_type]} liquid in it."""
        print(prompt)
        
        date = log.date_rated.strftime('%Y-%m-%d %H-%M-%S')
        shot_name = log.login_id + '_' + log.name + '_' + str(log.rating) + '_' + date
    
        dalle(prompt, shot_name)

        script_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(script_dir,  '..', 'static', 'myapp', 'shots', shot_name) + '.jpg'
        
        if not os.path.isfile(path):
            log.rating = -1
            log.date_rated = None
            log.save() # 별점 다시 -1로 초기화하기
            print('파일 생성 오류')
            
        return redirect('myapp:detail')
    
    # 네비게이션 바 이미지
    nav_img_home = '/static/myapp/base/home.png'
    nav_img_today = '/static/myapp/base/today.png'
    nav_img_dashboard = '/static/myapp/base/dashboard_clicked.png'
    
    
    context = {'user':user, 'log':log, 'detail':detail, 'link_sale': link_sale,
                'radar_chart':radar_path, 'dscb_name': dscb_name, 'dscb_field': dscb_field,
                'nav_img_home':nav_img_home, 'nav_img_today':nav_img_today, 'nav_img_dashboard':nav_img_dashboard}
    return render(request, 'myapp/today.html', context)


def site_wiki(request):
    login_id = request.session.get('login_id', None)
    user = User.objects.get(login_id=login_id)
    
    locations = Location.objects.all()  # 모든 위치 데이터 가져오기
    
    nav_img_home = '/static/myapp/base/home.png'
    nav_img_today = '/static/myapp/base/today.png'
    nav_img_dashboard = '/static/myapp/base/dashboard.png'
    
    context = {'user':user, 'nav_img_home':nav_img_home, 'nav_img_today':nav_img_today, 'nav_img_dashboard':nav_img_dashboard, 'sites':locations}
    return render(request, 'myapp/site_wiki.html', context)



def mypage(request):
    login_id = request.session.get('login_id', None)
    user = User.objects.get(login_id=login_id)
    log = Log.objects.filter(login_id=login_id) # 사용자의 전체 log 가져옴
    
    # 로그 기반 통계
    golajum_count = log.count()
    rated_count = log.filter(date_rated__isnull=False).count()
    rated_avg = log.filter(date_rated__isnull=False).aggregate(Avg('rating'))['rating__avg']
    
    # 프로필 사진 불러오기
    script_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(script_dir,  '..', 'static', 'myapp', 'shots')
    files = [f for f in os.listdir(path) if f.startswith(login_id) and f.endswith('.jpg')]

    if not files:
        print('평점 없음')  # 해당 유저 아이디의 파일이 없을 경우
        shot_name = 'no-rating.png' # 평점 매기라고 하는 사진 띄우기

    if files:
        file_info = []
        for file in files:
            parts = file.split('_') # 아이디_상품명_평점_날짜
            rating = int(parts[2])  # 파일 이름 (평점)에서 평점 추출
            date_rated = datetime.strptime(parts[3].split('.')[0], '%Y-%m-%d %H-%M-%S') # 파일 이름 (날짜.jpg)에서 날짜 추출
            file_info.append({'filename': file, 'rating': rating, 'date_rated':date_rated}) # 파일명, 평점, 날짜 형식 딕셔너리 생성

        # rating이 최고치인 항목 찾기
        highest_rating = max(file_info, key=lambda x: x['rating'])
        highest_rated_files = [x for x in file_info if x['rating'] == highest_rating['rating']]

        # date_rated를 기준으로 내림차순으로 정렬
        sorted_files = sorted(highest_rated_files, key=lambda x: x['date_rated'], reverse=True)
        shot_name = sorted_files[0]['filename']

    path = '../../static/myapp/shots/'+shot_name
    

    # 네비게이션 바 아이콘
    nav_img_home = '/static/myapp/base/home.png'
    nav_img_today = '/static/myapp/base/today.png'
    nav_img_dashboard = '/static/myapp/base/dashboard.png'
    
    context = {'user':user, 'nav_img_home':nav_img_home, 'nav_img_today':nav_img_today, 'nav_img_dashboard':nav_img_dashboard,
            'golajum_count':golajum_count, 'rated_count':rated_count, 'rated_avg':rated_avg, 'profile_image':path}
    return render(request, 'myapp/mypage.html', context)



def logout(request):
    if 'login_id' in request.session:
        del request.session['login_id']
    
    if 'golajum_id' in request.session:
        del request.session['golajum_id']    
    
    if 'user_id' in request.session:
        del request.session['user_id']
        
    # request.session.flush() # 로그아웃 시 세션 전체 초기화
    
    return redirect('init:begin')


def appearance(request):
    login_id = request.session.get('login_id', None)
    user = User.objects.get(login_id=login_id)
    
    if request.method == 'POST':
        user.hair_color = request.POST.get('hair_color', None)
        user.hair_style = request.POST.get('hair_style', None)
        user.hair_length = request.POST.get('hair_length', None)
        user.hair_bangs = request.POST.get('hair_bangs', None)
        user.eyelids = request.POST.get('eyelids', None)
        user.glasses = request.POST.get('glasses', None)
        user.save()
        
        return redirect('myapp:mypage')
    
    # 네비게이션 바 아이콘
    nav_img_home = '/static/myapp/base/home.png'
    nav_img_today = '/static/myapp/base/today.png'
    nav_img_dashboard = '/static/myapp/base/dashboard.png'
    
    context = {'user':user, 'nav_img_home':nav_img_home, 'nav_img_today':nav_img_today, 'nav_img_dashboard':nav_img_dashboard,}
    return render(request, 'myapp/appearance.html', context)



# Overlay
def image(request):
    login_id = request.session.get('login_id', None)
    user = User.objects.get(login_id=login_id)
    
    name = request.session.get('productName', None)
    log = Log.objects.filter(login_id=login_id, name=name).first() # dashboard-detail 눌렀을 때 저장된 상품명을 기준으로 로그 불러옴

    if log.rating != -1 : # 평점 존재
        date = log.date_rated.strftime('%Y-%m-%d %H-%M-%S') 
        shot_name = log.login_id + '_' + log.name + '_' + str(log.rating) + '_' + date
        path = '../../static/myapp/shots/'+shot_name+'.jpg'
    
    else: # 평점 미존재
        return render(request, 'myapp/image.html', {'rated':False})
    
    return render(request, 'myapp/image.html', {'image':path, 'log':log, 'user':user, 'rated':True})



def chart(request): # 취향통계보고서
    login_id = request.session.get('login_id', None)
    user = User.objects.get(login_id=login_id)    
    
    # 사용자가 평가한 log 중 최근 10개만 필터링
    log = Log.objects.filter(login_id=login_id, date_rated__isnull=False).order_by('-date_rated')
    recent_log = log[:10]
    recent_log_list = list(recent_log)

    date_from = min(recent_log, key=lambda x: x.date_rated).date_rated
    date_to = max(recent_log, key=lambda x: x.date_rated).date_rated
    
    index_list = random.sample(range(1, 7), 2) # 1~6까지 숫자중 2개 뽑기 (랜덤)
    index_list = [1,4] # 개발 전용
    chart_list_decoded = dashboard_chart(index_list, recent_log) # [['차트1이름','차트1주소'], ['차트2이름','차트2주소']
    
    context = {'user':user, 'nth':log.count()//10, 'date_from':date_from, 'date_to':date_to,
               'chart_list_decoded':chart_list_decoded}
    return render(request, 'myapp/chart.html', context)