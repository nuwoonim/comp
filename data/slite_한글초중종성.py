# split_csv_final.py
import os
import csv
from collections import defaultdict

# 입력/출력 경로
INPUT_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'com_sum.CSV')
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data_final')

# 인코딩
ENCODING = 'utf-8'

# 14개 초성 그룹 매핑 (초성 코드 0~18)
CHOSEONG_TO_GROUP = {
    0: '가',   # ㄱ
    1: '가',   # ㄲ
    2: '나',   # ㄴ
    3: '다',   # ㄷ
    4: '다',   # ㄸ
    5: '라',   # ㄹ
    6: '마',   # ㅁ
    7: '바',   # ㅂ
    8: '바',   # ㅃ
    9: '사',   # ㅅ
    10: '사',  # ㅆ
    11: '아',  # ㅇ
    12: '자',  # ㅈ
    13: '자',  # ㅉ
    14: '차',  # ㅊ
    15: '카',  # ㅋ
    16: '타',  # ㅌ
    17: '파',  # ㅍ
    18: '하'   # ㅎ
}

# 21개 중성 → 10개 그룹 매핑
JUNGSEONG_TO_GROUP = {
    0: '아',   # ㅏ
    1: '아',   # ㅐ
    2: '야',   # ㅑ
    3: '여',   # ㅕ
    4: '어',   # ㅓ
    5: '어',   # ㅔ
    6: '오',   # ㅗ
    7: '오',   # ㅘ
    8: '오',   # ㅙ
    9: '오',   # ㅚ
    10: '요',  # ㅛ
    11: '우',  # ㅜ
    12: '우',  # ㅝ
    13: '우',  # ㅞ
    14: '우',  # ㅟ
    15: '유',  # ㅠ
    16: '으',  # ㅡ
    17: '으',  # ㅢ
    18: '이',  # ㅣ
    19: '이',  # 이로 통합
    20: '이'   # 이로 통합
}

def is_hangul(char):
    """한글 체크"""
    code = ord(char)
    return 0xAC00 <= code <= 0xD7A3

def is_digit(char):
    """숫자 체크"""
    return char.isdigit()

def is_english(char):
    """영문 체크"""
    return char.isalpha()

def get_char_category(char):
    """첫 글자로 파일 결정"""
    if is_digit(char):
        return char  # 0~9
    elif is_english(char):
        return char.lower()  # a~z (소문자로 통합)
    elif is_hangul(char):
        return classify_korean_syllable(char)
    else:
        return '_'

def classify_korean_syllable(char):
    """한글 음절 분류: 초성그룹 + 중성그룹"""
    if not is_hangul(char):
        return '_'
    
    code = ord(char) - 0xAC00
    choseong = code // 588           # 초성 (0~18)
    jungseong = (code % 588) // 28   # 중성 (0~20)
    
    # 초성 → 그룹
    group = CHOSEONG_TO_GROUP.get(choseong, '_')
    
    # 중성 → 그룹
    vowel_group = JUNGSEONG_TO_GROUP.get(jungseong, '_')
    
    return f"{group}{vowel_group}"

def split_csv():
    """CSV 파일 분할"""
    # 출력 디렉토리 생성
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    
    print(f"📂 입력 파일: {INPUT_FILE}")
    print(f"📁 출력 디렉토리: {OUTPUT_DIR}")
    print("")
    
    # 출력 파일 쓰기 객체 관리
    output_files = {}
    file_counts = defaultdict(int)
    
    # CSV 읽기
    with open(INPUT_FILE, 'r', encoding=ENCODING) as infile:
        reader = csv.reader(infile)
        
        # 헤더 읽기
        header = next(reader, None)
        if header is None:
            print("❌ 파일이 비어있습니다.")
            return
        
        header_str = ','.join(header) + '\n'
        print(f"📋 헤더: {header_str.strip()}")
        print("")
        
        # 데이터 행 처리
        total_rows = 0
        for row_idx, row in enumerate(reader, start=1):
            if not row:
                continue
            
            total_rows += 1
            # company_name은 첫 번째 필드
            company_name = row[0].strip()
            
            if not company_name:
                continue
            
            # 분류 키 생성
            first_char = company_name[0]
            category = get_char_category(first_char)
            file_name = f"{category}.csv"
            
            # 출력 파일 생성 또는 가져오기
            if file_name not in output_files:
                output_path = os.path.join(OUTPUT_DIR, file_name)
                output_files[file_name] = open(output_path, 'w', encoding=ENCODING)
                output_files[file_name].write(header_str)
                print(f"📝 생성: {file_name}")
            
            # 기록
            output_files[file_name].write(','.join(row) + '\n')
            file_counts[file_name] += 1
            
            # 진행 상황 출력 (10만 건마다)
            if total_rows % 100000 == 0:
                print(f"  ⏳ 처리 중... {total_rows:,}건")
    
    # 모든 파일 닫기
    for file_name, f in output_files.items():
        f.close()
    
    # 결과 출력
    print("")
    print("✅ CSV 분할 완료!")
    print(f"📊 총 처리: {total_rows:,}건")
    print(f"📁 생성 파일: {len(output_files)}개")
    print("")
    print("📂 파일별 개수:")
    for file_name, count in sorted(file_counts.items()):
        print(f"  {file_name}: {count:,}건")

if __name__ == '__main__':
    split_csv()