from django.shortcuts import render, redirect
from .models import User, Input, Output, Scents, Log, Golajum
from .forms import UserInitForm, SigninForm

from django.utils import timezone

import pandas as pd
import random
import json
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from golaju_algorithm import golaju_content_init


# User 클래스 필드에 모두 null 허용해야 최초 save가 될 것

'''
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
'''

# begin.html
# 저장 없이 submit 버튼으로 다음 페이지 랜딩
def begin(request):
    # html에서 action 지정으로 랜딩
    return render(request, 'init/begin.html')


# q1.html
# 연령 5개 중 선택, 성별 2개 중 선택
# user 객체 생성 & radio 버튼으로 age, sex 저장 및 다음 페이지 랜딩 (공통)
def personal_info_create(request):
    if request.method == 'POST':
        form = UserInitForm(request.POST)
        if form.is_valid(): # Form에서 지정한 필수 필드 중 누락된 항목이 없음
            user = form.save(commit=False) # 임시 저장 (null 불가인데 null이 아직 남아있을 때)
            
            # session_id = request.session.get('user_id', None) # 현재 세션에서 session['user_id']가 존재하는지 확인
            # if session_id == None: # 존재하지 않는 경우
            user.save() # 기존 유저 아닌 경우에만 새로 저장 - 하려고 했으나 뒤로가기 시 오류 발생 가능해서 그냥 누를때마다 새로 저장할게
            request.session['user_id'] = user.unique_id # 현재 세션에 User의 autofield 값 저장 후 유지
            request.session.save()
            # print(f'신규 생성: User{user.unique_id}')
            # else: print(f'기존 유저: User{session_id}')
            
            return redirect('init:q2')
        
        else: print(form.errors) #
        
    else:
        form = UserInitForm()
    
    context = {'form': form}
    return render(request, 'init/q1.html', context) # 제대로 입력 안하면 여기서 못넘어가고 무한루프


# 이제 user 객체를 만들었으므로 모든 함수의 맨 처음에는 아래의 코드를 붙여서 연계를 해줘야 함
# user = User.objects.get(unique_id=request.session.get('user_id'))


# q2.html
# 전통주 선호 O, X 중 선택
# submit 버튼으로 다음 페이지 랜딩 (별개)
def service_select(request):
    session_login_id = request.session.get('login_id', None)
    # 최초 골라주와 다시 골라주 중 무엇으로 랜딩할지 결정
    
    if request.method == 'POST':
        jtj = request.POST.get('jtj', None)
        if jtj == 'Yes':
            return redirect('init:q3-jtj')
        if jtj == 'No':
            return redirect('init:q3')
        if jtj == 'List':
            return redirect('init:q3-list')

    return render(request, 'init/q2.html', {'session_login_id':session_login_id})




# q3-jtj.html (서비스1)
# 증류주, 탁주, 약주, 과실주 중 선택
# hidden 버튼으로 alc_type 저장 및 다음 페이지 랜딩 (공통)
def hellojtj(request):
    if request.method == 'POST':
        alc_type = request.POST.get('alc_type', '')
        print(alc_type)
        
        golajum = Golajum(alc_type=alc_type) # 골라줌 신규생성
        golajum.save()
        
        request.session['golajum_id'] = golajum.index # 세션에 임시 아이디 저장
        request.session.save()
            
        if request.session.get('login_id', None) != None: # 다시 골라주 시 (이미 로그인 했음)
            golajum.login_id = request.session.get('login_id', None) # DB에 실제 아이디 저장
            golajum.save()
            print('기존 로그인 저장 ID:', golajum.login_id)
        
        return redirect('init:q3-detail')
    
    return render(request, 'init/q3-jtj.html')



# q3.html (서비스2)
# 맥주, 소주, 와인 중 선택
# hidden 버튼으로 alc_type 저장 및 다음 페이지 랜딩 (공통)
def alc_type_select(request):
    if request.method == 'POST':
        alc_type = request.POST.get('alc_type', '')
        
        golajum = Golajum(alc_type=alc_type) # 골라줌 신규생성
        golajum.save()
        
        request.session['golajum_id'] = golajum.index # 세션에 임시 아이디 저장
        request.session.save()
            
        if request.session.get('login_id', None) != None: # 다시 골라주 시 (이미 로그인 했음)
            golajum.login_id = request.session.get('login_id', None) # DB에 실제 아이디 저장
            golajum.save()
            print('기존 로그인 저장 ID:', golajum.login_id)
                
        return redirect('init:q3-detail')
    
    return render(request, 'init/q3.html')


# q3-detail.html
# user.alc_type에 따라 보여지는 목록에 차이가 있도록 필터링
# html에서 모든 내용물이 나오도록 for문
# checkbox/submit 버튼으로 golm list 저장 및 다음 페이지 랜딩 (공통)
def alc_product_select(request):
    golajum = Golajum.objects.get(index=request.session.get('golajum_id'))
    inputs = Input.objects.filter(alc_type=golajum.alc_type)

    if request.method == 'POST':
        selected_inputs = request.POST.getlist('input[]') # 리스트 형식의 입력을 저장
        
        # 오류 리다이렉트
        min_checked = 1
        max_checked = 3
        if len(selected_inputs) < min_checked or len(selected_inputs) > max_checked:
            error_message = f"{min_checked}개 이상 {max_checked}개 이하로 선택해 주세요."
            return render(request, 'init/q3-detail.html', {'inputs': inputs, 'error_message': error_message})

        # 정상 리다이렉트
        golajum.golm = json.dumps(selected_inputs)
        golajum.save()
        
        return redirect('init:q4')
    
    return render(request, 'init/q3-detail.html', {'golajum':golajum, 'inputs': inputs})


# q3-list.html (서비스1, 다시골라주 전용)
def alc_product_select_list(request):
    # 로그인 정보 받아서 체크박스 형식 + 기추천 리스트 보이기 (context로 줘야 함)
    # 기추천 리스트 양식은 dashboard와 동일
    login_id = request.session.get('login_id', None)
    
    inputs = Log.objects.filter(login_id=login_id).order_by('-date_golajum') # log 가져옴
    inputs_names = inputs.values_list('name', flat=True) # log에 있는 술 이름들 -> 리스트로 변환
    lists = Output.objects.filter(name__in=inputs_names) # output의 술 상세정보 모두 가져옴
    
    inputs = pd.DataFrame.from_records(inputs.values())
    lists = pd.DataFrame.from_records(lists.values())
    inputs['date_rated'] = inputs['date_rated'].fillna('미평가') # from_records 거치면서 null -> NaT로 바뀌어서 인식이 안되는 문제..
    
    lists = pd.merge(inputs, lists, how='inner', on='name').iterrows()
    
    if request.method == 'POST':
        selected_inputs = request.POST.getlist('input[]') # 리스트 형식의 입력을 저장
        
        # 오류 리다이렉트
        min_checked = 1
        max_checked = 3
        if len(selected_inputs) < min_checked:
            error_message = f"{min_checked}개 이상 선택해 주세요."
            return render(request, 'init/q3-list.html', {'lists':lists, 'error_message':error_message})

        # 정상 리다이렉트
        golajum = Golajum(golm=json.dumps(selected_inputs)) # 골라줌 신규 생성
        golajum.save()
        
        request.session['golajum_id'] = golajum.index # 세션에 임시 아이디 저장
        request.session.save()
        
        if request.session.get('login_id', None) != None: # 다시 골라주 시 (이미 로그인 했음)
            golajum.login_id = request.session.get('login_id', None) # DB에 실제 아이디 저장
            golajum.save()
            print('기존 로그인 저장 ID:', golajum.login_id)
        
        return redirect('init:q3-list-alc-type')
    
    return render(request, 'init/q3-list.html', {'lists':lists})


# q3-list-alc-type.html (서비스1, 다시골라주 전용)
# 증류주, 탁주, 약주, 과실주 중 선택
# hidden 버튼으로 alc_type 저장 및 다음 페이지 랜딩 (공통)
def alc_type_select_list(request):
    golajum = Golajum.objects.get(index=request.session.get('golajum_id')) # 저장할 골라줌
    golm_list = json.loads(golajum.golm)
    golm_from_output = Output.objects.filter(name__in = golm_list)
    list = golm_from_output.values_list('alc_type', flat=True)
    
    if '탁주' in list or '약주' in list or '과실주' in list:
        if '증류주' in list:
            type = 'both'
        else:
            type = 'only_nonsoju'
    else:
        type = 'only_soju'
    
    if request.method == 'POST':
        alc_type = request.POST.get('alc_type', '')
        
        if alc_type == '랜덤':
            if type == 'both':
                alc_type = random.choice(['증류주', '탁주', '약주', '과실주'])
            if type == 'only_nonsoju':
                alc_type = random.choice(['탁주', '약주', '과실주'])
        
        golajum.alc_type = alc_type
        golajum.save()

        return redirect('init:q4')
    
    return render(request, 'init/q3-list-alc-type.html', {'type':type})



# q4.html
# 각 버튼별로 랜딩하는 페이지 종류를 다르게 해야 함
# hidden 버튼으로 factor 저장 및 다음 페이지 랜딩 (개별: user.alc_type, factor)
def factor_select(request):
    if request.method == 'POST':
        factor = request.POST.get('factor')
        
        golajum = Golajum.objects.get(index=request.session.get('golajum_id'))
        if golajum.alc_type == '소주' or golajum.alc_type == '증류주':
            if factor == '향':
                return redirect('init:q4-scentorstrong')
            if factor == '맛':
                golajum.factor = 'sweet'
                golajum.save()
                
                return redirect('init:q5')
            if factor == '질감':
                golajum.factor = 'body'
                golajum.save()
                
                return redirect('init:q5')
            
        else:
            if factor == '향':
                golajum.factor = 'scent'
                golajum.save()
                
                return redirect('init:q4-scent-select')
            if factor == '맛':
                return redirect('init:q4-sweetorsour')
            if factor == '질감':
                return redirect('init:q4-bodyorfizzy')
    
    return render(request, 'init/q4.html')


# q4-scentorstrong.html
# 향의 종류, 향의 강도 중 선택
# hidden 버튼으로 factor 저장 및 다음 페이지 랜딩 (개별: factor)
def scentorstrong_select(request):
    if request.method == 'POST':
        factor = request.POST.get('factor', '')
        
        golajum = Golajum.objects.get(index=request.session.get('golajum_id'))
        
        if factor == 'scent':
            golajum.factor = 'scent'
            golajum.save()
                        
            return redirect('init:q4-scent-select')
        if factor == 'strong':
            golajum.factor = 'strong'
            golajum.save()
            
            return redirect('init:q5')
    
    return render(request, 'init/q4-scentorstrong.html')


# q4-sweetorsour.html
# 단맛, 신맛 중 선택
# hidden 버튼으로 factor 저장 및 다음 페이지 랜딩 (공통)
def sweetorsour_select(request):
    if request.method == 'POST':
        factor = request.POST.get('factor', '')
        
        golajum = Golajum.objects.get(index=request.session.get('golajum_id'))
        
        golajum.factor = factor
        golajum.save()
        
        
        return redirect('init:q5')
    
    return render(request, 'init/q4-sweetorsour.html')
                


# q4-bodyorfizzy.html
# 바디감, 청량감 중 선택
# hidden 버튼으로 factor 저장 및 다음 페이지 랜딩 (공통)
def bodyorfizzy_select(request):
    if request.method == 'POST':
        factor = request.POST.get('factor', '')
        
        golajum = Golajum.objects.get(index=request.session.get('golajum_id'))
        
        golajum.factor = factor
        golajum.save()
        
        
        return redirect('init:q5')
    
    return render(request, 'init/q4-bodyorfizzy.html')


# q4-scent-select.html
# 향의 종류 복수선택 가능 (제한 없음)
# checkbox/submit 버튼으로 scent list 저장 및 다음 페이지 랜딩 (공통)
def scent_select(request):
    scents = Scents.objects.all()
    
    golajum = Golajum.objects.get(index=request.session.get('golajum_id'))
    
    if request.method == 'POST':
        selected_scents = request.POST.getlist('scent[]') # 리스트 형식의 입력을 저장
        
        # 오류 리다이렉트
        min_checked = 1
        if len(selected_scents) < min_checked:
            error_message = f"{min_checked}개 이상 선택해 주세요."
            return render(request, 'init/q4-scent-select.html', {'scents': scents, 'error_message': error_message})

        # 정상 리다이렉트
        golajum.scent = json.dumps(selected_scents) # 리스트 형식으로 바꿔서 DB에 저장
        golajum.save()
        
        return redirect('init:q5')
    
    return render(request, 'init/q4-scent-select.html', {'scents': scents})


# q5.html
# 절대 도수 (0) vs 상대 도수 (1) 선택
# hidden 버튼으로 alc_range_bool 저장 및 다음 페이지 랜딩 (공통)
def alc_range_bool_select(request): 
    if request.method == 'POST':
        alc_range_bool = request.POST.get('alc_range_bool', '')
        
        golajum = Golajum.objects.get(index=request.session.get('golajum_id'))
        
        golajum.alc_range_bool = alc_range_bool
        golajum.save()
        
        return redirect('init:q6')
    
    return render(request, 'init/q5.html')


# q6.html
# 가성비 좋음 (1) vs 상관 없음 (0) 선택
# hidden 버튼으로 CE_good_bool 저장 및 다음 페이지 랜딩 (공통)
def CE_good_bool_select(request):
    if request.method == 'POST':
        CE_good_bool = request.POST.get('CE_good_bool', '')
        
        golajum = Golajum.objects.get(index=request.session.get('golajum_id'))
        
        golajum.CE_good_bool = CE_good_bool
        golajum.save()
        
        return redirect('init:result')
    
    return render(request, 'init/q6.html')


# result.html
# 알고리즘 돌려!!!!!!!!!!!
# html: 결과에 따라서 띄우는 값 달라야 함
# submit 버튼으로 myapp으로 이동하기
def result(request):
    golajum = Golajum.objects.get(index=request.session.get('golajum_id'))
    result = golaju_content_init(golajum) # dict
    
    context = {'golajum':golajum} | result # dict끼리 연결
    return render(request, 'init/result.html', context)


# signin.html
# 문제(아이디 중복, 비밀번호 불일치, 필수값 미입력) 있는 경우 현재 페이지로 렌더링
# 문제 없는 경우 입력값을 현재 활성화 세션에 저장하고 myapp으로 전환
def signin(request):
    user = User.objects.get(unique_id=request.session.get('user_id')) # 유저정보에 ID 등록진행
    golajum = Golajum.objects.get(index=request.session.get('golajum_id')) # 골라줌에 ID 등록진행
    
    if request.method == 'POST':
        form = SigninForm(request.POST)
        
        if form.is_valid():
            login_id = form.cleaned_data['아이디']
            login_pw = form.cleaned_data['비밀번호']
            login_pw_confirm = form.cleaned_data['비밀번호_확인']
            username = form.cleaned_data.get('닉네임', None)
            
            # 정상 리다이렉트
            if login_pw == login_pw_confirm:
                # 유저 정보 저장
                user.login_id = login_id
                user.login_pw = login_pw
                user.username = username
                
                # 유저 기본 외형정보 설정 (빈칸)
                user.hair_color = ' '
                user.hair_style = ' '
                user.hair_length = ' '
                user.hair_bangs = 'without'
                user.eyelids = ' '
                user.glasses = ' '
                user.save() 
                
                golajum.login_id = login_id
                golajum.save()
                
                now = timezone.now()
                
                # 추천 로그 저장 (서비스1에서 선택한 것, 사용자 기반 때 데이터 축적하기 위함)
                '''
                if golajum.alc_type == '증류주' or golajum.alc_type == '탁주' or golajum.alc_type == '약주' or golajum.alc_type == '과실주':
                    for product_name in json.loads(golajum.golm):
                        product = Output.objects.get(name=product_name)
                        golajun = Log(login_id=login_id, name=product.name, alc_type=product.alc_type, date_golajum=now, date_checked=now, date_rated=now, rating=5)
                        golajun.save()
                '''
                
                # 추천 로그 저장 (최종 추천받은 것)
                product = Output.objects.get(name=golajum.golajum)
                golajun = Log(login_id=login_id, name=product.name, alc_type=product.alc_type, date_golajum=now, rating=-1) # 추천 but 미평가 시 -1로 저장
                golajun.save()
                
                request.session['login_id'] = user.login_id
                return redirect('myapp:home')
            
            # 오류 리다이렉트
            else: error_message = '비밀번호 일치여부를 확인하세요.' # 
            
        else: # 왜 POST가 아닌데 .. 이게 뜨고있지..?
            print(form.errors)
            error_message = '아이디 중복 또는 필수 항목 입력 여부를 확인하세요.'
    
    else:
        # 오류를 무시하는 코드
        form = SigninForm()
        error_message = None
    
    
    context = {'form': form, 'error_message': error_message} # ValidtionError로 검증하면 error_message 불필요
    return render(request, 'init/signin.html', context)


def save(request):
    golajum = Golajum.objects.get(index=request.session.get('golajum_id')) # 골라줌에 ID 등록진행
    login_id = request.session.get('login_id', None)
    
    now = timezone.now()
    
    # 추천 로그 저장 (서비스1에서 선택한 것, 사용자 기반 때 데이터 축적하기 위함)
    '''
    if golajum.alc_type == '증류주' or golajum.alc_type == '탁주' or golajum.alc_type == '약주' or golajum.alc_type == '과실주':
        for product_name in json.loads(golajum.golm):
            product = Output.objects.get(name=product_name)
            golajun = Log(login_id=login_id, name=product.name, alc_type=product.alc_type, date_golajum=now, date_checked=now, date_rated=now, rating=5)
            golajun.save()
    '''
    
    # 추천 로그 저장 (최종 추천받은 것)
    product = Output.objects.get(name=golajum.golajum)
    golajun = Log(login_id=login_id, name=product.name, alc_type=product.alc_type, date_golajum=now, rating=-1) # 추천 but 미평가 시 -1로 저장
    golajun.save()
    
    # request.session['login_id'] = user.login_id # 이미 세션에 있음
    return redirect('myapp:home')
