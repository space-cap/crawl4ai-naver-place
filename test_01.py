import asyncio
from crawl4ai import AsyncWebCrawler
import json
import pandas as pd
from datetime import datetime
import sys
import os
import re
from dotenv import load_dotenv

# .env 파일에서 환경변수 로드
load_dotenv()

# Windows 환경에서 UTF-8 인코딩 설정
if sys.platform == "win32":
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')


# HTML 파싱을 통한 리뷰 데이터 추출
async def extract_review_data():
    """리뷰 데이터를 구조화하여 추출"""
    
    # 타겟 URL
    url = "https://m.place.naver.com/restaurant/19792810/review/visitor?entry=ple&reviewSort=recent"
    
    async with AsyncWebCrawler(verbose=False) as crawler:
        # 페이지 크롤링
        result = await crawler.arun(
            url=url,
            word_count_threshold=1,
            wait_for="css:.place_section_content",  # 리뷰 섹션 로드 대기
            delay_before_return_html=3,  # 3초 대기 후 HTML 반환
            js_code=[
                # 리뷰 더보기 버튼들 클릭
                """
                // 리뷰 더보기 버튼 클릭
                const moreButtons = document.querySelectorAll('.review_more_btn, .btn_more');
                for(let button of moreButtons) {
                    if(button && button.offsetHeight > 0) {
                        button.click();
                        await new Promise(resolve => setTimeout(resolve, 1000));
                    }
                }
                """,
                # 페이지 스크롤로 추가 리뷰 로드
                """
                window.scrollTo(0, document.body.scrollHeight);
                await new Promise(resolve => setTimeout(resolve, 2000));
                """
            ]
        )
        
        if result.success:
            print(f"크롤링 성공! HTML 길이: {len(result.html)}")
            
            # HTML에서 리뷰 데이터 파싱
            reviews = parse_review_data(result.cleaned_html)
            return reviews
        else:
            print(f"크롤링 실패: {result.error_message}")
            return None

def parse_review_data(html_text):
    """HTML 텍스트에서 리뷰 데이터를 파싱"""
    reviews = []

    # 간단한 패턴 매칭으로 리뷰 정보 추출
    # 방문일 패턴: <time>8.13.수</time>
    visit_dates = re.findall(r'<time>([^<]+)</time>', html_text)

    # 리뷰어 이름 패턴: <span><span>넘버 One</span></span>
    reviewers = re.findall(r"<div><span><span>([^<]+)</span></span></div>", html_text)

    # 이모지와 태그 패턴 (리뷰 내용 대신)
    emojis = re.findall(r'<div><a href="#">([^<]+)</a></div>', html_text)

    # 방문 관련 태그들
    visit_tags = re.findall(r'<em>([^<]*방문[^<]*)</em>', html_text)

    print(f"찾은 방문일: {len(visit_dates)}개")
    print(f"찾은 리뷰어: {len(reviewers)}개") 
    print(f"찾은 이모지: {len(emojis)}개")
    print(f"찾은 방문태그: {len(visit_tags)}개")

    # 데이터 조합하여 리뷰 생성
    min_length = min(len(visit_dates), len(reviewers))

    for i in range(min_length):
        review = {
            "reviewer_name": reviewers[i] if i < len(reviewers) else "익명",
            "visit_date": visit_dates[i] if i < len(visit_dates) else "알 수 없음",
            "emoji_content": emojis[i] if i < len(emojis) else "",
            "visit_tag": visit_tags[i] if i < len(visit_tags) else "",
            "rating": 5  # 기본값
        }
        reviews.append(review)

    return reviews

# 실행 및 데이터 저장
async def main():
    """메인 실행 함수"""
    
    print("네이버 플레이스 리뷰 크롤링 시작...")
    
    try:
        # 리뷰 데이터 추출
        review_data = await extract_review_data()
        
        if review_data:
            # DataFrame으로 변환
            df = pd.DataFrame(review_data)
            
            # 결과 출력
            print(f"총 {len(df)}개의 리뷰를 수집했습니다!")
            print("\n수집된 데이터 샘플:")
            print(df.head())
            
            # CSV로 저장
            filename = f"naver_reviews_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            print(f"{filename}으로 저장완료!")
            
            return df
                
        else:
            print("리뷰 데이터 추출 실패")
            
    except Exception as e:
        print(f"오류 발생: {str(e)}")

# 실행
if __name__ == "__main__":
    reviews_df = asyncio.run(main())
