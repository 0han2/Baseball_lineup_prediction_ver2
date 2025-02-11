import streamlit as st
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import itertools
from datetime import datetime
import requests
from io import StringIO
import chardet
import os

# 폰트 파일 경로
font_path = "C:\python\퍼팩트게임_ver2\KBO Dia Gothic_TTF"

# HTML과 CSS를 사용하여 커스텀 폰트 및 스타일 적용
st.markdown(f"""
    <style>
    @font-face {{
        font-family: 'KBO 다이아고딕';
        src: url('{font_path}') format('truetype');
    }}
    * {{
        font-family: 'KBO 다이아고딕';
        font-weight: bold;
    }}
    .title {{
        text-align: center;
        color: #22326E;
    }}
    </style>
    """, unsafe_allow_html=True)

# 제목
st.markdown("<h1 class='title'>KBO 베스트 라인업 예측</h1>", unsafe_allow_html=True)

# 오늘 날짜
current_date = datetime.now().strftime('%y%m%d')

# 팀 이름과 값 매핑
teams = {
    '기아': 'KIA',
    '두산': 'doosan',
    'LG': 'LG',
    '삼성': 'samsung',
    'SSG': 'SSG',
    'NC': 'NC',
    'KT': 'KT',
    '롯데': 'lotte',
    '한화': 'hanwha',
    '키움': 'kiwoom'
}

# 팀별 배경 이미지 URL 매핑
background_images = {
    '구단을 선택하세요' : 'https://img1.daumcdn.net/thumb/R1280x0/?fname=http://t1.daumcdn.net/brunch/service/user/WkD/image/tQTODW3vLqSKlGiz-X1UvOaaKLk.png',
    '기아': 'https://tigers.co.kr/files/resource/2020/03/10/20200310132519.91a-0d4593993bc7.jpg',
    '두산': 'https://www.doosanbears.com/_next/image?url=https%3A%2F%2Fd3uesnxiude69b.cloudfront.net%2Fimgbbs%2F202007%2F20200709233136275.jpg&w=1920&q=75',
    'LG': 'https://www.lgtwins.com/images/homefield/seoul/img_facility002.jpg',
    '삼성': 'https://i.namu.wiki/i/BoTxqfBVlvAx10mDIRWJ9kqikWEYf5zfR-YJRWqEeBMbUUDHo10gMzQbtlNQMzML39xZwopk_SMFEwkgAFeK7g.webp',
    'SSG': 'https://i.namu.wiki/i/JFEtiftikjQUFOJRHrumc_l1XWIoCDVWGJyv2GFWfmN1lZj0V0awl3Ev3sH4phKBl1hvJhazgDWmHW9akponEg.webp',
    'NC': 'https://i.namu.wiki/i/v8pBY2eV08-UW0ZgRbzXf0AGLcoRe7GNSOI_sIgPSSNkm7Fv_QG6yZstHQ4kprMV6nXRamc0C1D5wBc1JRulBA.webp',
    'KT': 'https://i.namu.wiki/i/wWrWy_ic3lG9pVzxdGhTqfw4JJVyWzpjtnj_4r2T-eMcz-yeakYgVynaaNaOHTySORlHadAWJDNzGn36kei0EQ.webp',
    '롯데': 'https://i.namu.wiki/i/7gMx26HVjT0S0NHV4AGKkQx1yROJ_4DvZlVFrs5V95aEDB7KvZ9tG3Mem8L9jF1MYOh0ciMtMCuxVpg5SAQNNQ.webp',
    '한화': 'https://i.namu.wiki/i/rBPZ9C2tULpGU_kpqgxAWU1XGEjE0WwTKJEMlKNv6_1Y1qm4uF_hvGv_4AKGIVZ5Jr-YiQ6-AkxIROYd2N4oOUSjWDV5RKy_eSKOsclCC5gFPXpsH0-ctrYgrbBM-9qjcb-b7gb9EXekDp2iGlX5Sg.webp',
    '키움': 'https://i.namu.wiki/i/InYLMCVWQLjZ5K9jfllP3zKhlX7M130Udn7OF5gAovPSgd8HPfNEL0rYlgzbEr4k_VMKsxdx7YqIG2maJxjf6Q.webp'
}

# 인코딩 감지 및 데이터 로드
def detect_encoding(file_path):
    rawdata = requests.get(file_path).content
    result = chardet.detect(rawdata)
    charenc = result['encoding']
    return charenc

def load_csv(file_path):
    encoding = detect_encoding(file_path)
    response = requests.get(file_path)
    data = response.content.decode(encoding)
    df = pd.read_csv(StringIO(data))
    return df

st.write(f'데이터 업데이트: {current_date}')

# 팀 선택
selected_team = st.selectbox('팀을 선택하세요', ['구단을 선택하세요'] + list(teams.keys()))

# 선택한 팀의 배경 이미지 URL 가져오기
background_image_url = background_images.get(selected_team, '')

# 배경 이미지 설정
st.markdown(f"""
    <style>
    .stApp {{
        background: linear-gradient(rgba(255, 255, 255, 0.5), rgba(255, 255, 255, 0.5)), 
                    url('{background_image_url}');
        background-size: cover;
    }}
    </style>
    """, unsafe_allow_html=True)

if st.button("선발 라인업"):
    try:
        team = teams[selected_team]

        # GitHub URL 경로 설정
        hitter_path = f"https://raw.githubusercontent.com/0han2/Baseball_lineup_prediction_ver2/main/data/{team}_2024/{team}_hitter_{current_date}.csv"
        runner_path = f"https://raw.githubusercontent.com/0han2/Baseball_lineup_prediction_ver2/main/data/{team}_2024/{team}_runner_{current_date}.csv"
        defense_path = f"https://raw.githubusercontent.com/0han2/Baseball_lineup_prediction_ver2/main/data/{team}_2024/{team}_defense_{current_date}.csv"
        batting_order_path = f"https://raw.githubusercontent.com/0han2/Baseball_lineup_prediction_ver2/main/data/{team}_2024/{team}_batting_order_{current_date}.csv"
        players_path = f"https://raw.githubusercontent.com/0han2/Baseball_lineup_prediction_ver2/main/data/{team}_2024/{team}_players_{current_date}.csv"
        kbo_top5_path = "https://raw.githubusercontent.com/0han2/Baseball_lineup_prediction_ver2/main/KBO_top5.csv"

        # 데이터 로드
        df = load_csv(hitter_path)
        columns_to_keep = ['선수명', '팀명', '타율', '경기', '타수', '홈런', '득점', '장타율', '출루율', '득점권타율', '고의4구', '희생플라이', '희생번트']
        try:
            df = df[columns_to_keep]
        except KeyError as e:
            st.error(f"{team}의 타자 데이터에서 열을 찾을 수 없습니다: {e}")
            st.stop()

        df3 = load_csv(runner_path)
        try:
            df3 = df3[['선수명', '도루허용', '도루저지']]
        except KeyError as e:
            st.error(f"{team}의 주자 데이터에서 열을 찾을 수 없습니다: {e}")
            st.stop()
        df = pd.merge(df, df3, on='선수명', how='left')

        df5 = load_csv(defense_path)
        try:
            df5['수비이닝'] = pd.to_numeric(df5['수비이닝'], errors='coerce')
            df5['수비승리기여도'] = pd.to_numeric(df5['수비승리기여도'], errors='coerce')
            df5['평균대비수비득점기여'] = pd.to_numeric(df5['평균대비수비득점기여'], errors='coerce')
            df5['포지션'] = df5['포지션'].fillna('').astype(str)
        except KeyError as e:
            st.error(f"{team}의 수비 데이터에서 열을 찾을 수 없습니다: {e}")
            st.stop()

        def aggregate_positions(group):
            sorted_positions = group.sort_values(by='수비이닝', ascending=False)
            return ', '.join(sorted_positions['포지션'])

        df5 = df5.groupby('선수명').apply(
            lambda x: pd.Series({
                '포지션': aggregate_positions(x),
                '수비승리기여도': x['수비승리기여도'].mean(),
                '수비이닝': x['수비이닝'].sum()
            })
        ).reset_index()

        # 선수명단 로드
        players_list = load_csv(players_path)
        players_names = players_list['선수명'].unique()

        # df에 있는 선수명 필터링
        df = df[df['선수명'].isin(players_names)]

        df = pd.merge(df, df5, on='선수명', how='left')
        df = df.dropna()
        df = df[df['경기'] >= 10]
        df = df[df['타수'] >= 31]
        player_list_df = df # 끝에있는 df랑 구분하기 위해

        df2 = load_csv(batting_order_path)
        filtered_names = df['선수명'].unique()
        df2 = df2[df2['선수명'].isin(filtered_names)]
        df2['1루타'] = df2['안타'] - df2['2루타'] - df2['3루타'] - df2['홈런']
        try:
            df2 = pd.merge(df2, df[['선수명', '도루허용', '도루저지', '고의4구', '희생플라이', '희생번트', '수비승리기여도', '득점권타율']], on='선수명', how='left')
        except KeyError as e:
            st.error(f"열 병합 중 에러: {e}")
            st.stop()

        def calculate_XR(row):
            XR = (row['1루타'] * 0.5 +
                row['2루타'] * 0.72 +
                row['3루타'] * 1.04 +
                row['홈런'] * 1.44 +
                (row['사구'] + row['볼넷'] - row['고의4구']) * 0.34 +
                row['고의4구'] * 0.25 +
                row['도루허용'] * 0.18 -
                row['도루저지'] * 0.32 -
                (row['타수'] - row['안타'] - row['삼진']) * 0.09 -
                row['삼진'] * 0.098 -
                row['병살타'] * 0.37 +
                row['희생플라이'] * 0.37 +
                row['희생번트'] * 0.04)
            return XR

        def calculate_obp(row):
            hits = row['안타']
            walks = row['볼넷']
            hbp = row['사구']
            at_bats = row['타수']
            sac_flies = row['희생플라이']
            obp = (hits + walks + hbp) / (at_bats + walks + hbp + sac_flies) if (at_bats + walks + hbp + sac_flies) > 0 else 0
            return obp

        def calculate_slg(row):
            singles = row['안타'] - row['2루타'] - row['3루타'] - row['홈런']
            doubles = row['2루타']
            triples = row['3루타']
            homers = row['홈런']
            at_bats = row['타수']
            slg = (singles + 2*doubles + 3*triples + 4*homers) / at_bats if at_bats > 0 else 0
            return slg

        df2['추정득점'] = df2.apply(calculate_XR, axis=1)
        df2['출루율'] = df2.apply(calculate_obp, axis=1)
        df2['장타율'] = df2.apply(calculate_slg, axis=1)
        df2.drop(columns=['순위'], axis=1, inplace=True)
        excluded_orders = ['상위(1~2번)', '중심(3~5번)', '하위(6~9번)']
        df2 = df2[~df2['타순'].isin(excluded_orders)]
        df2['타율'] = df2['타율'].replace('-', np.nan).astype(float)
        df2 = df2[df2['타수'] >= 10]

        def calculate_weighted_average(records):
            weighted_avg = {}
            total_weight = records['타수'].sum()
            for column in records.columns:
                if column not in ['선수명', '팀명', '타순'] and pd.api.types.is_numeric_dtype(records[column]):
                    weighted_avg[column] = (records[column] * records['타수']).sum() / total_weight
            return weighted_avg

        unique_players = df2['선수명'].unique()
        all_new_records = []

        for player in unique_players:
            player_records = df2[df2['선수명'] == player]
            existing_orders = player_records['타순'].unique()
            all_orders = [f'{i}번' for i in range(1, 10)]
            missing_orders = [order for order in all_orders if order not in existing_orders]

            for order in missing_orders:
                weighted_avg = calculate_weighted_average(player_records)
                weighted_avg['타율'] = weighted_avg['안타'] / weighted_avg['타수'] if weighted_avg['타수'] != 0 else 0
                weighted_avg['선수명'] = player
                weighted_avg['팀명'] = player_records['팀명'].iloc[0]
                weighted_avg['타순'] = order
                all_new_records.append(weighted_avg)

        new_records_df = pd.DataFrame(all_new_records)
        df3 = pd.concat([df2, new_records_df], ignore_index=True)
        df3['타율'] = df3.apply(lambda row: row['안타'] / row['타수'] if row['타수'] != 0 else row['타율'], axis=1)
        df3 = df3[df3['타수'] >= 10]

        decimal_columns = ['타율', '수비승리기여도', '득점권타율', '추정득점', '출루율', '장타율']
        integer_columns = ['타수', '안타', '2루타', '3루타', '홈런', '타점', '볼넷', '사구', '삼진', '병살타', '1루타', '도루허용', '도루저지', '고의4구', '희생플라이', '희생번트']
        df3[decimal_columns] = df3[decimal_columns].round(3)
        df3[integer_columns] = df3[integer_columns].fillna(0).astype(int)
        df2 = df3

        df.replace('-', np.nan, inplace=True)
        df['장타율'] = df['장타율'].astype(float)
        df['출루율'] = df['출루율'].astype(float)
        df['타율'] = df['타율'].astype(float)

        scaler = StandardScaler()
        df[['장타율_표준화', '득점권 타율_표준화', '홈런_표준화']] = scaler.fit_transform(df[['장타율', '득점권타율', '홈런']])
        df['중심타선 합산 지표'] = df['장타율_표준화']*0.46 + df['득점권 타율_표준화']*0.33 + df['홈런_표준화']*0.56
        center_hitters_1 = df.nlargest(3, '중심타선 합산 지표')

        center_hitters_names = center_hitters_1['선수명'].values
        filtered_df2 = df2[df2['선수명'].isin(center_hitters_names)]
        filtered_df2 = filtered_df2[filtered_df2['타순'].isin(['3번', '4번', '5번'])]
        center_hitters = filtered_df2
        center_hitters_1_position = center_hitters_1[['선수명', '포지션']]
        center_hitters = pd.merge(center_hitters, center_hitters_1_position, on='선수명', how='left')
        center_per_player = filtered_df2.groupby('선수명')['타순'].apply(list).reset_index()

        df[['장타율_표준화', '출루율_표준화', '도루_표준화', '홈런_표준화']] = scaler.fit_transform(df[['장타율', '출루율', '도루허용', '홈런']])
        df['2번타자 합산 지표'] = df['장타율_표준화']*0.46 + df['출루율_표준화']*0.35 + df['도루_표준화']*0.33 + df['홈런_표준화']*0.56
        exclude_names = center_hitters['선수명'].tolist()
        filtered_df = df[~df['선수명'].isin(exclude_names)]
        center_main_positions = center_hitters['포지션'].apply(lambda x: x.split(',')[0]).unique()

        def filter_by_position(df, position, min_count, max_count, excluded_positions):
            if position in excluded_positions:
                return pd.DataFrame()
            pos_df = df[df['포지션'].str.contains(position)]
            if len(pos_df) > max_count:
                pos_df = pos_df.nlargest(max_count, '2번타자 합산 지표')
            elif len(pos_df) < min_count:
                pos_df = df[df['포지션'].str.contains(position)].nlargest(min_count, '2번타자 합산 지표')
            return pos_df

        catcher = filter_by_position(filtered_df, '포수', 1, 1, center_main_positions)
        outfielders = filter_by_position(filtered_df, '좌익수|우익수|중견수', 1, 3, center_main_positions)
        infielders = filter_by_position(filtered_df, '1루수|2루수|3루수|유격수', 1, 4, center_main_positions)
        final_candidates = pd.concat([catcher, outfielders, infielders]).drop_duplicates()
        second_hitter_1 = final_candidates.nlargest(1, '2번타자 합산 지표')

        second_hitter_names = second_hitter_1['선수명'].values
        filtered_df2 = df2[df2['선수명'].isin(second_hitter_names)]
        filtered_df2 = filtered_df2[filtered_df2['타순'].isin(['1번'])]
        second_hitter = filtered_df2
        second_hitter_1_position = second_hitter_1[['선수명', '포지션']]
        second_hitter = pd.merge(second_hitter, second_hitter_1_position, on='선수명', how='left')

        df[['출루율_표준화', '도루_표준화']] = scaler.fit_transform(df[['출루율', '도루허용']])
        df['1번타자 합산 지표'] = df['출루율_표준화']*0.35 + df['도루_표준화']*0.33
        exclude_names = center_hitters['선수명'].tolist() + second_hitter_1['선수명'].tolist()
        filtered_df = df[~df['선수명'].isin(exclude_names)]
        center_main_positions = center_hitters['포지션'].apply(lambda x: x.split(',')[0]).unique()
        second_hitter_main_positions = second_hitter_1['포지션'].apply(lambda x: x.split(',')[0]).unique()
        excluded_positions = list(center_main_positions) + list(second_hitter_main_positions)

        catcher = filter_by_position(filtered_df, '포수', 1, 1, excluded_positions)
        outfielders = filter_by_position(filtered_df, '좌익수|우익수|중견수', 1, 3, excluded_positions)
        infielders = filter_by_position(filtered_df, '1루수|2루수|3루수|유격수', 1, 4, excluded_positions)
        final_candidates = pd.concat([catcher, outfielders, infielders]).drop_duplicates()
        first_hitter_1 = final_candidates.nlargest(1, '1번타자 합산 지표')

        first_hitter_names = first_hitter_1['선수명'].values
        filtered_df2 = df2[df2['선수명'].isin(first_hitter_names)]
        filtered_df2 = filtered_df2[filtered_df2['타순'].isin(['1번'])]
        first_hitter = filtered_df2
        first_hitter_1_position = first_hitter_1[['선수명', '포지션']]
        first_hitter = pd.merge(first_hitter, first_hitter_1_position, on='선수명', how='left')

        scaler = StandardScaler()
        df[['출루율_표준화', '수비_표준화']] = scaler.fit_transform(df[['출루율', '수비승리기여도']])
        df['하위타선 합산 지표'] = df['출루율_표준화']*0.35 + df['수비_표준화']*0.10
        exclude_names = center_hitters['선수명'].tolist() + second_hitter_1['선수명'].tolist() + first_hitter_1['선수명'].tolist()
        filtered_df = df[~df['선수명'].isin(exclude_names)]
        center_main_positions = center_hitters['포지션'].apply(lambda x: x.split(',')[0]).unique()
        second_hitter_main_positions = second_hitter_1['포지션'].apply(lambda x: x.split(',')[0]).unique()
        first_hitter_main_positions = first_hitter_1['포지션'].apply(lambda x: x.split(',')[0]).unique()
        excluded_positions = list(center_main_positions) + list(second_hitter_main_positions) + list(first_hitter_main_positions)

        def filter_by_position(df, position, excluded_positions):
            if position in excluded_positions:
                return pd.DataFrame()
            return df[df['포지션'].str.contains(position)]

        catchers = filter_by_position(filtered_df, '포수', excluded_positions)
        outfielders = filter_by_position(filtered_df, '좌익수|우익수|중견수', excluded_positions)
        infielders = filter_by_position(filtered_df, '1루수|2루수|3루수|유격수', excluded_positions)
        bottom_candidates = pd.concat([catchers, outfielders, infielders]).drop_duplicates()

        if not any('포수' in pos for pos in center_main_positions) and \
        not any('포수' in pos for pos in second_hitter_main_positions) and \
        not any('포수' in pos for pos in first_hitter_main_positions):
            if '포수' not in bottom_candidates['포지션'].values:
                bottom_candidates = bottom_candidates.iloc[:-1]
                catcher = filtered_df[filtered_df['포지션'].str.contains('포수')].nlargest(1, '하위타선 합산 지표')
                bottom_candidates = pd.concat([bottom_candidates, catcher])

        if bottom_candidates['포지션'].str.contains('포수').sum() > 1:
            best_catcher = bottom_candidates[bottom_candidates['포지션'].str.contains('포수')].nlargest(1, '하위타선 합산 지표')
            bottom_candidates = bottom_candidates[~bottom_candidates['포지션'].str.contains('포수')].nlargest(3, '하위타선 합산 지표')
            bottom_candidates = pd.concat([bottom_candidates, best_catcher])

        bottom_hitters_1 = bottom_candidates.nlargest(4, '하위타선 합산 지표').drop_duplicates()
        selected_positions = set(center_main_positions) | set(second_hitter_main_positions) | set(first_hitter_main_positions)
        missing_positions = {'포수', '좌익수', '우익수', '중견수', '1루수', '2루수', '3루수', '유격수'} - selected_positions

        if missing_positions:
            for position in missing_positions:
                if not any(position in pos for pos in bottom_hitters_1['포지션']):
                    lowest_score_player = bottom_hitters_1.nsmallest(1, '하위타선 합산 지표')
                    bottom_hitters_1 = bottom_hitters_1.drop(lowest_score_player.index)
                    position_candidate = filtered_df[filtered_df['포지션'].str.contains(position)].nlargest(1, '타수')
                    bottom_hitters_1 = pd.concat([bottom_hitters_1, position_candidate])

        bottom_hitters_1 = bottom_hitters_1.nlargest(4, '하위타선 합산 지표').drop_duplicates()

        bottom_hitters_names = bottom_hitters_1['선수명'].values
        filtered_df2 = df2[df2['선수명'].isin(bottom_hitters_names)]
        filtered_df2 = filtered_df2[filtered_df2['타순'].isin(['6번', '7번', '8번', '9번'])]
        bottom_hitters = filtered_df2
        bottom_hitters_1_position = bottom_hitters_1[['선수명', '포지션']]
        bottom_hitters = pd.merge(bottom_hitters, bottom_hitters_1_position, on='선수명', how='left')
        bottom_per_player = filtered_df2.groupby('선수명')['타순'].apply(list).reset_index()

        df = pd.concat([first_hitter, second_hitter], ignore_index=True)

        players = center_per_player.set_index('선수명')['타순'].to_dict()
        possible_orders = list(itertools.product(*players.values()))
        valid_orders = [order for order in possible_orders if len(set(order)) == len(players)]
        combinations = []
        for order in valid_orders:
            order_dict = {order[i]: player for i, player in enumerate(players.keys())}
            combinations.append(order_dict)

        results = []
        for comb in combinations:
            filtered_center_hitters = center_hitters[center_hitters.apply(lambda row: row['타순'] in comb and comb[row['타순']] == row['선수명'], axis=1)]
            if len(filtered_center_hitters) == len(players):
                results.append(filtered_center_hitters)

        center_dfs = []
        for i, result in enumerate(results):
            center_df = result.reset_index(drop=True)
            center_dfs.append(center_df)
            globals()[f'center_{i+1}'] = center_df

        concat_dfs = []
        for i, center_df in enumerate(center_dfs):
            concat_df = pd.concat([df, center_df], ignore_index=True)
            concat_dfs.append(concat_df)
            globals()[f'df_{i+1}'] = concat_df

        players = bottom_per_player.set_index('선수명')['타순'].to_dict()
        possible_orders = list(itertools.product(*players.values()))
        valid_orders = [order for order in possible_orders if len(set(order)) == len(players)]
        combinations = []
        for order in valid_orders:
            order_dict = {order[i]: player for i, player in enumerate(players.keys())}
            combinations.append(order_dict)

        results = []
        for comb in combinations:
            filtered_bottom_hitters = bottom_hitters[bottom_hitters.apply(lambda row: row['타순'] in comb and comb[row['타순']] == row['선수명'], axis=1)]
            if len(filtered_bottom_hitters) == len(players):
                results.append(filtered_bottom_hitters)

        bottom_dfs = []
        for i, result in enumerate(results):
            bottom_df = result.reset_index(drop=True)
            bottom_dfs.append(bottom_df)
            globals()[f'bottom_{i+1}'] = bottom_df

        final_dfs = []
        count = 1
        for i in range(len(concat_dfs)):
            for j in range(len(bottom_dfs)):
                final_df = pd.concat([concat_dfs[i], bottom_dfs[j]], ignore_index=True)
                final_dfs.append(final_df)
                globals()[f'final_df_{count}'] = final_df
                count += 1

        for i in range(1, len(final_dfs) + 1):
            globals()[f'df_{i}'] = globals().pop(f'final_df_{i}')

        # 모델 생성 및 예측
        df = load_csv(kbo_top5_path)
        df = df.drop(columns=['선수명', '년도'])
        df = df[df['타율'] != '-']
        df.replace('-', 0, inplace=True)

        # '수비승리기여도' 컬럼이 존재하지 않으면 생성
        if '수비승리기여도' not in df.columns:
            df['수비승리기여도'] = 0  # 기본값 설정

        features = ['출루율', '장타율', '홈런', '수비승리기여도', '득점권타율', '도루허용']
        target = '추정득점'

        X = df[features]
        y = df[target]

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        model = RandomForestRegressor()
        model.fit(X_train, y_train)

        predicted_scores = {}

        for i in range(1, 145):
            lineup_df = globals()[f'df_{i}']
            lineup_features = lineup_df[features]
            predicted_score = model.predict(lineup_features)
            total_predicted_score = predicted_score.mean()
            predicted_scores[f'df_{i}'] = total_predicted_score

        best_lineup = max(predicted_scores, key=predicted_scores.get)
        best_score = round(predicted_scores[best_lineup],2)

        best_lineup_df = globals()[best_lineup].copy()
        best_lineup_df.index = range(1, len(best_lineup_df) + 1)

        # 필요한 컬럼만 선택
        selected_columns = ['선수명', '팀명', '타율', '타수', '출루율', '장타율', '득점권타율', '홈런', '수비승리기여도', '도루허용', '포지션']
        best_lineup_df = best_lineup_df[selected_columns]

        # best_lineup_df와 player_list_df를 병합하여 통계를 업데이트
        best_lineup_df = best_lineup_df[['선수명', '팀명']].merge(
        player_list_df[selected_columns],
        on=['선수명', '팀명'],
        how='left'
        )

        # 도루허용 도루개수로 변경
        best_lineup_df = best_lineup_df.rename(columns={'도루허용': '도루개수'})

        # # 포지션에서 첫 번째 값만 남기기 (공백 제거)
        # best_lineup_df['포지션'] = best_lineup_df['포지션'].apply(lambda x: x.split(',')[0].strip() if ',' in x else x.strip())

        # 소수점 3자리까지 표현
        decimal_columns = ['타율', '출루율', '득점권타율', '장타율', '수비승리기여도']
        best_lineup_df[decimal_columns] = best_lineup_df[decimal_columns].applymap(lambda x: f"{x:.3f}")

        # 인덱스를 0이 아닌 1부터 시작하도록 재설정
        best_lineup_df.index = best_lineup_df.index + 1

        # 베스트 라인업 출력
        st.subheader(f'{selected_team} 베스트 라인업')
        st.dataframe(best_lineup_df)
        st.write(f'예상 추정 득점: {best_score}')
    except Exception as e:
        st.error(f"Failed to load data: {e}")
