#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TF Bio Compliance Scanner
自動掃描 Markdown/HTML 文件中的違規醫療與誇張宣稱詞彙。
"""

import re
import sys
from datetime import datetime

# 載入違規詞彙規則庫 (內嵌版本)
VIOLATION_RULES = {
    "medical_efficacy": [
        r"治療", r"治癒", r"根治", r"預防\s+疾病", r"消炎", 
        r"止痛", r"抗癌", r"降血壓", r"降血糖", r"恢復健康"
    ],
    "exaggerated": [
        r"最有效", r"第一", r"唯一", r"最強", r"頂級", 
        r"奇蹟", r"100%\s*有效", r"包治百病", r"聖品", r"神效"
    ],
    "unapproved_health_claims": [
        r"調節免疫", r"延緩衰老", r"增加骨本", r"改善過敏", 
        r"改善睡眠品質", r"改善視力", r"護肝"
    ]
}

def scan_file(file_path):
    """掃描單一文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"[ERROR] 文件未找到: {file_path}")
        return None
    except Exception as e:
        print(f"[ERROR] 讀取失敗: {e}")
        return None

    issues = []
    lines = content.split('\n')

    for line_num, line in enumerate(lines, 1):
        # 檢查醫療效能
        for category, patterns in VIOLATION_RULES.items():
            for pattern in patterns:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    issues.append({
                        "line": line_num,
                        "category": category,
                        "word": match.group(),
                        "context": line.strip()[:100],
                        "severity": "CRITICAL" if category == "medical_efficacy" else "WARNING"
                    })

    return issues

def generate_report(issues, file_path):
    """生成合規報告"""
    if not issues:
        return {
            "status": "PASS",
            "file": file_path,
            "scan_time": datetime.now().isoformat(),
            "issues": [],
            "summary": "✅ 未發現違規詞彙"
        }
    
    critical_count = len([i for i in issues if i["severity"] == "CRITICAL"])
    warning_count = len([i for i in issues if i["severity"] == "WARNING"])
    
    report = {
        "status": "FAIL" if critical_count > 0 else "WARNING",
        "file": file_path,
        "scan_time": datetime.now().isoformat(),
        "summary": f"🚨 發現 {critical_count} 個嚴重違規，{warning_count} 個警告",
        "issues": issues
    }
    return report

def main():
    if len(sys.argv) < 2:
        print("用法: python compliance-scanner.py <file_path> [file_path2 ...]")
        sys.exit(1)

    files = sys.argv[1:]
    all_reports = []
    total_issues = 0

    print(f"🛡️ 開始掃描 {len(files)} 個文件...")
    for file_path in files:
        issues = scan_file(file_path)
        if issues:
            report = generate_report(issues, file_path)
            all_reports.append(report)
            total_issues += len(issues)
            print(f"❌ {file_path}: {report['summary']}")
        else:
            print(f"✅ {file_path}: 未發現違規")

    # 輸出最終結果
    print("\n--- 📊 掃描總結 ---")
    if total_issues == 0:
        print("🎉 所有文件合規！可以部署。")
        sys.exit(0)
    else:
        print(f"⚠️ 共發現 {total_issues} 個問題。請修正後重新掃描。")
        print("👉 建議動作：檢查 CRITICAL 違規詞彙並依規則庫替換。")
        sys.exit(1)

if __name__ == "__main__":
    main()