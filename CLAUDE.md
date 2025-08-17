# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python project for crawling Naver Place reviews using the `crawl4ai` library. The project consists of a single main script that asynchronously crawls restaurant reviews from Naver Place and extracts structured data using LLM-based content extraction.

## Key Dependencies

- `crawl4ai`: Main web crawling library with async support
- `pandas`: Data manipulation and CSV export
- `json`: JSON parsing for structured data
- `asyncio`: Asynchronous execution
- `datetime`: Timestamp generation for file naming

## Main Architecture

The project follows a simple async pipeline architecture:

1. **Web Crawling (`crawl_naver_place_reviews()`)**: Uses AsyncWebCrawler to load Naver Place pages with JavaScript rendering, clicking "more" buttons and scrolling to load additional reviews
2. **Data Extraction (`extract_review_data()`)**: Uses LLM-based extraction strategy to convert raw HTML into structured JSON data with review content, dates, ratings, and view counts  
3. **Data Processing (`main()`)**: Orchestrates the pipeline, converts JSON to DataFrame, and exports results to timestamped CSV files

## Running the Code

```bash
python test_01.py
```

The script will:
- Crawl the target Naver Place URL with JavaScript rendering
- Extract structured review data using LLM prompts
- Save results to a timestamped CSV file (format: `naver_reviews_YYYYMMDD_HHMMSS.csv`)

## Key Implementation Details

- Uses CSS selector `.place_section_content` to wait for review section loading
- Implements JavaScript injection to click "more" buttons and scroll for additional content
- 3-second delay before HTML return to ensure full page load
- LLM extraction prompt expects specific JSON schema with review_content, write_date, visit_date, view_count, and rating fields
- Error handling with try/catch and success status checking
- UTF-8-BOM encoding for CSV export to handle Korean text properly