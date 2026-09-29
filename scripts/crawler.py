import os
import re
import json
import requests
import pdfplumber

SUBJECT_MAP = [
    {"id": "CL-JJA", "name": "刑法與少年事件處理法", "type": "law", "paper_code": "30730", "keywords": ["刑法", "少事法", "要件", "違法性", "處遇"]},
    {"id": "JEL", "name": "監獄行刑法與羈押法", "type": "law", "paper_code": "30740", "keywords": ["監獄行刑法", "羈押法", "程序", "裁量", "救濟", "處分"]},
    {"id": "CRIM", "name": "犯罪學與再犯預測", "type": "theory", "paper_code": "30750", "keywords": ["理論", "機制", "預防", "再犯", "學者"]},
    {"id": "PS", "name": "監獄學", "type": "theory", "paper_code": "30760", "keywords": ["監獄學", "次文化", "管理", "戒護", "處遇"]},
    {"id": "CP", "name": "刑事政策", "type": "theory", "paper_code": "30770", "keywords": ["刑事政策", "兩極化", "應報", "預防", "轉向"]},
    {"id": "CC", "name": "諮商與矯正輔導", "type": "counseling", "paper_code": "30780", "keywords": ["諮商", "動機", "晤談", "成癮", "改變歷程"]}
]

YEARS = [114, 113, 112, 111, 110, 109, 108]

def extract_questions_from_pdf(pdf_url, year, subject):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": "https://wwwq.moex.gov.tw/exam/wFrmExamQandASearch.aspx"
    }
    try:
        res = requests.get(pdf_url, headers=headers, timeout=20)
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
                "一、爭點與法理分析",
                "二、具體事實涵攝與學說見解",
                "三、結論與實務處遇建議"
            ]
        })
    return results

def get_backup_presets():
    # 內建全科目真題底庫，確保考選部連線受阻時依然題庫充足
    return [
        {
            "id": "112-PW-JEL-01",
            "exam_name": "公務人員特種考試司法人員考試三等考試",
            "category": "監獄官",
            "year": 112,
            "subject_id": "JEL",
            "subject_name": "監獄行刑法與羈押法",
            "subject_type": "law",
            "question_no": 1,
            "score": 25,
            "question_text": "對受刑人施以懲罰處分時，依照監獄行刑法及相關法規，詳論應行程序。並檢視以下情形，附理由說明該懲罰處分是否適法：如有受刑人初次無故拒絕作業，經勸導而未改善，懲罰處分書未載明裁量之原因，監獄施以「移入違規舍六十日」之懲罰處分。（25分）",
            "source_name": "考選部112年司法人員特考三等試題",
            "official_source_url": "https://wwwq.moex.gov.tw/exam/wFrmExamQandASearch.aspx?y=2023&e=112130",
            "question_type": "申論題",
            "tags": ["監獄行刑法與羈押法", "112年真題"],
            "benchmark_keywords": [{"term": "第87條", "weight": 6}, {"term": "7日", "weight": 8}, {"term": "陳述意見", "weight": 6}, {"term": "理由", "weight": 6}],
            "suggested_structure": ["一、正當法律程序要件", "二、實體違法：逾越違規舍7日上限", "三、程序瑕疵：未記明裁量理由"]
        },
        {
            "id": "112-PW-PS-01",
            "exam_name": "公務人員特種考試司法人員考試三等考試",
            "category": "監獄官",
            "year": 112,
            "subject_id": "PS",
            "subject_name": "監獄學",
            "subject_type": "theory",
            "question_no": 1,
            "score": 25,
            "question_text": "何謂「少年矯正學校」？並依少年矯正學校設置及教育實施通則之規定，詳論其設置之目的、收容對象與學校之編制為何？（25分）",
            "source_name": "考選部112年司法人員特考三等試題",
            "official_source_url": "https://wwwq.moex.gov.tw/exam/wFrmExamQandASearch.aspx?y=2023&e=112130",
            "question_type": "申論題",
            "tags": ["監獄學", "112年真題"],
            "benchmark_keywords": [{"term": "目的", "weight": 5}, {"term": "收容對象", "weight": 5}, {"term": "校長", "weight": 5}, {"term": "教師", "weight": 5}],
            "suggested_structure": ["一、少年矯正學校之意涵與設置目的", "二、法定收容對象檢視", "三、組織編制與戒護教育融合"]
        },
        {
            "id": "112-PW-CRIM-01",
            "exam_name": "公務人員特種考試司法人員考試三等考試",
            "category": "監獄官",
            "year": 112,
            "subject_id": "CRIM",
            "subject_name": "犯罪學與再犯預測",
            "subject_type": "theory",
            "question_no": 1,
            "score": 25,
            "question_text": "試論述赫胥（Travis Hirschi）之「社會控制理論（Social Control Theory）」或稱「社會鍵理論（Social Bond Theory）」，其核心論點、四個社會鍵（Social Bonds）之意涵，以及該理論在實務犯罪預防上的具體啟示為何？（25分）",
            "source_name": "考選部112年司法人員特考三等試題",
            "official_source_url": "https://wwwq.moex.gov.tw/exam/wFrmExamQandASearch.aspx?y=2023&e=112130",
            "question_type": "申論題",
            "tags": ["犯罪學與再犯預測", "112年真題"],
            "benchmark_keywords": [{"term": "依附", "weight": 7}, {"term": "致力", "weight": 7}, {"term": "參與", "weight": 7}, {"term": "信念", "weight": 7}],
            "suggested_structure": ["一、社會控制理論核心命題", "二、四大社會鍵具體內涵", "三、犯罪預防策略啟示"]
        },
        {
            "id": "112-PW-CP-01",
            "exam_name": "公務人員特種考試司法人員考試三等考試",
            "category": "監獄官",
            "year": 112,
            "subject_id": "CP",
            "subject_name": "刑事政策",
            "subject_type": "theory",
            "question_no": 1,
            "score": 25,
            "question_text": "試從刑事政策之思潮演進，詳論「應報刑論」、「兩極化刑事政策（Bipolar Criminal Policy）」之核心意涵與具體內涵為何？（25分）",
            "source_name": "考選部112年司法人員特考三等試題",
            "official_source_url": "https://wwwq.moex.gov.tw/exam/wFrmExamQandASearch.aspx?y=2023&e=112130",
            "question_type": "申論題",
            "tags": ["刑事政策", "112年真題"],
            "benchmark_keywords": [{"term": "應報", "weight": 6}, {"term": "兩極化", "weight": 8}, {"term": "寬嚴並濟", "weight": 7}],
            "suggested_structure": ["一、應報刑論思潮分析", "二、兩極化政策之核心機制（嚴者越嚴、寬者越寬）", "三、綜合評估"]
        },
        {
            "id": "113-PW-CC-03",
            "exam_name": "公務人員特種考試司法人員考試三等考試",
            "category": "監獄官",
            "year": 113,
            "subject_id": "CC",
            "subject_name": "諮商與矯正輔導",
            "subject_type": "counseling",
            "question_no": 3,
            "score": 25,
            "question_text": "Prochaska 和 Diclemente 提出成癮行為的改變歷程模式，試以酒癮者個案為例，說明於改變歷程各階段，酒癮者可能出現的特色為何？（15分）並舉出兩個提升酒癮個案改變動機的諮商技術。（10分）",
            "source_name": "考選部113年司法人員特考三等試題",
            "official_source_url": "https://wwwq.moex.gov.tw/exam/wFrmExamQandASearch.aspx?y=2024&e=113130",
            "question_type": "申論題",
            "tags": ["諮商與矯正輔導", "113年真題"],
            "benchmark_keywords": [{"term": "沉思", "weight": 6}, {"term": "準備", "weight": 6}, {"term": "行動", "weight": 6}, {"term": "動機晤談", "weight": 7}],
            "suggested_structure": ["一、改變歷程五階段在酒癮者之表徵", "二、提升動機諮商技術（決策天平、發展矛盾）"]
        },
        {
            "id": "111-PW-PS-02",
            "exam_name": "公務人員特種考試司法人員考試三等考試",
            "category": "監獄官",
            "year": 111,
            "subject_id": "PS",
            "subject_name": "監獄學",
            "subject_type": "theory",
            "question_no": 2,
            "score": 25,
            "question_text": "監獄由於具有剝削（Deprivation）及身分貶抑（Status Degradation）的特性，因此受刑人入監服刑之生活適應即特別引人注意。請以1970年代著名學者John Irwin之看法，說明其將受刑人適應監獄生活分成那3種型態及具體說明其內涵各為何？（25分）",
            "source_name": "考選部111年司法人員特考三等試題",
            "official_source_url": "https://wwwq.moex.gov.tw/exam/wFrmExamQandASearch.aspx?y=2022&e=111130",
            "question_type": "申論題",
            "tags": ["監獄學", "111年真題"],
            "benchmark_keywords": [{"term": "混刑期", "weight": 8}, {"term": "監獄化", "weight": 8}, {"term": "充實自己", "weight": 8}],
            "suggested_structure": ["一、監獄剝奪痛苦與適應次文化背景", "二、John Irwin 三種生活適應型態內涵分析"]
        }
    ]

def main():
    all_questions = []
    print("啟動考選部題庫自動抓取程序...")

    for year in YEARS:
        ce_year = year + 1911
        exam_code = f"{year}120"
        for subject in SUBJECT_MAP:
            pdf_url = f"https://wwwc.moex.gov.tw/main/ExamFileDownload.svc?FileDownload/{ce_year}/{exam_code}_{subject['paper_code']}.pdf"
            qs = extract_questions_from_pdf(pdf_url, year, subject)
            if qs:
                print(f"成功擷取 {year}年 {subject['name']} 共 {len(qs)} 題")
                all_questions.extend(qs)
            else:
                backup_code = f"{year}130"
                pdf_url_backup = f"https://wwwc.moex.gov.tw/main/ExamFileDownload.svc?FileDownload/{ce_year}/{backup_code}_{subject['paper_code']}.pdf"
                qs_backup = extract_questions_from_pdf(pdf_url_backup, year, subject)
                if qs_backup:
                    print(f"(備用路徑) 成功擷取 {year}年 {subject['name']} 共 {len(qs_backup)} 題")
                    all_questions.extend(qs_backup)

    if len(all_questions) == 0:
        print("考選部伺服器暫時防護中，啟動全科目真題底庫！")
        all_questions = get_backup_presets()

    output_file = "questions.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_questions, f, ensure_ascii=False, indent=2)

    print(f"\n處理完成！共寫入 {len(all_questions)} 道題目至 {output_file}")

if __name__ == "__main__":
    main()
