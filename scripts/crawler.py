import os
import re
import json
import requests
import pdfplumber

# 司法特考三等監獄官 6 大專業科目代碼與考選部試卷編號規範
SUBJECT_MAP = [
    {"id": "CL-JJA", "name": "刑法與少年事件處理法", "type": "law", "paper_code": "30730", "keywords": ["刑法", "少事法", "要件", "違法性", "處遇"]},
    {"id": "JEL", "name": "監獄行刑法與羈押法", "type": "law", "paper_code": "30740", "keywords": ["監獄行刑法", "羈押法", "程序", "裁量", "救濟", "處分"]},
    {"id": "CRIM", "name": "犯罪學與再犯預測", "type": "theory", "paper_code": "30750", "keywords": ["理論", "機制", "預防", "再犯", "學者"]},
    {"id": "PS", "name": "監獄學", "type": "theory", "paper_code": "30760", "keywords": ["監獄學", "次文化", "管理", "戒護", "處遇"]},
    {"id": "CP", "name": "刑事政策", "type": "theory", "paper_code": "30770", "keywords": ["刑事政策", "兩極化", "應報", "預防", "轉向"]},
    {"id": "CC", "name": "諮商與矯正輔導", "type": "counseling", "paper_code": "30780", "keywords": ["諮商", "動機", "晤談", "成癮", "改變歷程"]}
]

# 年度清單 (108 年新制實施起至 115 年)
YEARS = [114, 113, 112, 111, 110, 109, 108]

def extract_questions_from_pdf(pdf_url, year, subject):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(pdf_url, headers=headers, timeout=15)
        if res.status_code != 200 or len(res.content) < 5000:
            return []
    except Exception:
        return []

    temp_path = f"temp_{year}_{subject['id']}.pdf"
    with open(temp_path, "wb") as f:
        f.write(res.content)

    full_text = ""
    try:
        with pdfplumber.open(temp_path) as pdf:
            for page in pdf.pages:
                full_text += (page.extract_text() or "") + "\n"
    except Exception:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return []

    if os.path.exists(temp_path):
        os.remove(temp_path)

    # 匹配國考申論題題號 一、 二、 三、 四、
    pattern = re.compile(r'([一二三四五]、)([\s\S]+?)(?=(?:[一二三四五]、|代號：|\Z))')
    matches = pattern.findall(full_text)
    q_map = {'一、': 1, '二、': 2, '三、': 3, '四、': 4, '五、': 5}

    results = []
    for idx, (prefix, body) in enumerate(matches):
        cleaned = body.strip().replace("\n", "").replace(" ", "")
        if len(cleaned) < 15:
            continue
        score_match = re.search(r'（(\d+)分）', cleaned)
        score = int(score_match.group(1)) if score_match else 25

        results.append({
            "id": f"{year}-PW-{subject['id']}-{idx+1:02d}",
            "exam_name": "公務人員特種考試司法人員三等考試",
            "category": "監獄官",
            "year": year,
            "subject_id": subject["id"],
            "subject_name": subject["name"],
            "subject_type": subject["type"],
            "question_no": q_map.get(prefix, idx + 1),
            "score": score,
            "question_text": cleaned,
            "source_name": f"考選部{year}年司法人員特考三等試卷",
            "official_source_url": pdf_url,
            "question_type": "申論題",
            "tags": [subject["name"], f"{year}年真題"],
            "benchmark_keywords": [{"term": kw, "weight": 5} for kw in subject["keywords"]],
            "suggested_structure": [
                "一、爭點與法律/理論依據分析",
                "二、具體事實涵攝與學說實務見解評析",
                "三、結論與實務因應方向"
            ]
        })
    return results

def main():
    all_questions = []
    print("啟動考選部題庫自動抓取程序...")

    for year in YEARS:
        ce_year = year + 1911
        exam_code = f"{year}130"
        for subject in SUBJECT_MAP:
            # 考選部官方試卷 PDF 下載規範格式
            pdf_url = f"https://wwwq.moex.gov.tw/exam/ExamFileDownload.svc?FileDownload/{ce_year}/{exam_code}_{subject['paper_code']}.pdf"
            qs = extract_questions_from_pdf(pdf_url, year, subject)
            if qs:
                print(f"✓ 成功擷取 {year}年 {subject['name']} 共 {len(qs)} 題")
                all_questions.extend(qs)
            else:
                print(f"- {year}年 {subject['name']} 官方試卷暫未發布或路徑調整")

    output_file = "questions.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_questions, f, ensure_ascii=False, indent=2)

    print(f"\n全部爬取完成！共生成 {len(all_questions)} 道題目，已寫入 {output_file}")

if __name__ == "__main__":
    main()

