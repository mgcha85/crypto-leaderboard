import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
import plotly.express as px
from postgres import Postgres


st.set_page_config(page_title="가상화폐 Backtest Dashboard", layout="wide")

pg = Postgres('binance')

# Streamlit UI
st.title("가상화폐 Backtest Dashboard")

# 탭 생성
tab1, tab2 = st.tabs(["Leaderboard", "Monthly Returns"])

# 첫 번째 탭: 리더보드 테이블
with tab1:
    st.subheader("Leaderboard")
    leaderboard_query = '''
    SELECT algorithm_name, init_money, backtest_start, backtest_end, final_return, mdd, win_rate, timeframe, backtest_range
    FROM leaderboard.backtest_results
    ORDER BY final_return DESC
    '''
    leaderboard_df = pd.read_sql(leaderboard_query, pg.engine)
    st.dataframe(leaderboard_df)

# 두 번째 탭: 월별 수익률 조회
with tab2:
    st.subheader("Select Algorithm to View Monthly Returns")
    
    # 알고리즘 목록 가져오기
    algorithm_query = "SELECT DISTINCT algorithm_name FROM leaderboard.backtest_results"
    algorithms = pd.read_sql(algorithm_query, pg.engine)['algorithm_name'].tolist()
    
    # 드롭다운으로 알고리즘 선택
    selected_algorithm = st.selectbox("Choose an Algorithm", algorithms)
    
    if selected_algorithm:
        # 선택한 알고리즘의 백테스트 ID 가져오기
        backtest_query = '''
        SELECT id, backtest_start, backtest_end
        FROM leaderboard.backtest_results
        WHERE algorithm_name = %s
        ORDER BY backtest_start DESC
        '''
        backtests_df = pd.read_sql(backtest_query, pg.engine, params=(selected_algorithm,))
        
        # 백테스트 ID를 선택하여 월별 수익률 표시
        selected_id = st.selectbox("Choose Backtest ID", backtests_df['id'])
        
        if selected_id:
            # backtest_rawdata 테이블에서 월별 수익률 계산
            monthly_query = '''
            SELECT 
                EXTRACT(YEAR FROM entry_time) AS year,
                EXTRACT(MONTH FROM entry_time) AS month,
                SUM(profit) AS monthly_return
            FROM leaderboard.backtest_rawdata
            WHERE backtest_id = %s
            GROUP BY year, month
            ORDER BY year, month
            '''
            monthly_df = pd.read_sql(monthly_query, pg.engine, params=(selected_id,))
            monthly_df['date'] = pd.to_datetime(monthly_df[['year', 'month']].assign(day=1))
            
            # 월별 누적 수익 계산
            monthly_df['cumulative_return'] = monthly_df['monthly_return'].cumsum()
            
            # 월별 수익률 막대 차트 생성
            st.subheader("Monthly Profit (Bar Chart)")
            bar_chart = px.bar(monthly_df, x='date', y='monthly_return', title="Monthly Profit")
            st.plotly_chart(bar_chart)
            
            # 누적 월별 수익률 선 차트 생성
            st.subheader("Cumulative Monthly Profit (Line Chart)")
            line_chart = px.line(monthly_df, x='date', y='cumulative_return', title="Cumulative Monthly Profit")
            st.plotly_chart(line_chart)