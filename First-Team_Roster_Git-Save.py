import pandas as pd
from github import Github
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
    "KIA": "KIA",
    "두산": "doosan",
    "LG": "LG",
    "삼성": "samsung",
    "SSG": "SSG",
    "NC": "NC",
    "KT": "KT",
    "롯데": "lotte",
    "한화": "hanwha",
    "키움": "kiwoom"
}

# GitHub 객체 생성
g = Github(GITHUB_TOKEN)
repo = g.get_user(REPO_OWNER).get_repo(REPO_NAME)

# 웹페이지 URL
url = 'https://www.koreabaseball.com/Player/RegisterAll.aspx'

# 웹페이지에서 테이블 읽기
tables = pd.read_html(url)

# 첫 번째 테이블 선택
df = tables[0]

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

# 어제 날짜 파일 삭제 함수
def delete_file(repo, file_path, message):
    try:
        contents = repo.get_contents(file_path)
        repo.delete_file(contents.path, message, contents.sha)
        print(f"Successfully deleted {file_path} on GitHub.")
    except Exception as e:
        print(f"Failed to delete {file_path}. The file may not exist. Exception: {e}")

# 팀별로 데이터 분리 및 GitHub에 저장
for team_name, team in team_name_map.items():
    folder_path = f"data/{team}_2024"
    
    # 어제 파일 경로와 오늘 파일 경로 설정
    old_file_name = f"{team}_players_{yesterday_date}.csv"
    new_file_name = f"{team}_players_{current_date}.csv"
    old_file_path = f"{folder_path}/{old_file_name}"
    new_file_path = f"{folder_path}/{new_file_name}"
    
    # 팀별로 데이터 필터링
    team_df = df[df['구단'] == team_name]

    # 포지션별 데이터 정리
    data = []
    for _, row in team_df.iterrows():
        for position in ['투수', '포수', '내야수', '외야수']:
            if pd.notna(row[position]):
                players = row[position].split(')')
                for player in players:
                    if player.strip():
                        player_name = player.split('(')[0].strip()
                        data.append([position, player_name])

    # 데이터 저장
    df_to_save = pd.DataFrame(data, columns=['포지션', '선수명'])
    
    # 데이터를 CSV 형식으로 변환
    csv_data = df_to_save.to_csv(index=False, encoding='utf-8')

    # 오늘 날짜 파일 생성
    try:
        repo.create_file(new_file_path, f"Add {team} players data for {current_date}", csv_data)
        print(f"Successfully created {new_file_path} on GitHub.")
    except Exception as e:
        print(f"Failed to create {new_file_path}. Exception: {e}")
    
    # 어제 날짜 파일 삭제
    delete_file(repo, old_file_path, f"Remove old file {old_file_name}")

print("Data update complete.")
