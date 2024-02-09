from init.models import User, Input, Output, Scents, Log

import pandas as pd
import numpy as np
import json

# init/user = User.objects.get(unique_id=request.session.get('user_id'))
# user 이라는 객체(행) 불러와서 작업할 것임 (ex. user.alc_type)
def golaju_content(user): # 콘텐츠 기반 알고리즘, 가중된 거리를 포함한 df 반환
    golm_list = json.loads(user.golm) # 최초 추천때 선택한 술들
    print(golm_list)    
    
    user_input = Input.objects.filter(name__in = golm_list) # 최초 추천때 선택한 술들의 정보
    user_input = pd.DataFrame.from_records(user_input.values()) # df로 변환
    print(user_input)
    
    if len(golm_list) != len(user_input): # input에 고른 술이 존재하지 않을 경우
        user_input = Output.objects.filter(name__in = golm_list) # output에서 가져와야 함! (다시 골라주 - 기추천 술에서 가져오기)
        user_input = pd.DataFrame.from_records(user_input.values()) # df로 변환
        print(user_input)
        
    # 1) 대표 DSCB-Flavor 생성 알고리즘
    # 일단 평균
    user_input_means = user_input[user_input.select_dtypes(include='number').columns].mean()
    # user_input_means = user_input_means[['sweet', 'sour', 'fizzy', 'body', 'strong', 'alc_range', 'alc_ab']] # 사용할 열만 미리 걸러놓기
    print(user_input_means)
    
    
    # 1-1) 레이다 차트를 위해 가져가줌
    factors = ['sweet', 'sour', 'fizzy', 'body', 'strong']
    myDSCB = []
    for factor in factors: # 사용할 열 가져오기
        # 'factor'에 해당하는 열이 'user_input_means'에 존재하는지 확인
        if factor in user_input_means.index:
            myDSCB.append(user_input_means[factor])
        else:
            myDSCB.append(0)
    print(myDSCB) # list
    
    user.dscb = json.dumps(myDSCB)
    user.save()
    
    '''
    # 1-1) 유저 평가에 따라 대표 술 좌표 수정
    # rating_dict = {'sweet_rating':-1, 'sour_rating':0, 'fizzy_rating':0, 'body_rating':0, 'strong_rating':0, 'alc_range_rating':0}
    def one_five(score): # 새로운 값이 1 이상 5 이하의 값만 갖도록 함
        return max(1, min(score, 5))
    
    if rating_dict:
        sweet_new = one_five(user_input_means.sweet + rating_dict.sweet_rating) 
        sour_new = one_five(user_input_means.sour + rating_dict.sour_rating)
        fizzy_new = one_five(user_input_means.fizzy + rating_dict.fizzy_rating)
        body_new = one_five(user_input_means.body + rating_dict.body_rating)
        strong_new = one_five(user_input_means.strong + rating_dict.strong_rating)
        alc_range_new = one_five(user_input_means.alc_range + rating_dict.alc_range_rating)
        user_input_means = {'sweet':sweet_new, 'sour':sour_new, 'fizzy':fizzy_new, 'body':body_new, 'strong':strong_new, 'alc_range':alc_range_new} # 새로운 user_input_means 생성 
    else:
        pass
    '''
    
    if user.alc_type == '소주' or user.alc_type == '증류주':
        user_alcohol = pd.Series({
            'sweet': user_input_means.sweet,
            'body': user_input_means.body,
            'strong': user_input_means.strong,
            'alc_range': user_input_means.alc_range
        })
        
        myOutput = Output.objects.filter(alc_type = '증류주')
        
    else: # 와인, 맥주 / 탁주, 약주, 과실주
        user_alcohol = pd.Series({
            'sweet': user_input_means.sweet,
            'sour': user_input_means.sour,
            'fizzy': user_input_means.fizzy,
            'body': user_input_means.body,
            'alc_range':user_input_means.alc_range
        })
        
        if user.alc_type == '와인':
            myOutput = Output.objects.filter(alc_type__in = ['약주', '과실주'])
        if user.alc_type == '맥주':
            myOutput = Output.objects.filter(alc_type__in = ['탁주', '과실주'])
        if user.alc_type == '탁주':
            myOutput = Output.objects.filter(alc_type = '탁주')
        if user.alc_type == '약주':
            myOutput = Output.objects.filter(alc_type = '약주')
        if user.alc_type == '과실주':
            myOutput = Output.objects.filter(alc_type = '과실주')

    
    myOutput = pd.DataFrame.from_records(myOutput.values()) # df로 변환
    myOutput = myOutput[~myOutput['name'].isin(golm_list)] # golm_list에 존재하는 선택한 술은 제외
        
    if user.login_id: # 기존 유저일 경우
        myLog = Log.objects.filter(login_id=user.login_id).values('name')
        myLog = pd.DataFrame.from_records(myLog)
        log_list = myLog['name']
        
        myOutput = myOutput[~myOutput['name'].isin(log_list)] # Log에 존재하는 기추천 술은 제외
    
    
    # 2) CE-based 필터링 알고리즘
    if user.CE_good_bool == 1:
        myOutput = myOutput[myOutput.CE_good == 1]
    else: pass # 0
        
    
    # 3) 절대 도수 필터링 알고리즘 + 상대 도수 좌표편입 알고리즘
    if user.alc_range_bool == 0:
        avg_alc = user_input_means.alc_ab
        lower = avg_alc -3 # 조정 필요
        upper = avg_alc +3
        
        myOutput = myOutput.query('@lower <= alc_ab <= @upper')
        user_alcohol.drop('alc_range')
        
    else: pass # 1
    
    
    # 4) 유클리드 거리계산 알고리즘
    myOutput['dist'] = np.linalg.norm(myOutput[user_alcohol.index] - np.array(user_alcohol), axis=1)
    
    
    # 5) 향의 종류 가중치 알고리즘 + DSCB-Flavor 중요도 가중치 알고리즘
    if user.factor == 'scent': # 향의 종류
        def split_to_list(row):
            scents_list = row.scent.split(', ')
            return scents_list
        myOutput['scent_list'] = myOutput.apply(split_to_list, axis=1)
        # myOutput['wdist'] = myOutput.apply(lambda output: output['dist']
        #                                 * max(0.2, 1-sum(1 for flavor in json.loads(user.scent) if flavor in output.scent_list / len(output.scent_list))))
    
        user_scent_list = json.loads(user.scent)
        wdist = []
        
        for _, output in myOutput.iterrows(): # myOutput에서 한 행씩 불러옴
            weight = max(0.2, 1- (len(set(output.scent_list) & set(user_scent_list)) / len(output.scent_list)))
            wdist.append(output['dist'] * weight)
            
        myOutput['wdist'] = wdist
            
    else: # 그 외
        myOutput['wdist'] = myOutput.dist * ((abs(myOutput[user.factor] - user_alcohol[user.factor]) + 1) / 5) # 'sweet'이 중요하고 1일 경우, 
        
    print(myOutput)    
    return myOutput


def golaju_content_init(user): # 최초 술 추천
    myOutput = golaju_content(user)
    
    golajum = myOutput.loc[myOutput['wdist'].idxmin()]
    print(golajum)

    product_name = golajum.iloc[0]
    alc_type = golajum.alc_type
    alc_ab = golajum.alc_ab
    ml = golajum.ml
    price = golajum.price
    link_img = golajum.link_img
    
    # 최초 추천 술 기록
    user.golajum = product_name
    user.save()
    
    return {'이름': product_name, '주종':alc_type, '도수': alc_ab, '용량': ml, '가격': price, '사진': link_img}














# myapp/user = User.objects.get(login_id=request.session.get('login_id', None))
def golaju_content_daily(user): # 매일 술 추천, 이거 함수 짜서 정기적으로 돌려야 함
    myOutput = golaju_content(user)
    
    # 기추천 목록에 없는 것으로 추천
    myLog = list(Log.objects.filter(login_id=user.login_id))
    
    imi_golajun = [] # 기추천 목록
    for product in myLog:
        imi_golajun.append(product.name)
    
    
    # 이전 로그의 평가 반영
    
    
    
    name = ''
    
    
    # 신규 로그 기록 생성
    golajun = Log(login_id=user.login_id, name=name)
    golajun.save()
    
    return golajun



def routine(user):
    if Log.objects.order_by('date_golajum').first().date_checked: # 가장 최근 추천을 확인했을 경우
        golaju_content_daily(user) # 추천 추가요
    else: pass