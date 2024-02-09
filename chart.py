from init.models import Output

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.patches import FancyArrowPatch


import json
import os
from collections import Counter, defaultdict

import base64
from io import BytesIO

# 한글폰트 설정
# 현재 스크립트 파일의 경로를 얻음
current_path = os.path.dirname(os.path.abspath(__file__))

# 폰트 파일의 상대 경로 설정 (예: 현재 경로에 fonts 폴더가 있고 그 안에 폰트 파일이 있음)
font_path = os.path.join(current_path, 'static/PretendardVariable.ttf')

# 폰트 속성 설정 및 전역 폰트 변경
plt.rcParams['font.family'] = 'PretendardVariable'
plt.rcParams['font.size'] = 20
plt.rcParams['font.weight'] = 'extra bold'
plt.rcParams['axes.unicode_minus'] = False  # 마이너스 기호 표시 문제 해결

# 폰트 매니저를 사용하여 폰트 설정
font_prop = fm.FontProperties(fname=font_path)
font_prop_small = fm.FontProperties(fname=font_path, size=16)
font_prop_bold = fm.FontProperties(fname=font_path, weight='extra bold')    
    
    
def radar(golajum):
    # 유저의 가상술 좌표
    dscb_user = json.loads(golajum.dscb)
    
    # 추천받은 술 좌표
    detail = Output.objects.get(name=golajum.golajum)
    dscb_golajum = [detail.sweet, detail.sour, detail.fizzy, detail.body, detail.strong]
    
    # 각 좌표의 특성명 (레이블)
    features = ['단맛', '신맛', '청량감', '바디감', '향의 강도']
    
    
    # 제외할 특성 제거
    remove_index = []
    for i in range(5):
        if dscb_golajum[i] == None:
            remove_index.append(i)
    
    for index in sorted(remove_index, reverse=True):
        del features[index]
        del dscb_user[index]
        del dscb_golajum[index]


    # 레이더 차트 그리기
    num_features = len(features)
    angles = np.linspace(0, 2 * np.pi, num_features, endpoint=False).tolist()
    angles += angles[:1]  # 레이더 차트를 닫기 위해 시작점을 끝에 다시 추가

    fig, ax = plt.subplots(figsize=(7,7), subplot_kw=dict(polar=True))

    # 추천받은 술 좌표
    values_output = [dscb_golajum[i] for i in range(len(dscb_golajum))] + [dscb_golajum[0]]
    ax.plot(angles, values_output, color="#C36576", label='추천 전통주', linewidth=10)
    ax.fill(angles, values_output, fill=False)  # 내부 색칠 없음
    scatter2 = ax.scatter(angles, values_output, color="#C36576", s=200)  # 각 꼭지점에 표식 추가
    
    # 유저의 가상술 좌표
    values_dscb = [dscb_user[i] for i in range(len(dscb_user))] + [dscb_user[0]]
    ax.plot(angles, values_dscb, color=(38/255, 13/255, 0/255, 0.7), label='나의 취향', linewidth=5)
    ax.fill(angles, values_dscb, fill=False)  # 내부 색칠 없음
    scatter1 = ax.scatter(angles, values_dscb, color=(38/255, 13/255, 0/255, 0.7), s=100)  # 각 꼭지점에 표식 추가


    # 그리드와 원형 배경 제거
    fig.patch.set_alpha(0)  # 전체 배경 투명하게 설정
    ax.grid(False)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(features, fontproperties=font_prop)
    ax.set_frame_on(False)  # 배경 원 제거
    ax.set_yticklabels([])

    # 다각형 배경 그리기
    num_vars = len(angles)
    for r in range(1, 6):  # 1부터 5까지의 레벨 (또는 필요한 만큼의 레벨)
        polygon = [r] * num_vars
        ax.plot(angles, polygon, '-', lw=1, color='gray', alpha=0.6)
        
        
    # 위치 조정
    ax.set_position([0.1, 0.2, 0.75, 0.75])
    ax.legend([scatter1, scatter2], ['나의 취향', '추천 전통주'],
              loc='lower center', bbox_to_anchor=(0.5, -0.3), prop=font_prop, ncol=2)

    # 차트 제목 설정
    # plt.title('내 취향과 비교', fontsize=14, color='navy')

    # 차트 표시
    # plt.show()
    
    
    # 그래프를 메모리에 저장
    buffer = BytesIO()
    fig.savefig(buffer, format='png')
    buffer.seek(0)
    
    # base64로 인코딩
    image_png = buffer.getvalue()
    buffer.close()
    image_base64 = base64.b64encode(image_png)
    image_base64 = image_base64.decode('utf-8')

    return image_base64



def dashboard_chart(index_list, recent_log):
    chart_list = [] # ex. chart_list = [fig1, fig2]
    chart_list_decoded = []

    
    # log&output 병합
    log_names = [log_item.name for log_item in recent_log] # log의 name의 리스트
    lists = Output.objects.filter(name__in=log_names) # output의 술 상세정보 모두 가져옴
    
    inputs = pd.DataFrame.from_records(recent_log.values())
    lists = pd.DataFrame.from_records(lists.values())
    inputs['date_rated'] = inputs['date_rated'].fillna('미평가') # from_records 거치면서 null -> NaT로 바뀌어서 인식이 안되는 문제..
    
    merged = pd.merge(inputs, lists, how='inner', on='name') # 상세정보 df: 전체
    # print(merged)
    
    # alc_type이 겹쳐서 두개 생김
    merged.drop('alc_type_x', axis=1, inplace=True) # 제거
    merged.rename(columns={'alc_type_y': 'alc_type'}, inplace=True) # 이름 원래대로
    # print(merged)
    
    merged_over3 = merged[merged['rating'] >= 3] # 상세정보 df: 3점 이상
    
    
    if 1 in index_list: # 주종: 빈도+평점
        
        # 딕셔너리 (주종별 평균평점)
        dd = defaultdict(list)
        for log_item in recent_log:
            dd[log_item.alc_type].append(log_item.rating)
        ratings = {alc_type: sum(rating) / len(rating) for alc_type, rating in dd.items()}


        # 딕셔너리 (주종별 빈도수)
        counts = Counter(log_item.alc_type for log_item in recent_log) 

        
        # 그래프 설정
        fig1 = plt.figure(figsize=(7,7))
        fig1.patch.set_facecolor('none')
        
        
        # 주종별 빈도수
        ax1 = fig1.add_subplot(111)
        bar = ax1.bar(counts.keys(), counts.values(), color=[('#C36576' if count == max(counts.values()) else (0.149, 0.051, 0, 0.2)) for count in counts.values()], width=0.3)

        for i, (alc_type, count) in enumerate(counts.items()):
            if count == max(counts.values()):
                ax1.text(i, count+0.2, str(count) + '회', ha='center', va='bottom', color='#1B0900', fontproperties=font_prop_bold,
                        bbox=dict(facecolor='white', edgecolor='None'))
                
                
        ax1.set_ylim(0, max(counts.values())+3)
        ax1.set_yticks([])  # y축 눈금 제거

        # 주종별 평균별점
        ax2 = ax1.twinx()
        line, = ax2.plot(ratings.keys(), ratings.values(), linestyle='--', marker='o', color=(0.149, 0.051, 0, 0.2), lw=5, markersize=10)

        for x, y in zip(ratings.keys(), ratings.values()):
            if y == max(ratings.values()):
                plt.plot(x, y, linestyle='--', marker='o', color='#C36576', lw=5, markersize=10)
            else:
                plt.plot(x, y, linestyle='--', marker='o', color=(0.8235, 0.7843, 0.7647, 1.0), lw=5, markersize=10)
                
        for i, (alc_type, rating) in enumerate(ratings.items()):
            if rating == max(ratings.values()):
                ax2.text(i, rating+0.2, f'{rating:.1f}' + '점', ha='center', va='bottom', color='#1B0900', fontproperties=font_prop_bold,
                        bbox=dict(facecolor='white', edgecolor='None'))

        ax2.set_ylim(2, 6)
        ax2.set_yticks([])  # y축 눈금 제거


        # 그래프 상자를 감싸는 선 없애기
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        ax1.spines['left'].set_visible(False)
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        ax2.spines['left'].set_visible(True)
        
        
        # x축, 범례 설정
        ax1.set_xlabel('주종', fontproperties=font_prop)        
        ax1.set_xticklabels(ax1.get_xticklabels(), fontproperties=font_prop)
        plt.legend([bar, line], ['빈도수', '평균 평점'], loc='upper center', prop=font_prop_small, ncol=2)
        
        ax1.set_ylabel('', fontproperties=font_prop, rotation=0, labelpad=40)
        ax1.annotate('빈도\n평점', xy=(-0.15, 0.9), xycoords='axes fraction', fontproperties=font_prop)


        # 저장
        chart_list.append(['주종별 요약', fig1])
    
    
    if 2 in index_list: # 향의 종류: 빈도
        fig2, ax = plt.subplots(figsize=(7,7), subplot_kw=dict(polar=True))
        chart_list.append(['나에게 어울리는 향 TOP2', fig2])
        
        
    if 3 in index_list: # 향의 종류: 빈도+평점
        fig3, ax = plt.subplots(figsize=(7,7), subplot_kw=dict(polar=True))
        chart_list.append(['내가 사랑한 향 TOP2', fig3])
        
    
    if 4 in index_list: # DSCB-Flavor: 3점 이상의 단순평균
        # 유저의 취향 통계
        myTaste = merged_over3[['sweet', 'sour', 'fizzy', 'body', 'strong']].mean().tolist()
        
        # 각 좌표의 특성명 (레이블)
        features = ['단맛', '신맛', '청량감', '바디감', '향의 강도']
        
        
        # 제외할 특성 제거
        remove_index = []
        for i in range(5):
            if np.isnan(myTaste[i]):
                remove_index.append(i)

        for index in sorted(remove_index, reverse=True):
            del myTaste[index]
            del features[index]
        
        
        # 레이더 차트 그리기
        num_features = len(features)
        angles = np.linspace(0, 2 * np.pi, num_features, endpoint=False).tolist()
        angles += angles[:1]  # 레이더 차트를 닫기 위해 시작점을 끝에 다시 추가

        fig4, ax = plt.subplots(figsize=(7,7), subplot_kw=dict(polar=True))

        # 추천받은 술 좌표
        values_output = [myTaste[i] for i in range(len(myTaste))] + [myTaste[0]]
        ax.plot(angles, values_output, color="#C36576", label='추천 전통주', linewidth=2)
        ax.fill(angles, values_output, color=(0.7647, 0.3961, 0.4627, 0.4))
        scatter = ax.scatter(angles, values_output, color="#C36576", s=100)  # 각 꼭지점에 표식 추가
        

        # 그리드와 원형 배경 제거
        fig4.patch.set_alpha(0)  # 전체 배경 투명하게 설정
        ax.grid(False)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(features, fontproperties=font_prop)
        ax.set_frame_on(False)  # 배경 원 제거
        ax.set_yticklabels([])

        # 다각형 배경 그리기
        num_vars = len(angles)
        for r in range(1, 6):  # 1부터 5까지의 레벨 (또는 필요한 만큼의 레벨)
            polygon = [r] * num_vars
            ax.plot(angles, polygon, '-', lw=1, color='gray', alpha=0.6)

        chart_list.append(['선호하는 주류 속성', fig4])
        
        
        
    if 5 in index_list: # 도수: 단순평균
        fig5, ax = plt.subplots(figsize=(7,7), subplot_kw=dict(polar=True))       
        chart_list.append(['나의 술 레벨', fig5])
        
        
    if 6 in index_list: # 가격: 가격총합 / 2500
        fig6, ax = plt.subplots(figsize=(7,7), subplot_kw=dict(polar=True))  
        chart_list.append(['이 돈이면 맥주가...', fig6])
    
    
    
    for name, chart in chart_list:
        # 그래프를 메모리에 저장
        buffer = BytesIO()
        chart.savefig(buffer, format='png')
        buffer.seek(0)
        
        # base64로 인코딩
        image = buffer.getvalue()
        buffer.close()
        chart = base64.b64encode(image).decode('utf-8')

        chart_list_decoded.append([name, chart])
    
    return chart_list_decoded