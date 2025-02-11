import selenium
from selenium import webdriver as wd
from selenium.webdriver.common.by import By
import time
import pandas as pd
import os
from github import Github
import base64
from datetime import datetime, timedelta

# GitHub Personal Access Token 및 저장소 정보 설정
GITHUB_TOKEN = '****'
REPO_OWNER = '****'
REPO_NAME = '****'

# 현재 날짜와 어제 날짜를 YYMMDD 형식으로 가져오기
current_date = datetime.now().strftime('%y%m%d')
yesterday_date = (datetime.now() - timedelta(1)).strftime('%y%m%d')

# 폴더와 파일명을 팀 코드에 따라 매핑
team_name_map = {
    "HT": "KIA",
    "OB": "doosan",
    "LG": "LG",
    "SS": "samsung",
    "SK": "SSG",
    "NC": "NC",
    "KT": "KT",
    "LT": "lotte",
    "HH": "hanwha",
    "WO": "kiwoom"
}

teams = ["SS", "SK", "NC", "KT", "LT", "HH", "WO"] # "HT", "OB", "LG", 

# 1 Chrome 열기
driver = wd.Chrome()

teps = ['HitterBasic/Basic1', 'HitterBasic/Basic2', 'HitterBasic/Detail1', 'Runner/Basic']
Hitter_years = [43]
Runner_years = [24]
batting_order = range(2,14)

# 열 이름 사전
column_translations = {
    # 타자기록
    '2B': '2루타', '3B': '3루타', 'AB': '타수', 'AO': '뜬공', 'AVG': '타율',
    'BB': '볼넷', 'BB/K': '볼넷/삼진', 'CS': '도루실패', 'E': '실책', 'G': '경기',
    'GDP': '병살타', 'GO': '땅볼', 'GO/AO': '땅볼/뜬공', 'GPA': '(1.8x출루율+장타율)/4',
    'GW RBI': '결승타', 'H': '안타', 'HBP': '사구', 'HR': '홈런', 'IBB': '고의4구',
    'ISOP': '순수장타율', 'MH': '멀티히트', 'OBP': '출루율', 'OPS': '출루율+장타율',
    'P/PA': '투구수/타석', 'PA': '타석', 'PH-BA': '대타타율', 'R': '득점', 'RBI': '타점',
    'RISP': '득점권타율', 'SAC': '희생번트', 'SB': '도루', 'SF': '희생플라이', 'SLG': '장타율',
    'SO': '삼진', 'TB': '루타', 'XBH': '장타', 'XR': '추정득점',
    # 수비기록
    'A': '어시스트', 'CS': '도루저지', 'CS%': '도루저지율', 'DP': '병살', 'FPCT': '수비율',
    'GS': '선발경기', 'PB': '포일', 'PKO': '견제사', 'PO': '풋아웃', 'POS': '포지션',
    'SB': '도루허용', 'IP': '수비이닝',
    # 주루기록
    'OOB': '주루사', 'SBA': '도루시도', 'SB%': '도루성공률'
}

# 타순 매핑
order_mapping = {
    2: '1번', 3: '2번', 4: '3번', 5: '4번', 6: '5번',
    7: '6번', 8: '7번', 9: '8번', 10: '9번',
    11: '상위(1~2번)', 12: '중심(3~5번)', 13: '하위(6~9번)'
}

# GitHub 객체 생성
g = Github(GITHUB_TOKEN)
repo = g.get_user(REPO_OWNER).get_repo(REPO_NAME)

# GitHub에 파일 업로드 함수
def upload_to_github(repo, file_path, content, message):
    try:
        # 파일이 이미 존재하는지 확인
        contents = repo.get_contents(file_path)
        # 파일이 존재하면 업데이트
        repo.update_file(contents.path, message, content, contents.sha)
        print(f"Successfully updated {file_path} on GitHub.")
    except Exception as e:
        # 파일이 존재하지 않으면 새로 생성
        repo.create_file(file_path, message, content)
        print(f"Successfully created {file_path} on GitHub. Exception: {e}")

# GitHub에서 파일 가져오기 함수
def download_from_github(repo, file_path):
    try:
        contents = repo.get_contents(file_path)
        file_content = base64.b64decode(contents.content).decode('utf-8')
        return pd.read_csv(pd.compat.StringIO(file_content), encoding='cp949')
    except Exception as e:
        print(f"Failed to download {file_path} from GitHub. Exception: {e}")
        return None

# 어제 날짜 파일 삭제 함수
def delete_file(repo, file_path, message):
    try:
        contents = repo.get_contents(file_path)
        repo.delete_file(contents.path, message, contents.sha)
        print(f"Successfully deleted {file_path} on GitHub.")
    except Exception as e:
        print(f"Failed to delete {file_path}. The file may not exist or another error occurred. Exception: {e}")

for team in teams:
    if team in team_name_map:
        file_name = team_name_map[team]
        folder_path = f"data/{file_name}_2024"
    
        # 빈 결과 테이블
        result_dfs = {year: [] for year in range(2024, 2024 + len(Hitter_years))}

        # 사이트 접속
        for tep in teps[:2]:
            url = f'https://www.koreabaseball.com/Record/Player/{tep}.aspx'
            driver.get(url)
            time.sleep(3)

            # 타자 기록 접속
            for year_index, year in enumerate(Hitter_years):
                # 연도 선택
                Season_selector = f'#cphContents_cphContents_cphContents_ddlSeason_ddlSeason > option:nth-child({year})'
                driver.find_element(By.CSS_SELECTOR, Season_selector).click()
                time.sleep(3)

                # 팀 정보 선택
                team_option = driver.find_element(By.CSS_SELECTOR, f"option[value='{team}']")
                team_option.click()
                time.sleep(3)

                # 1페이지로 돌아가기
                first_page_button = driver.find_element(By.CSS_SELECTOR, f'#cphContents_cphContents_cphContents_ucPager_btnNo1')
                first_page_button.click()
                time.sleep(3)

                # 페이지 반복하여 데이터 가져오기 (1페이지와 2페이지)
                for page in range(1, 3):
                    if page > 1:
                        try:
                            next_page_button = driver.find_element(By.CSS_SELECTOR, f'#cphContents_cphContents_cphContents_ucPager_btnNo{page}')
                            next_page_button.click()
                            time.sleep(3)
                        except:
                            break  # 페이지 버튼이 없는 경우 루프를 종료

                    # 결과 테이블 가져오기
                    result_table = driver.find_element(By.CSS_SELECTOR, '#cphContents_cphContents_cphContents_udpContent > div.record_result')
                    table_html = result_table.get_attribute('outerHTML')

                    # DataFrame으로 변환하여 리스트에 추가
                    df = pd.read_html(table_html, encoding='utf-8')[0]

                    # HitterBasic/Basic2일 경우에만 불필요한 열 제거
                    if tep == 'HitterBasic/Basic2':
                        df = df.drop(columns=['순위', '선수명', '팀명', 'AVG'])

                    # 결과를 리스트에 추가
                    result_dfs[2024 + year_index].append(df)

                # 연도가 바뀔 때마다 다시 첫 페이지로 돌아가기
                driver.get(url)
                time.sleep(3)
                driver.find_element(By.CSS_SELECTOR, Season_selector).click()
                time.sleep(3)

        # 어제 파일 경로와 오늘 파일 경로 설정
        old_file_name = f"{file_name}_hitter_{yesterday_date}.csv"
        new_file_name = f"{file_name}_hitter_{current_date}.csv"
        old_file_path = f"{folder_path}/{old_file_name}"
        new_file_path = f"{folder_path}/{new_file_name}"
        
        # 오늘 파일이 존재하는지 확인
        try:
            repo.get_contents(new_file_path)
            today_file_exists = True
            print(f"{new_file_path} already exists.")
        except:
            today_file_exists = False
            print(f"{new_file_path} does not exist.")

        # 각 연도별로 DataFrame을 CSV 파일로 저장
        for year, dfs in result_dfs.items():
            # dfs 개수에 따라 다르게 저장
            if len(dfs) >= 4:  # HitterBasic/Basic2의 데이터가 존재하는 경우
                df1 = dfs[0]  # HitterBasic/Basic1의 page1 결과
                df2 = dfs[1]  # HitterBasic/Basic1의 page2 결과
                df3 = dfs[2]  # HitterBasic/Basic2의 page1 결과
                df4 = dfs[3]  # HitterBasic/Basic2의 page2 결과
                Basic1_df = pd.concat([df1, df2], axis=0)
                Basic2_df = pd.concat([df3, df4], axis=0)
                final_df = pd.concat([Basic1_df, Basic2_df], axis=1)
            else:
                df1 = dfs[0]  # HitterBasic/Basic1의 page1 결과
                df2 = dfs[1]  # HitterBasic/Basic1의 page2 결과
                final_df = pd.concat([df1, df2], axis=1)

            # 열 이름을 한국어로 변환
            final_df.rename(columns=column_translations, inplace=True)

            # 데이터프레임 전체를 문자열로 변환하여 CSV 파일로 저장
            final_df = final_df.astype(str)
            csv_data = final_df.to_csv(index=False, encoding='utf-8')

            # 오늘 날짜 파일 생성
            try:
                repo.create_file(new_file_path, f"Add {file_name} hitter data for {current_date}", csv_data)
                print(f"Successfully created {new_file_path} on GitHub.")
            except Exception as e:
                print(f"Failed to create {new_file_path}. Exception: {e}")
            
            # 어제 날짜 파일 삭제
            delete_file(repo, old_file_path, f"Remove old file {old_file_name}")

        # 빈 결과 테이블
        result_dfs = {year: [] for year in range(2024, 2024 + len(Hitter_years))}

        # 사이트 접속
        for tep in teps[2:3]:
            url = f'https://www.koreabaseball.com/Record/Player/{tep}.aspx'
            driver.get(url)
            time.sleep(3)

            # 타자 기록 접속
            for year_index, year in enumerate(Hitter_years):
                # 연도 선택
                Season_selector = f'#cphContents_cphContents_cphContents_ddlSeason_ddlSeason > option:nth-child({year})'
                driver.find_element(By.CSS_SELECTOR, Season_selector).click()
                time.sleep(3)

                # 팀 정보 선택
                team_option = driver.find_element(By.CSS_SELECTOR, f"option[value='{team}']")
                team_option.click()
                time.sleep(3)

                # 1페이지로 돌아가기
                first_page_button = driver.find_element(By.CSS_SELECTOR, f'#cphContents_cphContents_cphContents_ucPager_btnNo1')
                first_page_button.click()
                time.sleep(3)

                # 페이지 반복하여 데이터 가져오기 (1페이지와 2페이지)
                for page in range(1, 3):
                    if page > 1:
                        try:
                            next_page_button = driver.find_element(By.CSS_SELECTOR, f'#cphContents_cphContents_cphContents_ucPager_btnNo{page}')
                            next_page_button.click()
                            time.sleep(3)
                        except:
                            break  # 페이지 버튼이 없는 경우 루프를 종료

                    # 결과 테이블 가져오기
                    result_table = driver.find_element(By.CSS_SELECTOR, '#cphContents_cphContents_cphContents_udpContent > div.record_result')
                    table_html = result_table.get_attribute('outerHTML')

                    # DataFrame으로 변환하여 리스트에 추가
                    df = pd.read_html(table_html, encoding='utf-8')[0]

                    # 결과를 리스트에 추가
                    result_dfs[2024 + year_index].append(df)

                # 연도가 바뀔 때마다 다시 첫 페이지로 돌아가기
                driver.get(url)
                time.sleep(3)
                driver.find_element(By.CSS_SELECTOR, Season_selector).click()
                time.sleep(3)

        # 어제 파일 경로와 오늘 파일 경로 설정
        old_file_name = f"{file_name}_hitter_detail_{yesterday_date}.csv"
        new_file_name = f"{file_name}_hitter_detail_{current_date}.csv"
        old_file_path = f"{folder_path}/{old_file_name}"
        new_file_path = f"{folder_path}/{new_file_name}"
        
        # 오늘 파일이 존재하는지 확인
        try:
            repo.get_contents(new_file_path)
            today_file_exists = True
            print(f"{new_file_path} already exists.")
        except:
            today_file_exists = False
            print(f"{new_file_path} does not exist.")

        # 각 연도별로 DataFrame을 CSV 파일로 저장
        for year, dfs in result_dfs.items():
            # dfs 개수에 따라 다르게 저장
            if len(dfs) > 1:
                df1 = dfs[0]  # HitterBasic/Detail1의 page1 결과
                df2 = dfs[1]  # HitterBasic/Detail1c의 page2 결과
                final_df = pd.concat([df1, df2], axis=0)
            else:
                df1 = dfs[0]  # Runner/Basic의 page1 결과
                final_df = df1

            # 열 이름을 한국어로 변환
            final_df.rename(columns=column_translations, inplace=True)

            # 데이터프레임 전체를 문자열로 변환하여 CSV 파일로 저장
            final_df = final_df.astype(str)
            csv_data = final_df.to_csv(index=False, encoding='utf-8')

            # 오늘 날짜 파일 생성
            try:
                repo.create_file(new_file_path, f"Add {file_name} hitter_detail data for {current_date}", csv_data)
                print(f"Successfully created {new_file_path} on GitHub.")
            except Exception as e:
                print(f"Failed to create {new_file_path}. Exception: {e}")
            
            # 어제 날짜 파일 삭제
            delete_file(repo, old_file_path, f"Remove old file {old_file_name}")

        # 빈 결과 테이블
        result_dfs = {year: [] for year in range(2024, 2024 + len(Hitter_years))}

        # 사이트 접속
        for tep in teps[:1]:
            url = f'https://www.koreabaseball.com/Record/Player/{tep}.aspx'
            driver.get(url)
            time.sleep(3)

            # 타자 기록 접속
            for year_index, year in enumerate(Hitter_years):
                # 연도 선택
                Season_selector = f'#cphContents_cphContents_cphContents_ddlSeason_ddlSeason > option:nth-child({year})'
                driver.find_element(By.CSS_SELECTOR, Season_selector).click()
                time.sleep(3)

                # 팀 정보 선택
                team_option = driver.find_element(By.CSS_SELECTOR, f"option[value='{team}']")
                team_option.click()
                time.sleep(3)

                # 타순별 선택
                Situation_selector = '#cphContents_cphContents_cphContents_ddlSituation_ddlSituation > option:nth-child(14)'
                driver.find_element(By.CSS_SELECTOR, Situation_selector).click()
                time.sleep(3)

                for order in batting_order:
                    # 타순 선택
                    Batting_order_selector = f'#cphContents_cphContents_cphContents_ddlSituationDetail_ddlSituationDetail > option:nth-child({order})'
                    driver.find_element(By.CSS_SELECTOR, Batting_order_selector).click()
                    time.sleep(3)

                    # 1페이지로 돌아가기
                    first_page_button = driver.find_element(By.CSS_SELECTOR, f'#cphContents_cphContents_cphContents_ucPager_btnNo1')
                    first_page_button.click()
                    time.sleep(3)

                    # 페이지 반복하여 데이터 가져오기 (1페이지와 2페이지)
                    for page in range(1, 3):
                        if page > 1:
                            try:
                                next_page_button = driver.find_element(By.CSS_SELECTOR, f'#cphContents_cphContents_cphContents_ucPager_btnNo{page}')
                                next_page_button.click()
                                time.sleep(3)
                            except:
                                break  # 페이지 버튼이 없는 경우 루프를 종료

                        # 결과 테이블 가져오기
                        result_table = driver.find_element(By.CSS_SELECTOR, '#cphContents_cphContents_cphContents_udpContent > div.record_result')
                        table_html = result_table.get_attribute('outerHTML')

                        # DataFrame으로 변환하여 리스트에 추가
                        df = pd.read_html(table_html, encoding='utf-8')[0]

                        # 타순 열 추가
                        df['타순'] = order_mapping[order]

                        # 결과를 리스트에 추가
                        result_dfs[2024 + year_index].append(df)

                # 연도가 바뀔 때마다 다시 첫 페이지로 돌아가기
                driver.get(url)
                time.sleep(3)
                driver.find_element(By.CSS_SELECTOR, Season_selector).click()
                time.sleep(3)

        # 어제 파일 경로와 오늘 파일 경로 설정
        old_file_name = f"{file_name}_batting_order_{yesterday_date}.csv"
        new_file_name = f"{file_name}_batting_order_{current_date}.csv"
        old_file_path = f"{folder_path}/{old_file_name}"
        new_file_path = f"{folder_path}/{new_file_name}"
        
        # 오늘 파일이 존재하는지 확인
        try:
            repo.get_contents(new_file_path)
            today_file_exists = True
            print(f"{new_file_path} already exists.")
        except:
            today_file_exists = False
            print(f"{new_file_path} does not exist.")

        # 결과 데이터프레임을 연도별로 합쳐서 각각의 CSV 파일로 저장
        for year, dfs in result_dfs.items():
            if dfs:  # dfs 리스트가 비어있지 않을 때만 처리
                combined_df = pd.concat(dfs, axis=0)
                combined_df.rename(columns=column_translations, inplace=True)
                combined_df = combined_df.astype(str)

                # 데이터프레임 전체를 문자열로 변환하여 CSV 파일로 저장
                final_df = combined_df.astype(str)
                csv_data = final_df.to_csv(index=False, encoding='utf-8')

                # 오늘 날짜 파일 생성
                try:
                    repo.create_file(new_file_path, f"Add {file_name} hitter data for {current_date}", csv_data)
                    print(f"Successfully created {new_file_path} on GitHub.")
                except Exception as e:
                    print(f"Failed to create {new_file_path}. Exception: {e}")
                
                # 어제 날짜 파일 삭제
                delete_file(repo, old_file_path, f"Remove old file {old_file_name}")

        # 빈 결과 테이블
        result_dfs = {year: [] for year in range(2024, 2024 + len(Hitter_years))}

        # 사이트 접속
        for tep in teps[3:4]:
            url = f'https://www.koreabaseball.com/Record/Player/{tep}.aspx'
            driver.get(url)
            time.sleep(3)

            # 주루 기록 접속
            for year_index, year in enumerate(Runner_years):
                # 연도 선택
                Season_selector = f'#cphContents_cphContents_cphContents_ddlSeason_ddlSeason > option:nth-child({year})'
                driver.find_element(By.CSS_SELECTOR, Season_selector).click()
                time.sleep(3)

                # 팀 정보 선택
                team_option = driver.find_element(By.CSS_SELECTOR, f"option[value='{team}']")
                team_option.click()
                time.sleep(3)

                # 1페이지로 돌아가기
                first_page_button = driver.find_element(By.CSS_SELECTOR, f'#cphContents_cphContents_cphContents_ucPager_btnNo1')
                first_page_button.click()
                time.sleep(3)

                # 페이지 반복하여 데이터 가져오기 (1페이지~ 4페이지)
                for page in range(1, 3):
                    if page > 1:
                        try:
                            next_page_button = driver.find_element(By.CSS_SELECTOR, f'#cphContents_cphContents_cphContents_ucPager_btnNo{page}')
                            next_page_button.click()
                            time.sleep(3)
                        except:
                            break  # 페이지 버튼이 없는 경우 루프를 종료

                    # 결과 테이블 가져오기
                    result_table = driver.find_element(By.CSS_SELECTOR, '#cphContents_cphContents_cphContents_udpContent > div.record_result')
                    table_html = result_table.get_attribute('outerHTML')

                    # DataFrame으로 변환하여 리스트에 추가
                    df = pd.read_html(table_html, encoding='utf-8')[0]

                    # 결과를 리스트에 추가
                    result_dfs[2024 + year_index].append(df)

                # 연도가 바뀔 때마다 다시 첫 페이지로 돌아가기
                driver.get(url)
                time.sleep(3)
                driver.find_element(By.CSS_SELECTOR, Season_selector).click()
                time.sleep(3)

        # 어제 파일 경로와 오늘 파일 경로 설정
        old_file_name = f"{file_name}_runner_{yesterday_date}.csv"
        new_file_name = f"{file_name}_runner_{current_date}.csv"
        old_file_path = f"{folder_path}/{old_file_name}"
        new_file_path = f"{folder_path}/{new_file_name}"
        
        # 오늘 파일이 존재하는지 확인
        try:
            repo.get_contents(new_file_path)
            today_file_exists = True
            print(f"{new_file_path} already exists.")
        except:
            today_file_exists = False
            print(f"{new_file_path} does not exist.")

        # 각 연도별로 DataFrame을 CSV 파일로 저장
        for year, dfs in result_dfs.items():
            # dfs 개수에 따라 다르게 저장
            if len(dfs) > 1:
                df1 = dfs[0]  # Runner/Basic의 page1 결과
                df2 = dfs[1]  # Runner/Basic의 page2 결과
                final_df = pd.concat([df1, df2], axis=0)
            else:
                df1 = dfs[0]  # Runner/Basic의 page1 결과
                final_df = df1

            # 열 이름을 한국어로 변환
            final_df.rename(columns=column_translations, inplace=True)

            # 데이터프레임 전체를 문자열로 변환하여 CSV 파일로 저장
            final_df = final_df.astype(str)
            csv_data = final_df.to_csv(index=False, encoding='utf-8')

            # 오늘 날짜 파일 생성
            try:
                repo.create_file(new_file_path, f"Add {file_name} runner data for {current_date}", csv_data)
                print(f"Successfully created {new_file_path} on GitHub.")
            except Exception as e:
                print(f"Failed to create {new_file_path}. Exception: {e}")
            
            # 어제 날짜 파일 삭제
            delete_file(repo, old_file_path, f"Remove old file {old_file_name}")

# 드라이버 종료
driver.quit()

# 팀 이름과 te 파라미터 값 매핑
teams = {
    '기아' : (2002, 'KIA'),
    '두산' : (6002, 'doosan'),
    'LG' : (5002, 'LG'),
    '삼성' : (1001, 'samsung'),
    'SSG' : (9002, 'SSG'),
    'NC' : (11001, 'NC'),
    'KT' : (12001, 'KT'),
    '롯데' : (3001, 'lotte'),
    '한화' : (7002, 'hanwha'),
    '키움' : (10001, 'kiwoom')
}

# 각 팀별로 데이터 수집 및 저장
for team_folder_name, (te_value, team) in teams.items():  # items() 메서드 사용
    folder_path = f"data/{team}_2024"

    # 2024 defense detail 수집 - 스탯티즈 
    url = f"https://statiz.sporki.com/stats/?m=main&m2=fielding&m3=default&so=WAAwithPOS&ob=DESC&year=2024&sy=&ey=&te={te_value}&po=&lt=10100&reg=A&pe=&ds=&de=&we=&hr=&ha=&ct=&st=&vp=&bo=&pt=&pp=&ii=&vc=&um=&oo=&rr=&sc=&bc=&ba=&li=&as=&ae=&pl=&gc=&lr=&pr=1000&ph=&hs=&us=&na=&ls=1&sf1=G&sk1=&sv1=&sf2=G&sk2=&sv2="
    
    # 웹페이지에서 테이블 읽기
    dfs = pd.read_html(url)
    
    # 첫 번째 테이블을 데이터프레임으로 선택
    df = dfs[0]
    
    # 첫 번째 컬럼 행 제거
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.droplevel(0)

    # 컬럼명 한글이름으로 바꾸기
    columns_to_keep = ['Name', 'Team', 'G', 'IP', 'WAAwithPOS', 'RAAwithPOS']
    df_detail = df[columns_to_keep].rename(columns={'Name' : '선수명', 'Team' : '포지션', 'G' : '경기수', 'IP' : '수비이닝', 'WAAwithPOS' : '수비승리기여도', 'RAAwithPOS' : '평균대비수비득점기여'})

    # 포지션 컬럼에서 앞 세 글자 제외
    df_detail['포지션'] = df_detail['포지션'].str[3:]

    position_mapping = {
        '1B': '1루수',    '2B': '2루수',    '3B': '3루수',    'SS': '유격수',
        'C': '포수',    'RF': '우익수',    'CF': '중견수',    'LF': '좌익수', 'P' : '투수'
    }

    # 포지션 컬럼 값 변환
    df_detail['포지션'] = df_detail['포지션'].map(position_mapping)

    # 팀 컬럼 추가
    df_detail['팀명'] = f'{team}'
    df_detail['순위'] = df_detail['수비승리기여도'].rank(ascending=False, method='min').fillna(len(df_detail)+1).astype(int)

    # 컬럼 배치 변경
    df_detail = df_detail[['순위', '선수명', '팀명', '포지션', '경기수', '수비이닝', '수비승리기여도', '평균대비수비득점기여']]

    # 어제 파일 경로와 오늘 파일 경로 설정
    old_file_name = f"{team}_defense_{yesterday_date}.csv"
    new_file_name = f"{team}_defense_{current_date}.csv"
    old_file_path = f"{folder_path}/{old_file_name}"
    new_file_path = f"{folder_path}/{new_file_name}"
        
    # 오늘 파일이 존재하는지 확인
    try:
        repo.get_contents(new_file_path)
        today_file_exists = True
        print(f"{new_file_path} already exists.")
    except:
        today_file_exists = False
        print(f"{new_file_path} does not exist.")

    # 데이터프레임 전체를 문자열로 변환하여 CSV 파일로 저장
    df_detail = df_detail.astype(str)
    csv_data = df_detail.to_csv(index=False, encoding='utf-8')

    # 파일 경로 설정
    data_name = f"{team}_defense_{current_date}.csv"
    file_path = f"{folder_path}/{data_name}"

    # 오늘 날짜 파일 생성
    try:
        repo.create_file(new_file_path, f"Add {team} defense data for {current_date}", csv_data)
        print(f"Successfully created {new_file_path} on GitHub.")
    except Exception as e:
        print(f"Failed to create {new_file_path}. Exception: {e}")
                
    # 어제 날짜 파일 삭제
    delete_file(repo, old_file_path, f"Remove old file {old_file_name}")
