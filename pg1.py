#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 14 15:04:20 2023

@author: woneunglee
"""

import streamlit as st
st.set_page_config(layout='wide')

import pandas as pd

import plotly.io as io
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots


#%% bg 생성

def bgLevels(fig, df, variable, level, mode, fillcolor, layer):
    """
    Set a specified color as background for given
    levels of a specified variable using a shape.

    Keyword arguments:
    ==================
    fig -- plotly figure
    variable -- column name in a pandas dataframe
    level -- int or float
    mode -- set threshold above or below
    fillcolor -- any color type that plotly can handle
    layer -- position of shape in plotly fiugre, like "below"

    """

    if mode == 'above':
        m = df[variable].gt(level)

    if mode == 'below':
        m = df[variable].lt(level)

    df1 = df[m].groupby((~m).cumsum())['date'].agg(['first','last'])

    for index, row in df1.iterrows():
        #print(row['first'], row['last'])
        fig.add_shape(type="rect",
                        xref="x",
                        yref="paper",
                        x0=row['first'],
                        y0=0,
                        x1=row['last'],
                        y1=1,
                        line=dict(color="rgba(0,0,0,0)",width=3,),
                        fillcolor=fillcolor,
                        layer=layer)
    return(fig)

#%% 제목

st.title("1번 이름")


#%% 데이터 불러오고 가공
news_data = pd.read_csv("카카오+김범수_.csv")
news_data = news_data.iloc[:2209] # 8월 4일 시작
news_data = news_data.iloc[:1975] #9월 1일시작 (가상화폐 소송 시작 정도)
news_data = news_data.iloc[:1840] #10월 2일시작 차트 깔끔
news_data = news_data.dropna()


#%% 언론사 그룹생성

신문사 = [ "강원도민일보",       "경기일보",       "경향신문",       "국민일보",       "국제신문",       "대전일보",       "동아일보",
       "디지털타임스",       "매일경제",       "매일신문",       "머니투데이",       "문화일보",       "부산일보",       "서울경제",
       "서울신문",       "세계일보",       "전자신문",       "조선일보",       "조세일보",       "중앙일보",       "파이낸셜뉴스",
       "한겨레",       "한국경제",       "한국일보",       "헤럴드경제",       "조선비즈"]

방송사 = ["JTBC",       "KBS",       "MBC",
       "MBN",       "SBS",       "TV조선",
       "YTN",       "채널A",       "한국경제TV",       "연합뉴스TV",
       ]

통신사 = ["뉴스1",
       "뉴시스",
       "연합뉴스"
       ]


언론_종류_df = pd.DataFrame( 
    [
         신문사 + 방송사 + 통신사,
         ["신문사"] * len(신문사) + ["방송사"] * len(방송사) + ["통신사"] * len(통신사)
    ],
    index = ["언론사명", "종류"]                            
    ).T

news_data = pd.merge(news_data, 
                   언론_종류_df,
                   how = "left",
                   left_on = ["media1"], 
                   right_on = ["언론사명"])


#%% 시간 -> 일자 생성
news_data["date"] = pd.to_datetime( news_data.time.str[:10], format = "%Y-%m-%d" )

#%% 받아올 정보

col11, col12, col13 = st.columns(3)

with col12:
    option_언론사종류 = st.selectbox(
        "언론사 종류를 선택하세요",
        ['전체', '신문사', '방송사', '통신사', '기타' ],
        index = 4,
    )

with col13:
    text = st.text_input('검색하고자 하는 단어를 입력하세요', '구속')


#%% 받아올 정보 2
col21, col22, col23, col24 = st.columns(4)

#line chart의 스케일 분리할까요?
#with col23:
#    second_Y = st.toggle('Secondary Y?')

# 주말 음영 표기 필요한가요?
with col24:
    bg_weekend = st.toggle('주말 음영 표기 여부')

#%% 차트 그리기
with st.spinner("검색 중입니다..."):

    news_data[text + "_(등장_횟수)"] = news_data["content"].str.count(text)
    
    chart_1_df = news_data[[ "date", "media1", text + "_(등장_횟수)",  '언론사명', '종류']]
    
    #언론사별 단어 등장 횟수 barchart
    chart_1_df["종류"] = chart_1_df["종류"].fillna("기타")
    
    if option_언론사종류 != "전체":
        chart_1_df = chart_1_df[chart_1_df["종류"] == option_언론사종류]
                      
    
    
    
    
    #fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig =  px.histogram( chart_1_df, x = "date", y = text + '_(등장_횟수)', color = "media1", barmode = 'group')
    
    기사_count_line_plot_df = chart_1_df.groupby(["date"]).count()
    
    fig.add_trace(
        go.Scatter(
            name="기사 개재 건수",
            x = 기사_count_line_plot_df.index,
            y = 기사_count_line_plot_df.media1,
        ),
        #secondary_y = second_Y
    )
    
    기사_count_line_plot_df = chart_1_df.groupby(["date"]).sum()
    
    fig.add_trace(
        go.Scatter(
            name= "단어 [ " + text +" ] 등장 횟수",
            x = 기사_count_line_plot_df.index,
            y = 기사_count_line_plot_df[text + '_(등장_횟수)'],
        ),
        #secondary_y = second_Y
    )
    
    
    max_언론사 = chart_1_df.groupby("media1")[text + '_(등장_횟수)'].sum().idxmax()
    
    fig.add_trace(
        go.Scatter(
            name= max_언론사 + "에서의 단어 [ " + text +" ] 등장 횟수",
            x = chart_1_df[chart_1_df["media1"] == max_언론사].groupby("date").sum().index,
            y = chart_1_df[chart_1_df["media1"] == max_언론사].groupby("date").sum()[text + '_(등장_횟수)'],
        ),
        #secondary_y = second_Y
    )
    
    
    if bg_weekend:
        
        chart_1_df["is_weekend"] = ( chart_1_df["date"].dt.dayofweek > 4 ).astype(int)
        
        fig = bgLevels(fig,
                   chart_1_df,
                   "is_weekend",
                   level = 0.5,
                   mode = 'above',
                   fillcolor = 'rgba(100,100,100,0.2)',
                   layer ='below')
    
st.plotly_chart( fig , use_container_width=True) 

