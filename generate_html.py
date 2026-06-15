#!/usr/bin/env python3
"""
Generate ROX project schedule HTML from clean_data.json
"""

import json
import os
import subprocess
import sys

def main():
    # ======================== READ DATA ========================
    with open('/tmp/clean_data.json', 'r', encoding='utf-8') as f:
        raw_data = json.load(f)

    with open('/tmp/all_people.json', 'r', encoding='utf-8') as f:
        all_people_data = json.load(f)

    # Transform records
    records = []
    for r in raw_data['records']:
        records.append({
            'title': r['工作内容'],
            'progress': r['进展'][0] if r.get('进展') else '',
            'testDate': r.get('最晚转测时间', ''),
            'freezeDate': r.get('封板时间', ''),
            'versionDate': r.get('版更时间', ''),
            'onlineDate': r.get('上线时间（功能owner维护）', ''),
            'startDate': r.get('启动日期', ''),
            'endDate': r.get('任务结束', ''),
            'assignee': r.get('执行人', []),
            'region': r.get('地区', []),
            'id': r.get('_id', ''),
            'jiraUrl': r.get('JIRA单', ''),
            'jiraKey': r.get('Jira Key', ''),
            'extVersion': r.get('对外版本', ''),
            'parentTask': r.get('本表--父记录', '')
        })

    # Serialize to JSON string for safe embedding
    # Use ensure_ascii=False so Chinese chars remain readable in the HTML source
    data_json_str = json.dumps(records, ensure_ascii=False)
    # Escape for embedding in a <script type="application/json"> block
    # Only need to escape </script> which would break HTML parsing
    data_json_safe = data_json_str.replace('</', '<\\/')

    # Load version name mapping
    with open('/tmp/ver_name_map.json', 'r', encoding='utf-8') as f:
        ver_name_map = json.load(f)
    ver_map_json_str = json.dumps(ver_name_map, ensure_ascii=False)
    ver_map_json_safe = ver_map_json_str.replace('</', '<\\/')

    # Serialize all_people data
    people_json_str = json.dumps(all_people_data, ensure_ascii=False)
    people_json_safe = people_json_str.replace('</', '<\\/')


    # ======================== BUILD HTML ========================
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ROX开发阶段项目排期看板</title>
<style>
/* ===== MORANDI GLASSMORPHISM DESIGN SYSTEM ===== */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

:root {{
  /* Morandi Monochromatic - Dusty Blue-Violet Palette */
  --morandi-50: #F5F3F7;
  --morandi-100: #ECE8F0;
  --morandi-200: #DDD6E3;
  --morandi-300: #C4B9CE;
  --morandi-400: #A99BB2;
  --morandi-500: #8E7D99;
  --morandi-600: #736580;
  --morandi-700: #5A4E66;
  --morandi-800: #43394E;
  --morandi-900: #2D2538;

  /* Functional Colors - Morandi Tones */
  --primary: #7B8CDE;
  --primary-light: #9DA8E8;
  --primary-dark: #5F6FBE;
  --primary-bg: #ECEEF8;
  --primary-glow: rgba(123,140,222,0.15);

  --success: #8DB5A2;
  --success-light: #B5D4C5;
  --success-bg: #EDF5F0;

  --warning: #D4A574;
  --warning-light: #E4C4A0;
  --warning-bg: #FDF5EC;

  --danger: #C48B8B;
  --danger-light: #D9AAAA;
  --danger-bg: #F8EFEF;

  --info: #8BA7C4;
  --info-light: #B0C8DE;

  /* Glassmorphism Tokens */
  --glass-bg: rgba(255,255,255,0.45);
  --glass-bg-strong: rgba(255,255,255,0.65);
  --glass-border: rgba(255,255,255,0.5);
  --glass-shadow: 0 8px 32px rgba(45,37,56,0.08);
  --glass-shadow-hover: 0 12px 40px rgba(45,37,56,0.12);
  --glass-blur: blur(20px);
  --glass-blur-strong: blur(30px);

  /* Watercolor Wash Backgrounds */
  --wash-gradient: linear-gradient(135deg, #F5F3F7 0%, #ECE8F0 25%, #E8E0ED 50%, #ECEEF8 75%, #F0EDE8 100%);
  --wash-header: linear-gradient(135deg, #7B8CDE 0%, #8E7D99 50%, #A99BB2 100%);
  --wash-card: linear-gradient(145deg, rgba(255,255,255,0.6) 0%, rgba(245,243,247,0.4) 100%);

  /* Neutral Scale */
  --gray-1: #F8F6FA;
  --gray-2: #F0EDE5;
  --gray-3: #E0DAD0;
  --gray-4: #C4BDB3;
  --gray-5: #8E877D;
  --gray-6: #5E5850;
  --gray-7: #3A3530;

  /* Radius & Shadows */
  --radius-sm: 8px;
  --radius-md: 14px;
  --radius-lg: 20px;
  --radius-xl: 28px;
  --shadow-sm: 0 2px 8px rgba(45,37,56,0.04);
  --shadow-md: 0 4px 16px rgba(45,37,56,0.06);
  --shadow-lg: 0 8px 32px rgba(45,37,56,0.08);
  --shadow-xl: 0 16px 48px rgba(45,37,56,0.1);

  /* Typography */
  --font: 'Inter', -apple-system, "PingFang SC", "Noto Sans SC", "Microsoft YaHei", sans-serif;
  --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  --transition-slow: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}}

* {{ margin:0; padding:0; box-sizing:border-box; }}

body {{
  font-family: var(--font);
  background: var(--wash-gradient);
  background-attachment: fixed;
  color: var(--gray-7);
  line-height: 1.6;
  min-height: 100vh;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}}

/* Decorative watercolor blobs */
body::before {{
  content: '';
  position: fixed;
  top: -20%;
  right: -10%;
  width: 600px;
  height: 600px;
  background: radial-gradient(ellipse, rgba(123,140,222,0.08) 0%, transparent 70%);
  border-radius: 50%;
  pointer-events: none;
  z-index: 0;
}}
body::after {{
  content: '';
  position: fixed;
  bottom: -15%;
  left: -10%;
  width: 500px;
  height: 500px;
  background: radial-gradient(ellipse, rgba(142,125,153,0.06) 0%, transparent 70%);
  border-radius: 50%;
  pointer-events: none;
  z-index: 0;
}}

/* ========== HEADER - Glassmorphism Bar ========== */
.header {{
  background: var(--wash-header);
  color: #fff;
  padding: 16px 32px;
  position: sticky;
  top: 0;
  z-index: 100;
  backdrop-filter: var(--glass-blur-strong);
  -webkit-backdrop-filter: var(--glass-blur-strong);
  box-shadow: 0 4px 30px rgba(123,140,222,0.2);
  border-bottom: 1px solid rgba(255,255,255,0.15);
}}
.header-inner {{
  max-width: 1440px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 10px;
}}
.header h1 {{
  font-size: 18px;
  font-weight: 600;
  letter-spacing: 1px;
  text-shadow: 0 1px 3px rgba(0,0,0,0.1);
}}
.header h1 small {{
  font-weight: 300;
  opacity: 0.8;
  font-size: 12px;
  margin-left: 12px;
  letter-spacing: 0.5px;
}}
.header-actions {{
  display: flex;
  align-items: center;
  gap: 8px;
}}
.container {{
  max-width: 1440px;
  margin: 0 auto;
  padding: 20px 24px;
  position: relative;
  z-index: 1;
}}

/* ========== BUTTONS - Soft & Elegant ========== */
.btn {{
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 7px 18px;
  border: none;
  border-radius: var(--radius-xl);
  font-size: 13px;
  font-family: var(--font);
  cursor: pointer;
  transition: var(--transition);
  font-weight: 500;
  white-space: nowrap;
  letter-spacing: 0.3px;
}}
.btn-primary {{
  background: var(--glass-bg-strong);
  color: var(--primary-dark);
  backdrop-filter: var(--glass-blur);
  border: 1px solid var(--glass-border);
}}
.btn-primary:hover {{
  background: rgba(255,255,255,0.85);
  transform: translateY(-1px);
  box-shadow: var(--glass-shadow);
}}
.btn-outline {{
  background: transparent;
  color: rgba(255,255,255,0.9);
  border: 1.5px solid rgba(255,255,255,0.35);
  border-radius: var(--radius-xl);
}}
.btn-outline:hover {{
  border-color: rgba(255,255,255,0.6);
  background: rgba(255,255,255,0.1);
}}
.btn-sm {{ padding: 4px 12px; font-size: 12px; }}
.btn-primary-solid {{
  background: var(--primary);
  color: #fff;
  border-radius: var(--radius-xl);
  box-shadow: 0 4px 15px rgba(123,140,222,0.3);
}}
.btn-primary-solid:hover {{
  background: var(--primary-dark);
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(123,140,222,0.4);
}}
.btn-danger {{ background: var(--danger); color: #fff; border-radius: var(--radius-xl); }}
.btn-danger:hover {{ opacity: 0.85; }}
.btn-success {{ background: var(--success); color: #fff; border-radius: var(--radius-xl); }}
.btn-success:hover {{ opacity: 0.85; }}

/* ========== STAT CARDS - Glass Cards ========== */
.stats-row {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}}
.stat-card {{
  background: var(--wash-card);
  backdrop-filter: var(--glass-blur);
  -webkit-backdrop-filter: var(--glass-blur);
  border-radius: var(--radius-lg);
  padding: 20px 22px;
  border: 1px solid var(--glass-border);
  box-shadow: var(--glass-shadow);
  transition: var(--transition);
  position: relative;
  overflow: hidden;
}}
.stat-card::before {{
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 4px;
  height: 100%;
  border-radius: 4px 0 0 4px;
}}
.stat-card:nth-child(1)::before {{ background: var(--primary); }}
.stat-card:nth-child(2)::before {{ background: var(--warning); }}
.stat-card:nth-child(3)::before {{ background: var(--success); }}
.stat-card:nth-child(4)::before {{ background: var(--morandi-400); }}
.stat-card:nth-child(5)::before {{ background: var(--danger); }}
.stat-card:nth-child(6)::before {{ background: var(--morandi-700); }}
.stat-card:hover {{
  transform: translateY(-3px);
  box-shadow: var(--glass-shadow-hover);
}}
.stat-card .label {{
  font-size: 12px;
  color: var(--morandi-500);
  margin-bottom: 6px;
  font-weight: 500;
  letter-spacing: 0.5px;
  text-transform: uppercase;
}}
.stat-card .value {{
  font-size: 30px;
  font-weight: 700;
  color: var(--morandi-800);
  letter-spacing: -0.5px;
}}
.stat-card .sub {{
  font-size: 11px;
  color: var(--morandi-400);
  margin-top: 4px;
}}

/* ========== FILTER BAR - Glass Panel ========== */
.filter-bar {{
  position: relative;
  z-index: 100;
  background: var(--glass-bg-strong);
  backdrop-filter: var(--glass-blur);
  -webkit-backdrop-filter: var(--glass-blur);
  border-radius: var(--radius-lg);
  padding: 16px 20px;
  box-shadow: var(--glass-shadow);
  border: 1px solid var(--glass-border);
  margin-bottom: 20px;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px;
}}
.filter-group {{
  display: flex;
  align-items: center;
  gap: 6px;
}}
.filter-group label {{
  font-size: 12px;
  color: var(--morandi-600);
  font-weight: 600;
  white-space: nowrap;
  letter-spacing: 0.3px;
}}
.filter-group select {{
  padding: 6px 12px;
  border: 1px solid var(--morandi-200);
  border-radius: var(--radius-sm);
  font-size: 13px;
  font-family: var(--font);
  background: rgba(255,255,255,0.7);
  color: var(--morandi-800);
  cursor: pointer;
  outline: none;
  min-width: 100px;
  transition: var(--transition);
}}
.filter-group select:focus {{
  border-color: var(--primary-light);
  box-shadow: 0 0 0 3px var(--primary-glow);
}}

/* Multi-select filters */
.multi-select {{ position: relative; min-width: 110px; }}
.multi-select-trigger {{
  display: flex; align-items: center; justify-content: space-between;
  padding: 6px 12px;
  background: rgba(255,255,255,0.7);
  border: 1px solid var(--morandi-200);
  border-radius: var(--radius-sm);
  cursor: pointer; font-size: 13px;
  min-height: 30px; gap: 4px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  transition: var(--transition);
}}
.multi-select-trigger:hover {{ border-color: var(--primary-light); }}
.multi-select-trigger .ms-count {{ font-size: 11px; color: var(--primary); margin-right: 4px; font-weight: 600; }}
.multi-select-trigger .ms-arrow {{ font-size: 10px; opacity: 0.4; flex-shrink: 0; }}
.multi-select-panel {{
  position: absolute; top: 100%; left: 0; min-width: 100%;
  z-index: 9999;
  background: var(--glass-bg-strong);
  backdrop-filter: var(--glass-blur-strong);
  -webkit-backdrop-filter: var(--glass-blur-strong);
  border: 1px solid var(--morandi-200);
  border-radius: var(--radius-md);
  max-height: 240px; overflow-y: auto;
  box-shadow: var(--shadow-lg);
  padding: 6px 0;
}}
.multi-select-panel label {{
  display: flex; align-items: center; gap: 6px;
  padding: 5px 12px; font-size: 12px; cursor: pointer; white-space: nowrap;
  transition: var(--transition);
}}
.multi-select-panel label:hover {{ background: var(--primary-bg); }}
.multi-select-panel input[type=checkbox] {{ margin: 0; flex-shrink: 0; accent-color: var(--primary); }}

/* Person search */
.person-search {{ position: relative; z-index: 10; }}
.person-search input {{
  padding: 6px 12px;
  border: 1px solid var(--morandi-200);
  border-radius: var(--radius-sm);
  font-size: 13px;
  background: rgba(255,255,255,0.7);
  min-width: 140px;
  outline: none;
  transition: var(--transition);
}}
.person-search input:focus {{ border-color: var(--primary-light); box-shadow: 0 0 0 3px var(--primary-glow); }}
.ps-results {{
  position: absolute; top: 100%; left: 0; right: 0; z-index: 9999;
  background: var(--glass-bg-strong);
  backdrop-filter: var(--glass-blur-strong);
  border: 1px solid var(--morandi-200);
  border-radius: var(--radius-md);
  max-height: 200px; overflow-y: auto;
  box-shadow: var(--shadow-lg);
  display: none;
}}
.ps-item {{ padding: 6px 12px; font-size: 12px; cursor: pointer; transition: var(--transition); }}
.ps-item:hover {{ background: var(--primary-bg); }}

/* Parent gantt */
.parent-gantt-wrap {{ padding: 0; }}
.parent-gantt-wrap .pg-header {{
  display: flex; gap: 8px; align-items: center; margin-bottom: 12px;
  padding: 14px; background: var(--glass-bg); border-radius: var(--radius-md);
  flex-wrap: wrap; border: 1px solid var(--glass-border);
}}
.parent-gantt-wrap .pg-header input {{
  flex: 1; min-width: 200px; padding: 8px 14px;
  border: 1px solid var(--morandi-200); border-radius: var(--radius-sm);
  font-size: 13px; background: rgba(255,255,255,0.7); outline: none;
}}
.psg-item {{ padding: 6px 12px; font-size: 12px; cursor: pointer; }}
.psg-item:hover {{ background: var(--primary-bg); }}
.pg-group-title {{ font-size: 15px; font-weight: 600; margin-bottom: 4px; color: var(--morandi-800); }}
.pg-group-subtitle {{ font-size: 12px; color: var(--morandi-500); margin-bottom: 10px; }}

.filter-search {{
  padding: 6px 12px;
  border: 1px solid var(--morandi-200);
  border-radius: var(--radius-sm);
  font-size: 13px;
  font-family: var(--font);
  outline: none;
  flex: 1;
  min-width: 160px;
  background: rgba(255,255,255,0.7);
  transition: var(--transition);
}}
.filter-search:focus {{ border-color: var(--primary-light); box-shadow: 0 0 0 3px var(--primary-glow); }}
.filter-stats {{
  font-size: 12px;
  color: var(--morandi-500);
  margin-left: auto;
  white-space: nowrap;
  font-weight: 500;
}}

/* ========== VIEW TABS - Pill Navigation ========== */
.view-tabs {{
  display: flex;
  gap: 4px;
  margin-bottom: 20px;
  background: var(--glass-bg);
  backdrop-filter: var(--glass-blur);
  -webkit-backdrop-filter: var(--glass-blur);
  border-radius: var(--radius-xl);
  padding: 4px;
  width: fit-content;
  border: 1px solid var(--glass-border);
  box-shadow: var(--shadow-sm);
  position: relative;
  z-index: 1;
  isolation: isolate;
}}
.view-tab {{
  padding: 8px 20px;
  border: none;
  border-radius: var(--radius-xl);
  font-size: 13px;
  font-family: var(--font);
  cursor: pointer;
  transition: var(--transition);
  background: transparent;
  color: var(--morandi-600);
  font-weight: 500;
  letter-spacing: 0.3px;
}}
.view-tab.active {{
  background: var(--glass-bg-strong);
  color: var(--primary-dark);
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--glass-border);
}}
.view-tab:hover:not(.active) {{
  color: var(--morandi-800);
  background: rgba(255,255,255,0.3);
}}

/* ========== TABLE VIEW ========== */
.table-wrapper {{
  background: var(--glass-bg-strong);
  backdrop-filter: var(--glass-blur);
  -webkit-backdrop-filter: var(--glass-blur);
  border-radius: var(--radius-lg);
  box-shadow: var(--glass-shadow);
  border: 1px solid var(--glass-border);
  overflow-x: auto;
}}
table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
table th, table td {{
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid var(--morandi-100);
  white-space: nowrap;
}}
table th {{
  background: rgba(236,232,240,0.5);
  font-weight: 600;
  color: var(--morandi-700);
  position: sticky;
  top: 0;
  cursor: pointer;
  user-select: none;
  font-size: 12px;
  letter-spacing: 0.3px;
  text-transform: uppercase;
}}
table th:hover {{ color: var(--primary); }}
table th .sort-icon {{ margin-left: 4px; font-size: 10px; opacity: 0.4; }}
table th .sort-icon.active {{ opacity: 1; color: var(--primary); }}
table tr:hover td {{ background: var(--primary-bg); }}
table tr:last-child td {{ border-bottom: none; }}

/* ========== TAGS - Soft Pastels ========== */
.tag {{
  display: inline-block;
  padding: 3px 10px;
  border-radius: var(--radius-xl);
  font-size: 11px;
  font-weight: 500;
  letter-spacing: 0.3px;
}}
.tag-notstarted {{ background: var(--morandi-100); color: var(--morandi-600); }}
.tag-progress {{ background: var(--warning-bg); color: #A07840; }}
.tag-qa {{ background: var(--success-bg); color: #5A8A6A; }}
.region-tag {{
  display: inline-block;
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  font-size: 11px;
  background: var(--morandi-100);
  color: var(--morandi-600);
  margin-right: 2px;
}}
.assignee-name {{ font-weight: 500; color: var(--morandi-700); }}

/* ========== CARD VIEW - Glass Cards ========== */
.card-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
}}
.task-card {{
  background: var(--wash-card);
  backdrop-filter: var(--glass-blur);
  -webkit-backdrop-filter: var(--glass-blur);
  border-radius: var(--radius-lg);
  padding: 18px 20px;
  box-shadow: var(--glass-shadow);
  border: 1px solid var(--glass-border);
  border-left: 4px solid var(--morandi-300);
  transition: var(--transition);
  cursor: default;
  position: relative;
  overflow: hidden;
}}
.task-card::after {{
  content: '';
  position: absolute;
  top: 0; right: 0;
  width: 80px; height: 80px;
  background: radial-gradient(circle at top right, rgba(123,140,222,0.06), transparent 70%);
  pointer-events: none;
}}
.task-card:hover {{
  box-shadow: var(--glass-shadow-hover);
  transform: translateY(-2px);
}}
.task-card.card-notstarted {{ border-left-color: var(--morandi-300); }}
.task-card.card-progress {{ border-left-color: var(--warning); }}
.task-card.card-qa {{ border-left-color: var(--success); }}
.task-card .card-title {{
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 10px;
  line-height: 1.5;
  color: var(--morandi-800);
}}
.task-card .card-meta {{
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  font-size: 12px;
  color: var(--morandi-500);
}}

/* ========== GANTT - Soft Timeline ========== */
.gantt-wrapper {{
  background: var(--glass-bg-strong);
  backdrop-filter: var(--glass-blur);
  -webkit-backdrop-filter: var(--glass-blur);
  border-radius: var(--radius-lg);
  box-shadow: var(--glass-shadow);
  border: 1px solid var(--glass-border);
  padding: 20px;
  overflow-x: auto;
}}
.gantt-container {{ min-width: 100%; position: relative; }}
.gantt-header {{
  display: flex;
  position: sticky;
  top: 0;
  z-index: 10;
  background: rgba(236,232,240,0.8);
  backdrop-filter: blur(10px);
  border-bottom: 2px solid var(--morandi-200);
}}
.gantt-person-col {{
  min-width: 120px; max-width: 120px;
  padding: 10px 12px;
  font-weight: 600; font-size: 13px;
  color: var(--morandi-600);
  border-right: 1px solid var(--morandi-200);
  flex-shrink: 0;
}}
.gantt-timeline {{ flex: 1; display: flex; position: relative; min-height: 36px; }}
.gantt-week-label {{
  flex: 1; text-align: center; padding: 8px 0;
  font-size: 11px; color: var(--morandi-500);
  border-right: 1px solid var(--morandi-100);
  font-weight: 500;
}}
.gantt-week-label.today {{ background: var(--primary-bg); font-weight: 700; color: var(--primary); }}
.gantt-person-group {{ display: flex; border-bottom: 1px solid var(--morandi-100); }}
.gantt-person-group:hover {{ background: rgba(123,140,222,0.03); }}
.gantt-person-name {{
  min-width: 120px; max-width: 120px;
  padding: 10px 12px; font-size: 13px;
  font-weight: 500; color: var(--morandi-700);
  border-right: 1px solid var(--morandi-200);
  flex-shrink: 0;
  display: flex; align-items: center; gap: 4px;
}}
.gantt-person-name .dept-tag {{ font-size: 10px; color: var(--morandi-400); font-weight: 400; }}
.gantt-row-timeline {{ flex: 1; position: relative; min-height: 44px; }}
.gantt-bar {{
  position: absolute; height: 28px;
  border-radius: var(--radius-sm);
  top: 8px; cursor: pointer;
  transition: var(--transition);
  display: flex; align-items: center;
  padding: 0 8px; font-size: 10px;
  color: #fff; font-weight: 500;
  overflow: hidden; text-overflow: ellipsis;
  white-space: nowrap; z-index: 2;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}}
.gantt-bar:hover {{ filter: brightness(1.1); transform: scaleY(1.08); z-index: 5; }}
.gantt-bar.progress-notstarted {{ background: var(--morandi-400); color: var(--morandi-800); }}
.gantt-bar.progress-progress {{ background: var(--warning); }}
.gantt-bar.progress-qa {{ background: var(--success); }}
.gantt-bar.overlap {{
  background-image: repeating-linear-gradient(
    45deg, rgba(255,255,255,0.15) 0px, rgba(255,255,255,0.15) 4px,
    transparent 4px, transparent 8px) !important;
  box-shadow: 0 0 0 2px var(--danger) inset, 0 0 12px rgba(196,139,139,0.3);
  z-index: 4;
}}
.gantt-bar.overlap-double {{ box-shadow: 0 0 0 2px #B07070 inset, 0 0 16px rgba(176,112,112,0.4); }}
.gantt-overlap-badge {{
  display: inline-block; background: var(--danger); color: #fff;
  font-size: 9px; font-weight: 700; padding: 1px 5px;
  border-radius: var(--radius-sm); margin-left: 4px;
}}
.gantt-milestone {{
  position: absolute; width: 10px; height: 10px;
  border-radius: 50%; top: 17px; z-index: 3;
  cursor: pointer; transform: translateX(-50%);
  box-shadow: 0 2px 6px rgba(0,0,0,0.15);
}}
.gantt-milestone.test {{ background: var(--danger); border: 2px solid #fff; }}
.gantt-milestone.freeze {{ background: var(--warning); border: 2px solid #fff; }}
.gantt-milestone.version {{ background: var(--primary); border: 2px solid #fff; }}
.gantt-tooltip {{
  position: fixed;
  background: var(--morandi-900);
  color: var(--morandi-100);
  padding: 12px 16px;
  border-radius: var(--radius-md);
  font-size: 12px; line-height: 1.6;
  z-index: 9999; max-width: 360px;
  pointer-events: none;
  box-shadow: var(--shadow-xl);
  backdrop-filter: blur(10px);
}}
.gantt-tooltip .tt-title {{ font-weight: 600; font-size: 13px; margin-bottom: 6px; }}
.gantt-tooltip .tt-row {{ display: flex; justify-content: space-between; gap: 12px; opacity: 0.85; }}
.gantt-gridlines {{ position: absolute; top: 0; left: 0; right: 0; bottom: 0; z-index: 0; display: flex; }}
.gantt-gridline {{ flex: 1; border-right: 1px dashed var(--morandi-100); }}
.gantt-gridline:last-child {{ border-right: none; }}

/* ========== MODALS - Frosted Glass ========== */
.modal-overlay {{
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(45,37,56,0.4);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  z-index: 200;
  display: none; align-items: center; justify-content: center;
}}
.modal-overlay.active {{ display: flex; }}
.modal {{
  background: var(--glass-bg-strong);
  backdrop-filter: var(--glass-blur-strong);
  -webkit-backdrop-filter: var(--glass-blur-strong);
  border-radius: var(--radius-xl);
  padding: 32px;
  max-width: 520px; width: 90%;
  box-shadow: var(--shadow-xl);
  border: 1px solid var(--glass-border);
  max-height: 90vh; overflow-y: auto;
}}
.modal h2 {{ font-size: 18px; font-weight: 600; margin-bottom: 20px; color: var(--morandi-800); }}
.form-group {{ margin-bottom: 16px; }}
.form-group label {{ display: block; font-size: 12px; font-weight: 600; color: var(--morandi-600); margin-bottom: 6px; letter-spacing: 0.3px; }}
.form-group input, .form-group select, .form-group textarea {{
  width: 100%; padding: 10px 14px;
  border: 1px solid var(--morandi-200);
  border-radius: var(--radius-sm);
  font-size: 13px; font-family: var(--font);
  outline: none; transition: var(--transition);
  background: rgba(255,255,255,0.6);
}}
.form-group input:focus, .form-group select:focus, .form-group textarea:focus {{
  border-color: var(--primary-light);
  box-shadow: 0 0 0 3px var(--primary-glow);
}}
.form-group textarea {{ min-height: 60px; resize: vertical; }}
.form-row {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }}
.form-actions {{ display: flex; gap: 8px; justify-content: flex-end; margin-top: 20px; }}

/* ========== ADMIN TASK LIST ========== */
.admin-task-list {{
  max-height: 300px; overflow-y: auto;
  border: 1px solid var(--morandi-200);
  border-radius: var(--radius-md);
  margin-top: 8px;
}}
.admin-task-item {{
  display: flex; align-items: center; gap: 10px;
  padding: 10px 14px;
  border-bottom: 1px solid var(--morandi-100);
  font-size: 13px;
}}
.admin-task-item:last-child {{ border-bottom: none; }}

/* ========== RESPONSIVE ========== */
.person-view {{ margin-top: 8px; }}
.person-view h3 {{ font-size: 16px; margin-bottom: 12px; }}
.person-stats {{ display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 16px; }}
.person-stat {{ background: var(--glass-bg); padding: 8px 14px; border-radius: var(--radius-sm); font-size: 13px; border: 1px solid var(--glass-border); }}
.person-stat strong {{ color: var(--primary); }}
.person-cards {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 12px; }}
.person-card {{ background: var(--glass-bg); border: 1px solid var(--glass-border); border-radius: var(--radius-md); padding: 12px; }}
.person-card h4 {{ font-size: 14px; margin-bottom: 8px; color: var(--primary); }}
.person-card .pc-stat {{ font-size: 12px; color: var(--morandi-500); margin-bottom: 4px; }}
.person-task {{ font-size: 12px; padding: 3px 0; border-bottom: 1px solid var(--morandi-100); }}
.person-task:last-child {{ border-bottom: none; }}
.person-task .pt-progress {{ display: inline-block; padding: 1px 6px; border-radius: var(--radius-sm); font-size: 10px; margin-left: 6px; }}
.fab {{ position: fixed; bottom: 24px; right: 24px; width: 50px; height: 50px; border-radius: 50%;
  background: var(--primary); color: #fff; border: none; font-size: 24px;
  cursor: pointer; box-shadow: 0 4px 20px rgba(123,140,222,0.35); z-index: 100;
  display: flex; align-items: center; justify-content: center; transition: var(--transition); }}
.fab:hover {{ transform: scale(1.1); box-shadow: 0 6px 28px rgba(123,140,222,0.45); }}
.fab:active {{ transform: scale(0.95); }}

/* ========== PERSON VIEW - Glass Groups ========== */
.person-dept-group {{ margin-bottom:16px; background: var(--glass-bg-strong); backdrop-filter: var(--glass-blur);
  border-radius: var(--radius-lg); box-shadow: var(--glass-shadow); border: 1px solid var(--glass-border); overflow: hidden }}
.person-dept-header {{ background: rgba(236,232,240,0.6); padding:12px 18px; font-size:14px; font-weight:600;
  color: var(--morandi-700); display:flex; align-items:center; gap:8px; letter-spacing: 0.3px; }}
.person-dept-header .dept-count {{ font-weight:400; font-size:12px; color: var(--morandi-400); }}
.person-item {{ display:flex; align-items:flex-start; padding:12px 18px; border-bottom:1px solid var(--morandi-100); transition: var(--transition) }}
.person-item:last-child {{ border-bottom:none }}
.person-item:hover {{ background: var(--primary-bg); }}
.person-avatar {{ width:36px; height:36px; border-radius:50%;
  background: linear-gradient(135deg, var(--primary), var(--morandi-500));
  color:#fff; display:flex; align-items:center; justify-content:center;
  font-size:14px; font-weight:600; flex-shrink:0; margin-right:12px;
  box-shadow: 0 2px 8px rgba(123,140,222,0.2); }}
.person-info {{ flex:1; min-width:0 }}
.person-name {{ font-size:14px; font-weight:600; color: var(--morandi-800); margin-bottom:2px }}
.person-task-count {{ font-size:12px; color: var(--morandi-400); }}
.person-tasks {{ padding-left:48px }}
.person-task-card {{ padding:8px 12px; margin:4px 0; background: var(--morandi-50); border-radius: var(--radius-sm);
  border-left:3px solid var(--morandi-300); font-size:13px; display:flex; align-items:center; gap:8px;
  transition: var(--transition); }}
.person-task-card:hover {{ background: var(--morandi-100); }}
.person-task-card.card-progress {{ border-left-color: var(--warning); }}
.person-task-card.card-notstarted {{ border-left-color: var(--primary); }}
.person-task-card.card-qa {{ border-left-color: var(--success); }}
.person-task-title {{ flex:1; color: var(--morandi-700); }}
.person-task-meta {{ font-size:11px; color: var(--morandi-400); white-space:nowrap; }}
.person-no-tasks {{ padding:6px 12px 6px 48px; font-size:12px; color: var(--morandi-400); font-style:italic; }}

/* ========== FLOATING ADD BUTTON ========== */
.fab-add {{ position:fixed; bottom:28px; right:28px; width:52px; height:52px; border-radius:50%;
  background: linear-gradient(135deg, var(--primary), var(--morandi-600)); color:#fff;
  font-size:28px; font-weight:300; display:flex; align-items:center; justify-content:center;
  cursor:pointer; box-shadow: 0 6px 24px rgba(123,140,222,0.35); z-index:200;
  transition: var(--transition); user-select:none; border: none; }}
.fab-add:hover {{ transform:scale(1.1) rotate(90deg); box-shadow: 0 8px 32px rgba(123,140,222,0.45); }}

/* ========== INLINE ADD TASK PANEL ========== */
.add-task-panel {{ position:fixed; bottom:90px; right:24px; width:380px; max-width:92vw;
  background: var(--glass-bg-strong); backdrop-filter: var(--glass-blur-strong);
  border-radius: var(--radius-xl); box-shadow: var(--shadow-xl);
  z-index:199; overflow:hidden; border: 1px solid var(--glass-border);
  animation: slideUp .3s ease; }}
@keyframes slideUp {{ from{{opacity:0;transform:translateY(20px)}} to{{opacity:1;transform:translateY(0)}} }}
.add-task-header {{ display:flex; align-items:center; justify-content:space-between; padding:14px 18px;
  background: rgba(236,232,240,0.5); font-size:14px; font-weight:600; color: var(--morandi-700); }}
.add-task-close {{ background:none; border:none; font-size:18px; cursor:pointer; color: var(--morandi-500);
  padding:2px 6px; border-radius:4px; transition: var(--transition); }}
.add-task-close:hover {{ background: var(--morandi-100); color: var(--morandi-700); }}
.add-task-body {{ padding:14px 18px 18px; }}
.add-task-row {{ margin-bottom:8px; }}

/* ========== DELETE BUTTON ========== */
.delete-btn {{ background:none; border:none; cursor:pointer; font-size:14px; color: var(--morandi-400);
  padding:2px 6px; border-radius:4px; transition: var(--transition); opacity:.3; flex-shrink:0; }}
.delete-btn:hover {{ color: var(--danger); opacity:1; background: var(--danger-bg); }}
.card-delete {{ position:absolute; top:8px; right:8px; }}
.table-delete {{ padding:2px 8px; }}
.person-task-card .delete-btn {{ opacity:.15; }}
.person-task-card:hover .delete-btn {{ opacity:.5; }}

/* ========== SCROLLBAR ========== */
::-webkit-scrollbar {{ width: 6px; height: 6px; }}
::-webkit-scrollbar-track {{ background: transparent; }}
::-webkit-scrollbar-thumb {{ background: var(--morandi-300); border-radius: 3px; }}
::-webkit-scrollbar-thumb:hover {{ background: var(--morandi-400); }}

/* ========== MOBILE RESPONSIVE ========== */
@media (max-width: 768px) {{
  .header {{ padding: 12px 16px; }}
  .header-inner {{ flex-direction: column; align-items: flex-start; gap: 6px; }}
  .header h1 {{ font-size: 16px; }}
  .header h1 small {{ font-size: 11px; margin-left: 6px; }}
  .header-actions {{ width: 100%; justify-content: space-between; }}
  .container {{ padding: 12px 10px; }}
  .stats-row {{ grid-template-columns: repeat(2, 1fr); gap: 10px; margin-bottom: 14px; }}
  .stat-card {{ padding: 14px 16px; }}
  .stat-card .value {{ font-size: 24px; }}
  .stat-card .label {{ font-size: 11px; }}
  .filter-bar {{ padding: 12px 14px; gap: 8px; }}
  .filter-group {{ flex-wrap: wrap; }}
  .filter-group label {{ font-size: 11px; }}
  .filter-group select {{ min-width: 80px; font-size: 12px; padding: 5px 8px; }}
  .multi-select {{ min-width: 90px; }}
  .multi-select-trigger {{ font-size: 12px; padding: 5px 8px; min-height: 28px; }}
  .multi-select-panel {{ max-height: 200px; }}
  .person-search input {{ min-width: 100px; font-size: 12px; }}
  .filter-search {{ min-width: 100%; font-size: 12px; }}
  .filter-stats {{ margin-left: 0; font-size: 11px; width: 100%; text-align: center; }}
  .view-tabs {{ width: 100%; overflow-x: auto; -webkit-overflow-scrolling: touch; }}
  .view-tabs::-webkit-scrollbar {{ display: none; }}
  .view-tab {{ padding: 7px 14px; font-size: 12px; white-space: nowrap; flex-shrink: 0; }}
  .card-grid {{ grid-template-columns: 1fr; gap: 10px; }}
  .task-card {{ padding: 14px 16px; }}
  .task-card .card-title {{ font-size: 13px; }}
  .task-card .card-meta {{ font-size: 11px; }}
  .table-wrapper {{ font-size: 12px; }}
  table th, table td {{ padding: 8px 10px; font-size: 11px; }}
  .gantt-wrapper {{ padding: 12px; }}
  .gantt-person-col, .gantt-person-name {{ min-width: 80px; max-width: 80px; font-size: 11px; padding: 6px 6px; }}
  .gantt-bar {{ height: 22px; font-size: 9px; top: 8px; }}
  .gantt-week-label {{ font-size: 10px; padding: 4px 0; }}
  .person-cards {{ grid-template-columns: 1fr; }}
  .person-dept-group {{ margin-bottom: 12px; }}
  .person-item {{ padding: 10px 14px; }}
  .person-avatar {{ width: 30px; height: 30px; font-size: 12px; margin-right: 10px; }}
  .person-tasks {{ padding-left: 40px; }}
  .person-task-card {{ padding: 6px 10px; font-size: 12px; }}
  .parent-gantt-wrap .pg-header {{ padding: 10px; }}
  .parent-gantt-wrap .pg-header input {{ min-width: 150px; font-size: 12px; }}
  .fab-add {{ width: 46px; height: 46px; bottom: 20px; right: 16px; font-size: 24px; }}
  .add-task-panel {{ width: calc(100vw - 32px); right: 16px; bottom: 76px; }}
  .modal {{ padding: 20px; margin: 16px; width: calc(100% - 32px); }}
  .modal h2 {{ font-size: 16px; }}
  .form-row {{ grid-template-columns: 1fr; }}
  .delete-btn {{ font-size: 12px; padding: 2px 4px; }}
}}

@media (max-width: 480px) {{
  .header {{ padding: 10px 12px; }}
  .header h1 {{ font-size: 15px; }}
  .header h1 small {{ display: none; }}
  .stats-row {{ grid-template-columns: repeat(2, 1fr); gap: 8px; }}
  .stat-card {{ padding: 12px 14px; border-radius: var(--radius-md); }}
  .stat-card .value {{ font-size: 22px; }}
  .stat-card .label {{ font-size: 10px; }}
  .stat-card .sub {{ display: none; }}
  .filter-bar {{ padding: 10px 12px; gap: 6px; }}
  .view-tab {{ padding: 6px 12px; font-size: 11px; }}
  .container {{ padding: 10px 8px; }}
}}
/* ===== VERSION BADGE ===== */
.version-badge {{
  display: inline-block;
  background: rgba(139, 126, 200, 0.15);
  color: var(--accent-2);
  padding: 1px 8px;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 500;
  margin-left: 4px;
  border: 1px solid rgba(139, 126, 200, 0.2);
}}
.version-filter {{
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  padding: 6px 10px;
  color: var(--text-primary);
  font-size: 12px;
  min-width: 120px;
  cursor: pointer;
  backdrop-filter: blur(8px);
}}
.version-filter:focus {{
  outline: none;
  border-color: var(--accent-1);
  box-shadow: 0 0 0 2px rgba(139, 126, 200, 0.2);
}}

/* ===== JIRA ===== */
.jira-link {{
  display: inline-flex;
  align-items: center;
  gap: 4px;
  color: var(--accent-1);
  text-decoration: none;
  font-size: 11px;
  font-weight: 500;
  padding: 1px 8px;
  border-radius: 10px;
  background: rgba(139, 126, 200, 0.1);
  border: 1px solid rgba(139, 126, 200, 0.15);
  transition: all 0.2s;
  cursor: pointer;
}}
.jira-link:hover {{
  background: rgba(139, 126, 200, 0.2);
  border-color: var(--accent-1);
}}
.jira-status {{
  display: inline-block;
  padding: 0 6px;
  border-radius: 8px;
  font-size: 10px;
  font-weight: 600;
  margin-left: 2px;
}}
.jira-status.todo {{ background: rgba(180,180,180,0.2); color: #888; }}
.jira-status.progress {{ background: rgba(100,149,237,0.15); color: cornflowerblue; }}
.jira-status.done {{ background: rgba(144,238,144,0.15); color: mediumseagreen; }}

/* ===== SAVE VIEW ===== */
.save-view-btn {{
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  padding: 6px 12px;
  color: var(--text-secondary);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
  backdrop-filter: blur(8px);
}}
.save-view-btn:hover {{
  background: rgba(139, 126, 200, 0.15);
  border-color: var(--accent-1);
  color: var(--accent-1);
}}
.saved-views {{
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  align-items: center;
}}
.saved-view-chip {{
  display: inline-flex;
  align-items: center;
  gap: 4px;
  background: rgba(139, 126, 200, 0.12);
  border: 1px solid rgba(139, 126, 200, 0.2);
  border-radius: 12px;
  padding: 3px 10px;
  font-size: 11px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s;
}}
.saved-view-chip:hover {{
  background: rgba(139, 126, 200, 0.22);
  color: var(--accent-1);
}}
.sv-delete {{
  margin-left: 4px;
  opacity: 0.5;
  font-size: 10px;
  cursor: pointer;
}}
.sv-delete:hover {{ opacity: 1; color: #e57373; }}

/* ===== CARD EXPAND ===== */
.task-card {{ cursor: pointer; }}
/* Glass morphism card overlay */
.card-expand-overlay {{
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0,0,0,0.25);
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
  animation: overlayFadeIn 0.2s ease;
}}
@keyframes overlayFadeIn {{
  from {{ opacity: 0; }} to {{ opacity: 1; }}
}}
.card-expand-popup {{
  background: rgba(255,255,255,0.85);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid rgba(255,255,255,0.5);
  border-radius: 20px;
  padding: 32px 36px;
  max-width: 560px;
  width: 90vw;
  max-height: 85vh;
  overflow-y: auto;
  box-shadow: 0 25px 60px rgba(0,0,0,0.12), 0 8px 20px rgba(0,0,0,0.06);
  animation: popupSlideIn 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  position: relative;
}}
@keyframes popupSlideIn {{
  from {{ opacity: 0; transform: translateY(20px) scale(0.96); }}
  to {{ opacity: 1; transform: translateY(0) scale(1); }}
}}
.card-expand-popup .popup-close {{
  position: absolute;
  top: 16px; right: 20px;
  width: 32px; height: 32px;
  border-radius: 50%;
  border: 1px solid rgba(0,0,0,0.08);
  background: rgba(255,255,255,0.6);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  color: #999;
  transition: all 0.2s;
  line-height: 1;
}}
.card-expand-popup .popup-close:hover {{
  background: rgba(0,0,0,0.06);
  color: #555;
}}
.card-expand-popup .popup-title {{
  font-size: 16px;
  font-weight: 700;
  color: var(--morandi-800);
  margin-bottom: 20px;
  padding-right: 40px;
  line-height: 1.5;
}}
.card-expand-popup .popup-meta {{
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 20px;
}}
.card-expand-row {{
  display: flex;
  padding: 8px 0;
  font-size: 13px;
  line-height: 1.6;
  border-bottom: 1px solid rgba(0,0,0,0.04);
}}
.card-expand-label {{
  color: var(--text-muted);
  min-width: 80px;
  flex-shrink: 0;
  font-weight: 500;
}}
.card-expand-value {{
  color: var(--text-secondary);
  word-break: break-all;
}}
.card-expand-value a {{
  color: var(--accent-1);
  text-decoration: none;
}}
.card-expand-value a:hover {{
  text-decoration: underline;
}}

@media (max-width: 768px) {{
  .save-view-btn {{ padding: 5px 8px; font-size: 11px; }}
  .version-filter {{ min-width: 90px; font-size: 11px; }}
  .card-expand-row {{ flex-direction: column; }}
  .card-expand-label {{ min-width: auto; }}
}}

/* ===== JIRA VIEW ===== */
.jira-view-header {{
  padding: 16px;
  background: var(--glass-bg);
  border-radius: 12px;
  border: 1px solid var(--glass-border);
  backdrop-filter: blur(12px);
  margin-bottom: 16px;
}}
.jira-filter-row {{
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: flex-end;
}}
.jira-filter-row .filter-group label {{
  display: block;
  font-size: 11px;
  color: var(--text-muted);
  margin-bottom: 4px;
}}
.jira-filter-row .filter-group select,
.jira-filter-row .filter-group input {{
  background: rgba(255,255,255,0.06);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  padding: 6px 10px;
  color: var(--text-primary);
  font-size: 12px;
  min-width: 140px;
}}
.jira-filter-row .filter-group select:focus,
.jira-filter-row .filter-group input:focus {{
  outline: none;
  border-color: var(--accent-1);
}}
.jira-stats {{
  margin-top: 12px;
  padding: 10px 14px;
  background: rgba(139, 126, 200, 0.08);
  border-radius: 8px;
  font-size: 12px;
  color: var(--text-secondary);
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}}
.jira-stats .stat-item {{
  display: flex;
  align-items: center;
  gap: 6px;
}}
.jira-stats .stat-num {{
  font-weight: 700;
  font-size: 18px;
  color: var(--accent-1);
}}
.jira-stats .stat-label {{
  color: var(--text-muted);
  font-size: 11px;
}}
.jira-table-wrap {{
  background: var(--glass-bg);
  border-radius: 12px;
  border: 1px solid var(--glass-border);
  backdrop-filter: blur(12px);
  overflow-x: auto;
}}
.jira-table {{
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
}}
.jira-table th {{
  position: sticky;
  top: 0;
  background: rgba(139, 126, 200, 0.1);
  padding: 10px 12px;
  text-align: left;
  font-weight: 600;
  color: var(--text-secondary);
  border-bottom: 1px solid var(--glass-border);
  white-space: nowrap;
  z-index: 1;
}}
.jira-table td {{
  padding: 8px 12px;
  border-bottom: 1px solid rgba(255,255,255,0.04);
  color: var(--text-secondary);
  vertical-align: middle;
}}
.jira-table tr:hover td {{
  background: rgba(139, 126, 200, 0.05);
}}
.jira-table .jira-key-cell a {{
  color: var(--accent-1);
  text-decoration: none;
  font-weight: 500;
}}
.jira-table .jira-key-cell a:hover {{
  text-decoration: underline;
}}
.jira-person-badge {{
  display: inline-block;
  padding: 1px 8px;
  border-radius: 10px;
  font-size: 11px;
  background: rgba(139, 126, 200, 0.12);
  color: var(--text-secondary);
  margin: 1px 2px;
}}
.jira-progress-tag {{
  display: inline-block;
  padding: 2px 8px;
  border-radius: 8px;
  font-size: 11px;
  font-weight: 500;
}}
.jira-progress-tag.todo {{ background: rgba(180,180,180,0.15); color: #999; }}
.jira-progress-tag.progress {{ background: rgba(100,149,237,0.12); color: cornflowerblue; }}
.jira-progress-tag.done {{ background: rgba(144,238,144,0.12); color: mediumseagreen; }}
.jira-progress-tag.blocked {{ background: rgba(239,83,80,0.12); color: #ef5350; }}
.jira-empty {{
  padding: 40px;
  text-align: center;
  color: var(--text-muted);
  font-size: 13px;
}}

@media (max-width: 768px) {{
  .jira-filter-row {{ flex-direction: column; }}
  .jira-filter-row .filter-group select,
  .jira-filter-row .filter-group input {{ width: 100%; }}
  .jira-stats {{ flex-direction: column; gap: 8px; }}
}}
</style>
</head>
<body>

<!-- ========== HEADER ========== -->
<div class="header">
  <div class="header-inner">
    <h1>ROX \u9879\u76ee\u6392\u671f\u770b\u677f <small>\u5f00\u53d1\u9636\u6bb5</small></h1>
    <div class="header-actions">
      <button class="btn btn-outline btn-sm" id="adminBtn" onclick="openAdminModal()">0̇0̇ 管理员</button>
      <span style="font-size:12px;opacity:0.7" id="headerInfo"></span>
    </div>
  </div>
</div>

<!-- ========== CONTAINER ========== -->
<div class="container">
  <!-- Stats Cards -->
  <div class="stats-row" id="statsRow"></div>

  <!-- Filter Bar -->
  <div class="filter-bar" id="filterBar">
    <!-- Region multi-select -->
    <div class="filter-group">
      <label>\u5730\u533a</label>
      <div class="multi-select" id="msRegion">
        <div class="multi-select-trigger" onclick="toggleMsPanel('region')">
          <span class="ms-count"></span><span class="ms-label">\u5168\u90e8</span>
          <span class="ms-arrow">\u25bc</span>
        </div>
        <div class="multi-select-panel" id="msPanel_region" style="display:none">
          <label><input type="checkbox" data-all="region" checked onchange="toggleMsAll('region')"> \u5168\u90e8</label>
          <div id="msCheckboxes_region"></div>
        </div>
      </div>
      <input type="hidden" id="filterRegion" value="ALL">
    </div>
    <!-- Progress multi-select -->
    <div class="filter-group">
      <label>\u8fdb\u5c55</label>
      <div class="multi-select" id="msProgress">
        <div class="multi-select-trigger" onclick="toggleMsPanel('progress')">
          <span class="ms-count"></span><span class="ms-label">\u5168\u90e8</span>
          <span class="ms-arrow">\u25bc</span>
        </div>
        <div class="multi-select-panel" id="msPanel_progress" style="display:none">
          <label><input type="checkbox" data-all="progress" checked onchange="toggleMsAll('progress')"> \u5168\u90e8</label>
          <div id="msCheckboxes_progress"></div>
        </div>
      </div>
      <input type="hidden" id="filterProgress" value="ALL">
    </div>
    <!-- Department multi-select -->
    <div class="filter-group">
      <label>\u90e8\u95e8</label>
      <div class="multi-select" id="msDept">
        <div class="multi-select-trigger" onclick="toggleMsPanel('dept')">
          <span class="ms-count"></span><span class="ms-label">\u5168\u90e8</span>
          <span class="ms-arrow">\u25bc</span>
        </div>
        <div class="multi-select-panel" id="msPanel_dept" style="display:none">
          <label><input type="checkbox" data-all="dept" checked onchange="toggleMsAll('dept')"> \u5168\u90e8</label>
          <div id="msCheckboxes_dept"></div>
        </div>
      </div>
      <input type="hidden" id="filterDept" value="ALL">
    </div>
    <!-- Person search + multi-select -->
    <div class="filter-group">
      <label>\u6267\u884c\u4eba</label>
      <div class="person-search">
        <input type="text" id="filterPersonSearch" placeholder="\u641c\u7d22\u59d3\u540d..." oninput="onPersonSearch(this.value)" onfocus="onPersonSearch(this.value)" onblur="setTimeout(function(){{ document.getElementById('psResults').style.display='none'; }},200)" autocomplete="off">
        <div class="ps-results" id="psResults"></div>
      </div>
      <div class="multi-select" id="msPerson" style="min-width:80px">
        <div class="multi-select-trigger" onclick="toggleMsPanel('person')">
          <span class="ms-count"></span><span class="ms-label">\u5168\u90e8</span>
          <span class="ms-arrow">\u25bc</span>
        </div>
        <div class="multi-select-panel" id="msPanel_person" style="display:none">
          <label><input type="checkbox" data-all="person" checked onchange="toggleMsAll('person')"> \u5168\u90e8</label>
          <div style="max-height:300px;overflow-y:auto" id="msCheckboxes_person"></div>
        </div>
      </div>
      <input type="hidden" id="filterPerson" value="ALL">
    </div>
    <div class="filter-group">
      <label>\u7248\u672c</label>
      <select id="filterVersion" onchange="applyFilters()" class="version-filter">
        <option value="ALL">\u5168\u90e8\u7248\u672c</option>
      </select>
    </div>
    <div class="filter-group">
      <label>\u641c\u7d22</label>
      <input type="text" class="filter-search" id="filterSearch" placeholder="\u641c\u7d22\u5de5\u4f5c\u5185\u5bb9..." oninput="applyFilters()">
    </div>
    <div class="filter-group">
      <button class="save-view-btn" onclick="saveCurrentView()">\U0001F4BE \u4fdd\u5b58\u89c6\u56fe</button>
    </div>
    <div class="saved-views" id="savedViewsBar"></div>
    <div class="filter-stats" id="filterStats"></div>
  </div>

  <!-- View Tabs -->
  <div class="view-tabs">
    <button class="view-tab active" data-view="card" onclick="switchView('card')">\u5361\u7247\u89c6\u56fe</button>
    <button class="view-tab" data-view="person" onclick="switchView('person')">\u4eba\u5458\u89c6\u56fe</button>
    <button class="view-tab" data-view="table" onclick="switchView('table')">\u8868\u683c\u89c6\u56fe</button>
    <button class="view-tab" data-view="gantt" onclick="switchView('gantt')">\u7518\u7279\u56fe</button>
    <button class="view-tab" data-view="parentgantt" onclick="switchView('parentgantt')">\u5b50\u4efb\u52a1\u7518\u7279</button>
    <button class="view-tab" data-view="jira" onclick="switchView('jira')">Jira\u5173\u8054</button>
  </div>

  <!-- Content Area -->
  <div id="cardView" class="fade-in"></div>
  <div id="personView" class="fade-in" style="display:none">
    <div class="person-view" id="personViewInner"></div>
  </div>
  <div id="tableView" class="fade-in" style="display:none"></div>
  <div id="ganttView" class="fade-in" style="display:none"></div>
  <div id="parentGanttView" class="fade-in parent-gantt-wrap" style="display:none">
    <div class="pg-header">
      <input type="text" id="pgSearch" placeholder="\u641c\u7d22\u4efb\u52a1\uff0c\u67e5\u770b\u540c\u7248\u672c\u6240\u6709\u4efb\u52a1\u6392\u671f\u7518\u7279\u56fe..." oninput="onPgSearch(this.value)" autocomplete="off">
      <div class="ps-results" id="pgSuggest"></div>
    </div>
    <div id="pgResult"></div>
  </div>
  <div id="jiraView" class="fade-in" style="display:none">
    <div class="jira-view-header">
      <div class="jira-filter-row">
        <div class="filter-group">
          <label>\u6267\u884c\u4eba</label>
          <select id="jiraPersonFilter" onchange="renderJiraView()">
            <option value="ALL">\u5168\u90e8\u4eba\u5458</option>
          </select>
        </div>
        <div class="filter-group">
          <label>\u5916\u653e\u7248\u672c</label>
          <select id="jiraVersionFilter" onchange="renderJiraView()">
            <option value="ALL">\u5168\u90e8\u7248\u672c</option>
          </select>
        </div>
        <div class="filter-group">
          <label>\u641c\u7d22</label>
          <input type="text" id="jiraSearchInput" placeholder="\u641c\u7d22\u4efb\u52a1\u6216Jira\u5355\u53f7..." oninput="renderJiraView()">
        </div>
      </div>
      <div class="jira-stats" id="jiraStats"></div>
    </div>
    <div class="jira-table-wrap" id="jiraTableWrap"></div>
  </div>
</div>

<!-- ========== ADMIN TASK MODAL ========== -->
<div class="modal-overlay" id="adminModalOverlay">
  <div class="modal" id="adminModal">
    <h2>\U0001F4DD \u4efb\u52a1\u7ba1\u7406</h2>
    <div id="adminTasksList" class="admin-task-list"></div>
    <hr style="border:none;border-top:1px solid var(--gray-3);margin:10px 0">
    <h3 style="font-size:14px;font-weight:600;margin-bottom:12px">\u6dfb\u52a0\u65b0\u4efb\u52a1</h3>
    <div class="form-group">
      <label>\u5de5\u4f5c\u5185\u5bb9</label>
      <textarea id="newTaskTitle" placeholder="\u8f93\u5165\u4efb\u52a1\u63cf\u8ff0..."></textarea>
    </div>
    <div class="form-row">
      <div class="form-group">
        <label>\u5de5\u65f6\uff08\u5929\uff09</label>
        <input type="number" id="newTaskHours" min="0.5" step="0.5" value="1">
      </div>
      <div class="form-group">
        <label>\u4f18\u5148\u7ea7</label>
        <select id="newTaskPriority">
          <option value="P0">P0</option>
          <option value="P2" selected>P2</option>
        </select>
      </div>
    </div>
    <div class="form-group">
      <label>\u6267\u884c\u4eba</label>
      <select id="newTaskPerson"></select>
    </div>
    <div class="form-group">
      <label>\u622a\u6b62\u65e5\u671f</label>
      <input type="date" id="newTaskDeadline">
    </div>
    <div class="form-group">
      <label>\u5730\u533a</label>
      <select id="newTaskRegion">
        <option value="\u56fd\u670d">\u56fd\u670d</option>
        <option value="\u7f8e\u670d">\u7f8e\u670d</option>
        <option value="\u65e5\u670d">\u65e5\u670d</option>
        <option value="\u6b27\u670d">\u6b27\u670d</option>
      </select>
    </div>
    <div id="scheduleResult" class="schedule-result"></div>
    <div class="form-actions">
      <button class="btn btn-success" onclick="addAdminTask()">\u6dfb\u52a0\u5e76\u6392\u671f</button>
      <button class="btn btn-outline" style="color:var(--gray-6);border-color:var(--gray-3)" onclick="closeAdminModal()">\u5173\u95ed</button>
    </div>
  </div>
</div>


<!-- ========== FLOATING ADD BUTTON ========== -->
<div class="fab-add" id="fabAddBtn" onclick="toggleAddForm()" title="添加任务">+</div>

<!-- ========== INLINE ADD TASK FORM ========== -->
<div class="add-task-panel" id="addTaskPanel" style="display:none">
  <div class="add-task-header">
    <span>➕ 添加新任务</span>
    <button class="add-task-close" onclick="toggleAddForm()">✖</button>
  </div>
  <div class="add-task-body">
    <div class="add-task-row">
      <textarea id="addTaskTitle" placeholder="输入任务描述..." rows="2" style="width:100%;padding:8px 10px;border:1.5px solid var(--gray-3);border-radius:8px;font-size:13px;"></textarea>
    </div>
    <div class="add-task-row" style="display:flex;gap:8px;flex-wrap:wrap">
      <select id="addTaskPerson" style="flex:1;min-width:120px;padding:7px 8px;border:1.5px solid var(--gray-3);border-radius:8px;font-size:13px;"><option value="">选择执行人</option></select>
      <input type="number" id="addTaskHours" value="1" min="0.5" step="0.5" style="width:70px;padding:7px 8px;border:1.5px solid var(--gray-3);border-radius:8px;font-size:13px;text-align:center" title="工时（天）">
      <select id="addTaskRegion" style="width:80px;padding:7px 8px;border:1.5px solid var(--gray-3);border-radius:8px;font-size:13px;">
        <option value="">地区</option>
        <option value="国服">国服</option>
        <option value="日服">日服</option>
        <option value="美服">美服</option>
        <option value="欧服">欧服</option>
      </select>
      <input type="date" id="addTaskDeadline" style="padding:7px 8px;border:1.5px solid var(--gray-3);border-radius:8px;font-size:13px;">
    </div>
    <div class="add-task-row" style="display:flex;gap:8px;margin-top:8px">
      <button class="btn btn-primary-solid" onclick="submitAddTask()" style="flex:1">➕ 添加并排期</button>
      <button class="btn btn-outline" onclick="toggleAddForm()" style="color:var(--gray-6);border-color:var(--gray-3)">取消</button>
    </div>
    <div id="addTaskResult" class="schedule-result" style="margin-top:8px"></div>
  </div>
</div>
<!-- ========== GANTT TOOLTIP ========== -->
<div class="gantt-tooltip" id="ganttTooltip"></div>

<!-- ========== DATA EMBEDDED AS JSON ========== -->
<script id="__DATA__" type="application/json">{data_json_safe}</script>
<script id="__PEOPLE__" type="application/json">{people_json_safe}</script>
<script id="__VER_MAP__" type="application/json">{ver_map_json_safe}</script>

<!-- ========== APPLICATION SCRIPT ========== -->
<script>
// ======================== DATA LOADING ========================
var DATA = JSON.parse(document.getElementById('__DATA__').textContent);
var ALL_PEOPLE = JSON.parse(document.getElementById('__PEOPLE__').textContent);
var VER_NAME_MAP = JSON.parse(document.getElementById('__VER_MAP__').textContent);


// ======================== STATE ========================
var currentView = 'card';
var sortField = null;
var sortDir = 'asc';
var adminMode = false; // true if logged in as admin
var adminTasks = [];
var allRegions = [];
var allProgress = [];
var allPeople = [];

// ======================== ADMIN TASKS ========================
function loadAdminTasks() {{
  try {{
    adminTasks = JSON.parse(localStorage.getItem('rox_admin_tasks') || '[]');
  }} catch(e) {{ adminTasks = []; }}
}}

function saveAdminTasks() {{
  localStorage.setItem('rox_admin_tasks', JSON.stringify(adminTasks));
}}

// ======================== DATA PROCESSING ========================
function normalizeDate(d) {{
  if (!d) return null;
  var s = String(d).replace(' 00:00:00','').trim();
  if (s.length <= 10) return s;
  return s.substring(0,10);
}}

function parseDate(s) {{
  if (!s) return null;
  var d = new Date(s);
  if (isNaN(d.getTime())) return null;
  return d;
}}

function getWeekNumber(d) {{
  var year = d.getFullYear();
  var firstJan = new Date(year, 0, 1);
  var days = Math.floor((d - firstJan) / (86400000));
  return Math.ceil((days + firstJan.getDay() + 1) / 7);
}}

function getMonday(d) {{
  var day = d.getDay();
  var diff = d.getDate() - day + (day === 0 ? -6 : 1);
  var m = new Date(d);
  m.setDate(diff);
  m.setHours(0,0,0,0);
  return m;
}}

function formatDate(d) {{
  return d.getFullYear() + '/' + String(d.getMonth()+1).padStart(2,'0') + '/' + String(d.getDate()).padStart(2,'0');
}}

function formatDateISO(d) {{
  return d.getFullYear() + '-' + String(d.getMonth()+1).padStart(2,'0') + '-' + String(d.getDate()).padStart(2,'0');
}}

// ======================== INIT ========================
function init() {{
  // Extract filter options
  var regionSet = {{}}, progSet = {{}}, personSet = {{}};
  DATA.forEach(function(r) {{
    if (r.region) r.region.forEach(function(x) {{ regionSet[x] = true; }});
    if (r.progress) progSet[r.progress] = true;
    if (r.assignee) r.assignee.forEach(function(p) {{ personSet[p.name] = true; }});
  }});
  allRegions = Object.keys(regionSet).sort();
  var progOrder = ['\u672a\u542f\u52a8', '\u8fdb\u884c\u4e2d', 'QA\u9a8c\u6536\u4e2d'];
  allProgress = progOrder.filter(function(p) {{ return progSet[p]; }});
  if (allProgress.length === 0) allProgress = Object.keys(progSet);
  allPeople = ALL_PEOPLE.map(function(p) {{ return p.name; }});

  // Populate multi-select checkboxes
  msPopulate('region', allRegions, allRegions);

  // Progress: add empty option
  if (progSet['']) allProgress.unshift('(\u7a7a)');
  msPopulate('progress', allProgress, allProgress);

  // Department
  var deptMap = {{}}, deptList = [];
  ALL_PEOPLE.forEach(function(p) {{
    if (p.dept && !deptMap[p.dept]) {{ deptMap[p.dept] = true; deptList.push(p.dept); }}
  }});
  deptList.sort();
  msPopulate('dept', deptList, deptList);

  // Person: by dept groups
  var sortedDepts2 = Object.keys(deptMap).sort();
  var personOpts = [];
  sortedDepts2.forEach(function(d) {{
    ALL_PEOPLE.filter(function(p) {{ return p.dept === d; }})
      .sort(function(a,b) {{ return a.name.localeCompare(b.name); }})
      .forEach(function(p) {{ personOpts.push(p.name); }});
  }});
  msPopulate('person', personOpts, personOpts);

  // Init person search data
  _psData = ALL_PEOPLE.map(function(p) {{ return {{ name: p.name, dept: p.dept, label: p.dept + ' - ' + p.name }}; }});

  // Populate admin form person select (same grouped list)
  var selAP = document.getElementById('newTaskPerson');
  sortedDepts2.forEach(function(dept) {{
    var og = document.createElement('optgroup');
    og.label = dept;
    ALL_PEOPLE.filter(function(p) {{ return p.dept === dept; }})
      .sort(function(a,b) {{ return a.name.localeCompare(b.name); }})
      .forEach(function(p) {{
        var o = document.createElement('option');
        o.value = p.name; o.textContent = dept + ' - ' + p.name;
        og.appendChild(o);
      }});
    selAP.appendChild(og);
  }});

  // Set default deadline to 7 days from now
  var dl = document.getElementById('newTaskDeadline');
  var f = new Date(); f.setDate(f.getDate() + 7); dl.value = formatDateISO(f);

  // Init versions
  initVersions();
  renderSavedViews();

  document.getElementById('headerInfo').textContent = DATA.length + ' \u4e2a\u4efb\u52a1 | ' + allPeople.length + ' \u4eba';

  // Close multi-select panels on outside click
  document.addEventListener('click', function(e) {{
    var hit = false;
    ['region','progress','dept','person'].forEach(function(k) {{
      var el = document.getElementById('ms' + k.charAt(0).toUpperCase() + k.slice(1));
      if (el && el.contains(e.target)) hit = true;
    }});
    if (!hit) {{
      document.querySelectorAll('.multi-select-panel').forEach(function(p) {{ p.style.display = 'none'; }});
    }}
  }});

  render();
}}

// ======================== FILTER ========================
function getFilteredData() {{
  var regionVal = document.getElementById('filterRegion').value;
  var progressVal = document.getElementById('filterProgress').value;
  var deptVal = document.getElementById('filterDept').value;
  var personVal = document.getElementById('filterPerson').value;
  var search = document.getElementById('filterSearch').value.trim().toLowerCase();

  var regions = regionVal === 'ALL' ? [] : regionVal.split(',');
  var progressFilter = progressVal === 'ALL' ? [] : progressVal.split(',');
  var depts = deptVal === 'ALL' ? [] : deptVal.split(',');
  var persons = personVal === 'ALL' ? [] : personVal.split(',');

  var filtered = DATA.filter(function(r) {{
    if (regions.length > 0) {{
      if (!r.region || !regions.some(function(x) {{ return r.region.indexOf(x) >= 0; }})) return false;
    }}
    if (progressFilter.length > 0) {{
      if (!progressFilter.some(function(x) {{
        if (x === '(\u7a7a)') return !r.progress;
        return r.progress === x;
      }})) return false;
    }}
    if (depts.length > 0) {{
      var rDepts = [];
      if (r.assignee) r.assignee.forEach(function(p) {{
        ALL_PEOPLE.forEach(function(ap) {{ if (ap.name === p.name && ap.dept) rDepts.push(ap.dept); }});
      }});
      if (!depts.some(function(d) {{ return rDepts.indexOf(d) >= 0; }})) return false;
    }}
    if (persons.length > 0) {{
      if (!r.assignee || !r.assignee.some(function(p) {{ return persons.indexOf(p.name) >= 0; }})) return false;
    }}
    if (search && !fuzzyMatch(r.title, search)) return false;
    var versionVal = (document.getElementById('filterVersion') || {{}}).value || 'ALL';
    if (versionVal !== 'ALL') {{
      var vn = VER_NAME_MAP[r.extVersion] || r.extVersion;
      if (vn !== versionVal) return false;
    }}
    return true;
  }});

  var adminFiltered = adminTasks.filter(function(t) {{
    if (regions.length > 0 && regions.indexOf(t.region) === -1) return false;
    if (progressFilter.length > 0) {{
      var tp = t.progress;
      if (!progressFilter.some(function(x) {{ return x === '(\u7a7a)' ? !tp : tp === x; }})) return false;
    }}
    if (depts.length > 0) {{
      var td = null;
      ALL_PEOPLE.forEach(function(ap) {{ if (ap.name === t.assigneeName && ap.dept) td = ap.dept; }});
      if (depts.indexOf(td) === -1) return false;
    }}
    if (persons.length > 0 && persons.indexOf(t.assigneeName) === -1) return false;
    if (search && !fuzzyMatch(t.title, search)) return false;
    return true;
  }});

  return {{ records: filtered, adminTasks: adminFiltered }};
}}

function render() {{
  var result = getFilteredData();
  var filtered = result.records;
  var adminFiltered = result.adminTasks;

  renderStats(filtered, adminFiltered);
  document.getElementById('filterStats').textContent = '\\u5df2\\u7b5b\\u9009 ' + (filtered.length + adminFiltered.length) + ' / ' + (DATA.length + adminTasks.length) + ' \\u4e2a\\u4efb\\u52a1';

  if (currentView === 'person') renderPersonView();
  else if (currentView === 'card') renderCard(filtered, adminFiltered);
  else if (currentView === 'table') renderTable(filtered, adminFiltered);
  else if (currentView === 'gantt') renderGantt(filtered, adminFiltered);
  else if (currentView === 'parentgantt') renderParentGantt(filtered, adminFiltered);
}}

function applyFilters() {{
  if (currentView === 'person') renderPersonView();
  else render();
}}

// ======================== STATS ========================
function renderStats(filtered, adminFiltered) {{
  var total = filtered.length + adminFiltered.length;
  var inProgress = filtered.filter(function(r) {{ return r.progress === '\\u8fdb\\u884c\\u4e2d'; }}).length +
    adminFiltered.filter(function(t) {{ return t.progress === '\\u8fdb\\u884c\\u4e2d'; }}).length;
  var notStarted = filtered.filter(function(r) {{ return r.progress === '\\u672a\\u542f\\u52a8'; }}).length +
    adminFiltered.filter(function(t) {{ return t.progress === '\\u672a\\u542f\\u52a8'; }}).length;
  var qaCount = filtered.filter(function(r) {{ return r.progress === 'QA\\u9a8c\\u6536\\u4e2d'; }}).length +
    adminFiltered.filter(function(t) {{ return t.progress === 'QA\\u9a8c\\u6536\\u4e2d'; }}).length;

  // Unique people
  var personSet = {{}};
  filtered.forEach(function(r) {{
    if (r.assignee) r.assignee.forEach(function(p) {{ personSet[p.name] = true; }});
  }});
  adminFiltered.forEach(function(t) {{ if (t.assigneeName) personSet[t.assigneeName] = true; }});
  var peopleCount = Object.keys(personSet).length;

  var cards = [
    {{ label: '\\u603b\\u4efb\\u52a1\\u6570', value: total, sub: '\\u5f53\\u524d\\u6392\\u671f' }},
    {{ label: '\\u8fdb\\u884c\\u4e2d', value: inProgress, sub: '\\u6267\\u884c\\u4e2d\\u4efb\\u52a1' }},
    {{ label: '\\u672a\\u542f\\u52a8', value: notStarted, sub: '\\u5f85\\u542f\\u52a8\\u4efb\\u52a1' }},
    {{ label: 'QA\\u9a8c\\u6536\\u4e2d', value: qaCount, sub: '\\u7b49\\u5f85\\u9a8c\\u6536' }},
    {{ label: '\\u6d89\\u53ca\\u4eba\\u5458', value: peopleCount, sub: '\\u5f53\\u524d\\u7b5b\\u9009' }},
    {{ label: '\\u56e2\\u961f\\u6210\\u5458', value: ALL_PEOPLE.length, sub: '\\u5168\\u90e8\\u4eba\\u5458' }}
  ];

  document.getElementById('statsRow').innerHTML = cards.map(function(c) {{
    return '<div class="stat-card"><div class="label">' + c.label + '</div><div class="value">' + c.value + '</div><div class="sub">' + c.sub + '</div></div>';
  }}).join('');
}}

// ======================== CARD VIEW ========================
function renderCard(filtered, adminFiltered) {{
  var html = '<div class="card-grid">';
  filtered.forEach(function(r) {{
    var cls = 'card-notstarted';
    if (r.progress === '\\u8fdb\\u884c\\u4e2d') cls = 'card-progress';
    else if (r.progress === 'QA\\u9a8c\\u6536\\u4e2d') cls = 'card-qa';
    var pTag = r.progress === '\\u672a\\u542f\\u52a8' ? '<span class="tag tag-notstarted">\\u672a\\u542f\\u52a8</span>' :
      r.progress === '\\u8fdb\\u884c\\u4e2d' ? '<span class="tag tag-progress">\\u8fdb\\u884c\\u4e2d</span>' :
      '<span class="tag tag-qa">' + r.progress + '</span>';
    var regionTags = (r.region || []).map(function(x) {{ return '<span class="region-tag">' + x + '</span>'; }}).join('');
    var names = (r.assignee || []).map(function(p) {{ return p.name; }}).join(', ');
    var dates = [];
        if (r.startDate) dates.push('\\u{{1F4C5}} 启动: ' + normalizeDate(r.startDate));
        if (r.endDate) dates.push('\\u23F0 结束: ' + normalizeDate(r.endDate));
    if (r.freezeDate) dates.push('\\u{{1F4C4}} \\u5c01\\u677f: ' + r.freezeDate);
    if (r.versionDate) dates.push('\\u{{1F4C5}} \\u7248\\u66f4: ' + r.versionDate);

    var jiraHtml = renderJiraHtml(r);
    var verHtml = renderVersionHtml(r);
    html += '<div class="task-card ' + cls + '" data-id="' + r.id + '">';
    html += '<div class="card-title">' + escapeHtml(r.title) + verHtml + '</div>';
    html += '<div class="card-meta">' + pTag + regionTags + (jiraHtml ? ' ' + jiraHtml : '') + '</div>';
    html += '<div class="card-meta" style="margin-top:4px"><span>\\u{{1F465}} ' + escapeHtml(names) + '</span></div>';
    if (dates.length) html += '<div class="card-meta" style="margin-top:4px">' + dates.join(' | ') + '</div>';
    html += '<div class="card-expand" id="card-expand-' + r.id + '" style="display:none">';
    html += buildCardExpandHtml(r);
    html += '</div>';
    html += '</div>';
  }});

  // Admin tasks
  adminFiltered.forEach(function(t) {{
    var pTag = t.progress === '\\u672a\\u542f\\u52a8' ? '<span class="tag tag-notstarted">\\u672a\\u542f\\u52a8</span>' :
      t.progress === '\\u8fdb\\u884c\\u4e2d' ? '<span class="tag tag-progress">\\u8fdb\\u884c\\u4e2d</span>' : '';
    var prio = '<span class="priority-high">' + (t.priority || 'P2') + '</span>';
    html += '<div class="task-card card-progress">';
    html += '<div class="card-title">' + escapeHtml(t.title) + '</div>';
    html += '<div class="card-meta">' + pTag + ' <span class="region-tag">' + escapeHtml(t.region) + '</span> ' + prio + '</div>';
    html += '<div class="card-meta" style="margin-top:4px"><span>\\u{{1F465}} ' + escapeHtml(t.assigneeName) + '</span></div>';
    html += '<div class="card-meta" style="margin-top:4px"><span>\\u23F0 \\u6392\\u671f: ' + escapeHtml(t.scheduledStart) + ' ~ ' + escapeHtml(t.scheduledEnd) + '</span></div>';
    html += '</div>';
  }});

  if (!filtered.length && !adminFiltered.length) {{
    html = '<div class="empty-state"><span class="empty-icon">\\u{{1F4C4}}</span><div>\\u6682\\u65e0\\u5339\\u914d\\u7684\\u4efb\\u52a1</div></div>';
  }}
  document.getElementById('cardView').innerHTML = html + '</div>';
}}

// ======================== TABLE VIEW ========================
function renderTable(filtered, adminFiltered) {{
  var all = filtered.concat(adminFiltered.map(function(t) {{
    return {{
      title: t.title + ' \\u{{1F517}}',
      progress: t.progress,
      testDate: '',
      freezeDate: t.scheduledEnd || '',
      versionDate: '',
      onlineDate: null,
      startDate: t.scheduledStart || '',
      endDate: t.scheduledEnd || '',
      assignee: [{{ name: t.assigneeName }}],
      region: [t.region],
      id: '_admin_' + Date.now(),
      _priority: t.priority,
      _isAdmin: true
    }};
  }}));

  // Sort
  if (sortField) {{
    all.sort(function(a, b) {{
      var va = a[sortField], vb = b[sortField];
      if (sortField === 'assignee') {{
        va = (a.assignee && a.assignee[0]) ? a.assignee[0].name : '';
        vb = (b.assignee && b.assignee[0]) ? b.assignee[0].name : '';
      }}
      if (sortField === 'region') {{
        va = (a.region && a.region[0]) ? a.region[0] : '';
        vb = (b.region && b.region[0]) ? b.region[0] : '';
      }}
      if (typeof va === 'string') va = va.toLowerCase();
      if (typeof vb === 'string') vb = vb.toLowerCase();
      if (va < vb) return sortDir === 'asc' ? -1 : 1;
      if (va > vb) return sortDir === 'asc' ? 1 : -1;
      return 0;
    }});
  }}

  var cols = [
    {{ key: 'title', label: '\\u5de5\\u4f5c\\u5185\\u5bb9', width: '300px' }},
    {{ key: 'progress', label: '\\u8fdb\\u5c55', width: '80px' }},
    {{ key: 'assignee', label: '\\u6267\\u884c\\u4eba', width: '100px' }},
    {{ key: 'region', label: '\\u5730\\u533a', width: '80px' }},
    {{ key: 'startDate', label: '\\u542f\\u52a8\\u65e5\\u671f', width: '110px' }},
    {{ key: 'endDate', label: '\u4efb\u52a1\u7ed3\u675f', width: '110px' }},
    {{ key: 'freezeDate', label: '\\u5c01\\u677f\\u65f6\\u95f4', width: '110px' }},
    {{ key: 'versionDate', label: '\\u7248\\u66f4\\u65f6\\u95f4', width: '110px' }},
    {{ key: 'extVersion', label: '\\u5916\\u653e\\u7248\\u672c', width: '130px' }},
    {{ key: 'jiraKey', label: 'Jira\\u5355\\u53f7', width: '130px' }}
  ];

  function sortIcon(k) {{
    if (sortField !== k) return '<span class="sort-icon">\\u25B2</span>';
    return '<span class="sort-icon active">' + (sortDir === 'asc' ? '\\u25B2' : '\\u25BC') + '</span>';
  }}

  var html = '<div class="table-wrapper"><table><thead><tr>';
  cols.forEach(function(c) {{
    html += '<th style="min-width:' + c.width + '" onclick="sortBy(\\'' + c.key + '\\')">' + c.label + sortIcon(c.key) + '</th>';
  }});
  html += '</tr></thead><tbody>';

  all.forEach(function(r) {{
    var pTag = r.progress === '\\u672a\\u542f\\u52a8' ? '<span class="tag tag-notstarted">\\u672a\\u542f\\u52a8</span>' :
      r.progress === '\\u8fdb\\u884c\\u4e2d' ? '<span class="tag tag-progress">\\u8fdb\\u884c\\u4e2d</span>' :
      '<span class="tag tag-qa">' + r.progress + '</span>';
    var names = (r.assignee || []).map(function(p) {{ return '<span class="assignee-name">' + escapeHtml(p.name) + '</span>'; }}).join(', ');
    var regionTags = (r.region || []).map(function(x) {{ return '<span class="region-tag">' + escapeHtml(x) + '</span>'; }}).join('');
    var prioHtml = '';
    if (r._isAdmin) {{
      prioHtml = ' <span class="priority-high">\\u2605 ' + (r._priority || '') + '</span>';
    }}
    html += '<tr><td style="max-width:300px;overflow:hidden;text-overflow:ellipsis;white-space:normal;word-break:break-all">' + escapeHtml(r.title) + prioHtml + '</td>';
    html += '<td>' + pTag + '</td>';
    html += '<td>' + names + '</td>';
    html += '<td>' + regionTags + '</td>';
    html += '<td>' + (normalizeDate(r.startDate) || '') + '</td>';
    html += '<td>' + (r.endDate ? normalizeDate(r.endDate) : '') + '</td>';
    html += '<td>' + (r.freezeDate || '') + '</td>';
    html += '<td>' + (r.versionDate || '') + '</td>';
    html += '<td>' + (r.extVersion ? '<span class="version-badge">' + escapeHtml(VER_NAME_MAP[r.extVersion] || r.extVersion) + '</span>' : '') + '</td>';
    html += '<td>' + renderJiraHtml(r) + '</td></tr>';
  }});

  if (!all.length) {{
    html += '<tr><td colspan="10" style="text-align:center;padding:40px;color:var(--gray-5)">\\u6682\\u65e0\\u5339\\u914d\\u7684\\u4efb\\u52a1</td></tr>';
  }}

  html += '</tbody></table></div>';
  document.getElementById('tableView').innerHTML = html;
}}

function sortBy(field) {{
  if (sortField === field) {{
    sortDir = sortDir === 'asc' ? 'desc' : 'asc';
  }} else {{
    sortField = field;
    sortDir = 'asc';
  }}
  render();
}}

// ======================== GANTT CHART ========================
function renderGantt(filtered, adminFiltered) {{
  // Combine
  var all = filtered.concat(adminFiltered.map(function(t) {{
    return {{
      title: t.title,
      progress: t.progress,
      testDate: '',
      freezeDate: t.scheduledEnd || '',
      versionDate: t.scheduledStart || '',
      onlineDate: null,
      startDate: t.scheduledStart || '',
      endDate: t.scheduledEnd || '',
      assignee: [{{ name: t.assigneeName }}],
      region: [t.region],
      id: '_admin_' + Date.now() + Math.random(),
      _priority: t.priority,
      _isAdmin: true
    }};
  }}));

  if (!all.length) {{
    document.getElementById('ganttView').innerHTML = '<div class="empty-state"><span class="empty-icon">\\u{{1F4CA}}</span><div>\\u6682\\u65e0\\u6570\\u636e</div></div>';
    return;
  }}

  // Determine date range
  var minDate = null, maxDate = null;
  all.forEach(function(r) {{
    var sd = parseDate(normalizeDate(r.startDate));
    var ed = parseDate(normalizeDate(r.endDate));
    if (sd && (!minDate || sd < minDate)) minDate = sd;
    if (ed && (!maxDate || ed > maxDate)) maxDate = ed;
    var fd = parseDate(r.freezeDate);
    if (fd && (!maxDate || fd > maxDate)) maxDate = fd;
    var vd = parseDate(r.versionDate);
    if (vd && (!maxDate || vd > maxDate)) maxDate = vd;
  }});

  if (!minDate) minDate = new Date();
  if (!maxDate) maxDate = new Date();
  minDate = getMonday(minDate);
  var msDiff = maxDate - minDate;
  var weeksNeeded = Math.max(8, Math.ceil(msDiff / (7 * 86400000)) + 3);
  var pixelPerDay = 24;
  var weekWidth = pixelPerDay * 7;

  // Group by person
  var personMap = {{}};
  all.forEach(function(r) {{
    var names = (r.assignee || []).map(function(p) {{ return p.name; }});
    if (!names.length) names = ['\\u672a\\u6307\\u6d3e'];
    names.forEach(function(n) {{
      if (!personMap[n]) personMap[n] = [];
      personMap[n].push(r);
    }});
  }});

  // Detect task overlaps for each person
  var overlapInfo = {{}};
  Object.keys(personMap).forEach(function(pName) {{
    var tasks = personMap[pName];
    var overlapMap = {{}};
    for (var i = 0; i < tasks.length; i++) {{
      var t1 = tasks[i];
      var sd1 = parseDate(normalizeDate(t1.startDate));
      var ed1 = parseDate(normalizeDate(t1.endDate));
      if (!sd1 && !ed1) continue;
      if (!sd1) sd1 = ed1;
      if (!ed1) ed1 = sd1;
      for (var j = i + 1; j < tasks.length; j++) {{
        var t2 = tasks[j];
        var sd2 = parseDate(normalizeDate(t2.startDate));
        var ed2 = parseDate(normalizeDate(t2.endDate));
        if (!sd2 && !ed2) continue;
        if (!sd2) sd2 = ed2;
        if (!ed2) ed2 = sd2;
        // Check overlap: startA <= endB AND endA >= startB
        if (sd1 <= ed2 && ed1 >= sd2) {{
          overlapMap[i] = (overlapMap[i] || 0) + 1;
          overlapMap[j] = (overlapMap[j] || 0) + 1;
        }}
      }}
    }}
    overlapInfo[pName] = overlapMap;
  }});

  var personNames = Object.keys(personMap).sort();

  // Generate week labels
  var weekLabels = [];
  for (var w = 0; w < weeksNeeded; w++) {{
    var monday = new Date(minDate);
    monday.setDate(monday.getDate() + w * 7);
    var month = monday.getMonth() + 1;
    var day = monday.getDate();
    var isToday = false;
    var today = new Date();
    var diffDays = Math.round((monday - getMonday(today)) / 86400000);
    if (diffDays === 0) isToday = true;
    weekLabels.push({{ date: monday, label: month + '/' + day, isToday: isToday }});
  }}

  var totalWidth = weekLabels.length * weekWidth;

  var html = '<div class="gantt-wrapper"><div class="gantt-container">';

  // Header
  html += '<div class="gantt-header">';
  html += '<div class="gantt-person-col">\\u6267\\u884c\\u4eba</div>';
  html += '<div class="gantt-timeline">';
  weekLabels.forEach(function(wl) {{
    var cls = 'gantt-week-label';
    if (wl.isToday) cls += ' today';
    html += '<div class="' + cls + '" style="width:' + weekWidth + 'px">' + wl.label + '</div>';
  }});
  html += '</div></div>';

  // Rows
  personNames.forEach(function(pName) {{
    var tasks = personMap[pName];
    html += '<div class="gantt-person-group">';
      html += '<div class="gantt-person-name">' + escapeHtml(pName) + ' <span class="dept-tag">(' + tasks.length + ')</span>';
      // Show overlap badge if this person has overlapping tasks
      var pOverlapInfo = overlapInfo[pName] || {{}};
      var hasOverlap = Object.keys(pOverlapInfo).length > 0;
      if (hasOverlap) {{
        var maxOverlap = 0;
        for (var oi in pOverlapInfo) {{
          if (pOverlapInfo[oi] > maxOverlap) maxOverlap = pOverlapInfo[oi];
        }}
        html += ' <span class="gantt-overlap-badge" title="' + maxOverlap + '\u4e2a\u4efb\u52a1\u65f6\u95f4\u91cd\u53e0\">\u26A0 ' + maxOverlap + '\u91cd\u53e0</span>';
      }}
      html += '</div>';
    html += '<div class="gantt-row-timeline" style="position:relative;min-height:44px;width:' + totalWidth + 'px">';

    // Grid lines
    html += '<div class="gantt-gridlines" style="display:flex;position:absolute;top:0;left:0;right:0;bottom:0;pointer-events:none">';
    weekLabels.forEach(function() {{
      html += '<div class="gantt-gridline" style="width:' + weekWidth + 'px"></div>';
    }});
    html += '</div>';

    // Task bars
    tasks.forEach(function(r) {{
      var sd = parseDate(normalizeDate(r.startDate));
      var ed = parseDate(normalizeDate(r.endDate));
      if (!sd && !ed) return;
      if (!sd) sd = ed;
      if (!ed) ed = sd;

      var startMs = sd.getTime();
      var endMs = ed.getTime();
      var minMs = minDate.getTime();
      var dayMs = 86400000;

      var left = Math.max(0, (startMs - minMs) / dayMs * pixelPerDay);
      var width = Math.max(pixelPerDay, (endMs - startMs) / dayMs * pixelPerDay + pixelPerDay);
      if (left + width > totalWidth) width = totalWidth - left;
      if (width < pixelPerDay) width = pixelPerDay;

      var progClass = 'progress-notstarted';
      if (r.progress === '\\u8fdb\\u884c\\u4e2d') progClass = 'progress-progress';
      else if (r.progress === 'QA\\u9a8c\\u6536\\u4e2d') progClass = 'progress-qa';
      // Check overlap
      var tIdx = tasks.indexOf(r);
      var isOverlap = false;
      var overlapCount = 0;
      if (overlapInfo[pName] && overlapInfo[pName][tIdx]) {{
        isOverlap = true;
        overlapCount = overlapInfo[pName][tIdx];
        progClass += ' overlap';
        if (overlapCount >= 2) progClass += ' overlap-double';
      }}

      var barTitle = r.title;
      if (barTitle.length > 12) barTitle = barTitle.substring(0, 12) + '..';

      var escTitle = r.title.replace(/'/g, "\\\\'").replace(/"/g, '&quot;');
      var names = (r.assignee || []).map(function(p) {{ return p.name; }}).join(', ');
      var regionStr = (r.region || []).join(', ');

      html += '<div class="gantt-bar ' + progClass + '" style="left:' + left + 'px;width:' + Math.max(30, width) + 'px" ';
      html += 'onmouseenter="showGanttTooltip(event,\\'' + escTitle + '\\',\\'' + r.progress + '\\',\\'' + names + '\\',\\'' + regionStr + '\\',\\'' + (normalizeDate(r.startDate)||'') + '\\',\\'' + (normalizeDate(r.endDate)||'') + '\\',\\'' + (r.freezeDate||'') + '\\',\\'' + (r.versionDate||'') + '\\')" ';
      html += 'onmouseleave="hideGanttTooltip()">';
      html += escapeHtml(barTitle) + '</div>';

      // Milestones
      var fd = parseDate(r.freezeDate);
      if (fd && fd >= minDate) {{
        var fLeft = (fd.getTime() - minMs) / dayMs * pixelPerDay;
        if (fLeft >= 0 && fLeft <= totalWidth) {{
          html += '<div class="gantt-milestone freeze" style="left:' + fLeft + 'px" title="\\u5c01\\u677f: ' + r.freezeDate + '"></div>';
        }}
      }}
      var vd = parseDate(r.versionDate);
      if (vd && vd >= minDate) {{
        var vLeft = (vd.getTime() - minMs) / dayMs * pixelPerDay;
        if (vLeft >= 0 && vLeft <= totalWidth) {{
          html += '<div class="gantt-milestone version" style="left:' + vLeft + 'px" title="\\u7248\\u66f4: ' + r.versionDate + '"></div>';
        }}
      }}
      var td = parseDate(r.testDate);
      if (td && td >= minDate) {{
        var tLeft = (td.getTime() - minMs) / dayMs * pixelPerDay;
        if (tLeft >= 0 && tLeft <= totalWidth) {{
          html += '<div class="gantt-milestone test" style="left:' + tLeft + 'px" title="\\u8f6c\\u6d4b: ' + r.testDate + '"></div>';
        }}
      }}
    }});

    html += '</div></div>';
  }});

  html += '</div></div>';
  document.getElementById('ganttView').innerHTML = html;
}}

// ======================== GANTT TOOLTIP ========================
function showGanttTooltip(e, title, progress, assignee, region, startDate, endDate, freezeDate, versionDate) {{
  var tip = document.getElementById('ganttTooltip');
  var html = '<div class="tt-title">' + escapeHtml(title) + '</div>';
  html += '<div class="tt-row"><span>\\u8fdb\\u5c55: ' + progress + '</span><span>' + (assignee||'') + '</span></div>';
  if (region) html += '<div class="tt-row"><span>\\u5730\\u533a: ' + region + '</span></div>';
  html += '<div class="tt-row"><span>' + startDate + ' ~ ' + endDate + '</span></div>';
  if (freezeDate) html += '<div class="tt-row"><span>\\u5c01\\u677f: ' + freezeDate + '</span></div>';
  if (versionDate) html += '<div class="tt-row"><span>\\u7248\\u66f4: ' + versionDate + '</span></div>';
  if (typeof extVersion !== 'undefined' && extVersion) html += '<div class="tt-row"><span>\\u5916\\u653e\\u7248\\u672c: ' + extVersion + '</span></div>';
  if (typeof jiraKey !== 'undefined' && jiraKey) html += '<div class="tt-row"><span>Jira: ' + jiraKey + '</span></div>';
  tip.innerHTML = html;
  tip.style.display = 'block';
  var rect = e.target.getBoundingClientRect();
  var tx = rect.left;
  var ty = rect.top - tip.offsetHeight - 8;
  if (ty < 0) ty = rect.bottom + 8;
  if (tx + 360 > window.innerWidth) tx = window.innerWidth - 370;
  if (tx < 0) tx = 4;
  tip.style.left = tx + 'px';
  tip.style.top = ty + 'px';
}}

function hideGanttTooltip() {{
  document.getElementById('ganttTooltip').style.display = 'none';
}}

// ======================== VIEW SWITCH ========================
function switchView(view) {{
  currentView = view;
  document.querySelectorAll('.view-tab').forEach(function(t) {{ t.classList.remove('active'); }});
  document.querySelector('.view-tab[data-view="' + view + '"]').classList.add('active');
  ['cardView','personView','tableView','ganttView','parentGanttView','jiraView'].forEach(function(id) {{
    var show = false;
    if (view === 'parentgantt' && id === 'parentGanttView') show = true;
    else if (view === 'jira' && id === 'jiraView') show = true;
    else if (view !== 'parentgantt' && view !== 'jira' && id.indexOf(view) === 0) show = true;
    document.getElementById(id).style.display = show ? 'block' : 'none';
  }});
  if (view === 'jira') {{ initJiraView(); renderJiraView(); }}
  else {{ render(); }}
}}

// ======================== HELPERS ========================
function escapeHtml(str) {{
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#x27;');
}}

// ======================== ADMIN MODAL ========================
function openAdminModal() {{
  renderAdminTasks();
  document.getElementById('adminModalOverlay').classList.add('active');
}}

function closeAdminModal() {{
  document.getElementById('adminModalOverlay').classList.remove('active');
}}

function renderAdminTasks() {{
  var list = document.getElementById('adminTasksList');
  if (!adminTasks.length) {{
    list.innerHTML = '<div style="text-align:center;padding:20px;color:var(--gray-5)">\\u6682\\u65e0\\u624b\\u52a8\\u6dfb\\u52a0\\u7684\\u4efb\\u52a1</div>';
    return;
  }}
  var html = '';
  adminTasks.forEach(function(t, i) {{
    var prioTag = '<span class="priority-high">' + (t.priority || 'P2') + '</span>';
    html += '<div class="admin-task-item">';
    html += '<span class="at-title">' + escapeHtml(t.title) + '</span>';
    html += '<span>' + prioTag + ' | ' + escapeHtml(t.assigneeName) + ' | ' + escapeHtml(t.scheduledStart) + '~' + escapeHtml(t.scheduledEnd) + '</span>';
    html += '<div class="at-actions"><button class="btn btn-sm btn-danger" onclick="removeAdminTask(' + i + ')">\\u5220\\u9664</button></div>';
    html += '</div>';
  }});
  list.innerHTML = html;
}}

function removeAdminTask(idx) {{
  adminTasks.splice(idx, 1);
  saveAdminTasks();
  renderAdminTasks();
  render();
}}

function addAdminTask() {{
  var title = document.getElementById('newTaskTitle').value.trim();
  var hours = parseFloat(document.getElementById('newTaskHours').value) || 1;
  var priority = document.getElementById('newTaskPriority').value;
  var assigneeName = document.getElementById('newTaskPerson').value;
  var region = document.getElementById('newTaskRegion').value;
  var deadline = document.getElementById('newTaskDeadline').value;

  if (!title) {{ alert('\\u8bf7\\u8f93\\u5165\\u5de5\\u4f5c\\u5185\\u5bb9'); return; }}
  if (!assigneeName) {{ alert('\\u8bf7\\u9009\\u62e9\\u6267\\u884c\\u4eba'); return; }}

  // Calculate schedule - find next available slot
  // Look at existing tasks for this person to find earliest gap
  var personTasks = DATA.filter(function(r) {{
    return r.assignee && r.assignee.some(function(p) {{ return p.name === assigneeName; }});
  }});

  // Also consider admin tasks
  adminTasks.filter(function(t) {{ return t.assigneeName === assigneeName; }}).forEach(function(t) {{
    personTasks.push({{
      startDate: t.scheduledStart,
      endDate: t.scheduledEnd,
      title: t.title
    }});
  }});

  // Sort by start date
  personTasks.sort(function(a, b) {{
    var da = parseDate(normalizeDate(a.startDate));
    var db = parseDate(normalizeDate(b.startDate));
    if (!da && !db) return 0;
    if (!da) return 1;
    if (!db) return -1;
    return da - db;
  }});

  // Find earliest available slot (starting from today)
  var today = new Date();
  today.setHours(0,0,0,0);
  var candidateStart = new Date(today);

  var workDaysNeeded = Math.ceil(hours);
  var scheduledStart = null;
  var scheduledEnd = null;

  // If a deadline is set, use it as the upper bound
  var deadlineDate = deadline ? parseDate(deadline) : null;

  // Scan for earliest gap: try starting from each existing task's end date + 1
  var candidates = [new Date(today)];
  personTasks.forEach(function(t) {{
    var te = parseDate(normalizeDate(t.endDate));
    if (te) {{
      var next = new Date(te);
      next.setDate(next.getDate() + 1);
      candidates.push(next);
    }}
  }});

  // Sort candidates
  candidates.sort(function(a,b) {{ return a - b; }});

  var maxSearchDays = 120;
  for (var ci = 0; ci < candidates.length; ci++) {{
    var baseStart = new Date(Math.max(candidates[ci].getTime(), today.getTime()));
    for (var d = 0; d < maxSearchDays; d++) {{
      var slotStart = new Date(baseStart);
      slotStart.setDate(slotStart.getDate() + d);
      var slotEnd = new Date(slotStart);
      slotEnd.setDate(slotEnd.getDate() + workDaysNeeded - 1);

      // Check if slot exceeds deadline
      if (deadlineDate && slotEnd > deadlineDate) {{
        break; // Try next candidate
      }}

      // Check overlap
      var overlap = personTasks.some(function(t) {{
        var ts = parseDate(normalizeDate(t.startDate));
        var te = parseDate(normalizeDate(t.endDate));
        if (!ts || !te) return false;
        return (slotStart <= te && slotEnd >= ts);
      }});

      if (!overlap) {{
        scheduledStart = formatDate(slotStart);
        scheduledEnd = formatDate(slotEnd);
        break;
      }}
    }}
    if (scheduledStart) break;
  }}

  if (!scheduledStart) {{
    alert('\\u65e0\\u6cd5\\u627e\\u5230\\u8db3\\u591f\\u7684\\u7a7a\\u4f59\\u6392\\u671f\\u65f6\\u95f4\\uff0c\\u8bf7\\u8c03\\u6574\\u5de5\\u65f6\\u6216\\u8054\\u7cfb\\u7ba1\\u7406\\u5458');
    return;
  }}

  var resultDiv = document.getElementById('scheduleResult');
  resultDiv.style.display = 'block';
  resultDiv.innerHTML = '\\u2705 \\u6392\\u671f\\u7ed3\\u679c: <strong>' + escapeHtml(assigneeName) + '</strong> \\u4e8e <strong>' + scheduledStart + ' ~ ' + scheduledEnd + '</strong> \\u6267\\u884c\\u300c' + escapeHtml(title) + '\\u300d\\uff08' + hours + '\\u4eba\\u5929\\uff09';

  // Add task
  var newTask = {{
    title: title,
    hours: hours,
    priority: priority,
    assigneeName: assigneeName,
    region: region,
    progress: '\\u672a\\u542f\\u52a8',
    scheduledStart: scheduledStart,
    scheduledEnd: scheduledEnd,
    createdAt: new Date().toISOString()
  }};

  adminTasks.push(newTask);
  saveAdminTasks();
  renderAdminTasks();

  // Reset form
  document.getElementById('newTaskTitle').value = '';
  var future = new Date();
  future.setDate(future.getDate() + 7);
  document.getElementById('newTaskDeadline').value = formatDateISO(future);
  render();
}}


// ======================== MULTI-SELECT ========================
var _msSelected = {{}};
function msPopulate(key, values, initSelected) {{
  var box = document.getElementById('msCheckboxes_' + key);
  if (!box) return;
  box.innerHTML = '';
  _msSelected[key] = initSelected.slice();
  values.forEach(function(v) {{
    var lb = document.createElement('label');
    var cb = document.createElement('input');
    cb.type = 'checkbox'; cb.value = v; cb.checked = true;
    cb.onchange = function() {{ onMsChange(key); }};
    lb.appendChild(cb);
    lb.appendChild(document.createTextNode(' ' + v));
    box.appendChild(lb);
  }});
}}

function toggleMsPanel(key) {{
  var panel = document.getElementById('msPanel_' + key);
  panel.style.display = panel.style.display === 'block' ? 'none' : 'block';
}}

function toggleMsAll(key) {{
  var allCb = document.querySelector('#msPanel_' + key + ' input[data-all]');
  var cbs = document.querySelectorAll('#msPanel_' + key + ' input[type=checkbox]:not([data-all])');
  var check = allCb.checked;
  cbs.forEach(function(c) {{ c.checked = check; }});
  onMsChange(key);
}}

function onMsChange(key) {{
  var cbs = document.querySelectorAll('#msCheckboxes_' + key + ' input[type=checkbox]');
  var checked = [];
  cbs.forEach(function(c) {{ if (c.checked) checked.push(c.value); }});
  var allCb = document.querySelector('#msPanel_' + key + ' input[data-all]');
  var trigger = document.querySelector('#ms' + key.charAt(0).toUpperCase() + key.slice(1) + ' .ms-label');
  if (trigger) {{
    if (checked.length === 0) {{ trigger.textContent = '\\u65e0'; }}
    else if (checked.length === cbs.length) {{ trigger.textContent = '\\u5168\\u90e8'; }}
    else if (checked.length <= 2) {{ trigger.textContent = checked.join(', '); }}
    else {{ trigger.textContent = checked.length + '\\u4e2a'; }}
  }}
  if (allCb) allCb.checked = checked.length === cbs.length;
  var hidden = document.getElementById('filter' + key.charAt(0).toUpperCase() + key.slice(1));
  if (hidden) hidden.value = checked.length === 0 || checked.length === cbs.length ? 'ALL' : checked.join(',');
  applyFilters();
}}

// ======================== PERSON SEARCH ========================
var _psData = [];
function onPersonSearch(val) {{
  var div = document.getElementById('psResults');
  if (!val) {{ div.style.display = 'none'; return; }}
  var q = val.toLowerCase();
  var matched = _psData.filter(function(e) {{ return e.label.toLowerCase().indexOf(q) >= 0 || e.name.toLowerCase().indexOf(q) >= 0; }});
  if (matched.length === 0) {{ div.style.display = 'none'; return; }}
  div.innerHTML = '';
  matched.slice(0, 15).forEach(function(e) {{
    var item = document.createElement('div');
    item.className = 'ps-item';
    item.textContent = e.label;
    item.setAttribute('data-name', e.name);
    item.setAttribute('data-label', e.label);
    item.addEventListener('mousedown', function() {{ selectPerson(e.name, e.label); }});
    div.appendChild(item);
  }});
  div.style.display = 'block';
}}function selectPerson(name, label) {{
  // Toggle person in multi-select
  var cbs = document.querySelectorAll('#msCheckboxes_person input[type=checkbox]');
  cbs.forEach(function(c) {{ if (c.value === name) {{ c.checked = !c.checked; onMsChange('person'); }} }});
  document.getElementById('filterPersonSearch').value = '';
  document.getElementById('psResults').style.display = 'none';
}}

// ======================== PARENT GANTT ========================
var _pgTimer = null;
function onPgSearch(val) {{
  clearTimeout(_pgTimer);
  var div = document.getElementById('pgSuggest');
  if (!val || val.length < 2) {{ div.style.display = 'none'; return; }}
  _pgTimer = setTimeout(function() {{
    var q = val.toLowerCase();
    var m = DATA.filter(function(r) {{ return fuzzyMatch(r.title, q); }}).slice(0, 15);
    if (m.length === 0) {{ div.style.display = 'none'; return; }}
    var seen = {{}};
    div.innerHTML = '';
    m.forEach(function(r) {{
      var pfx = r.title.match(/^(\\u3010[^\\u3010]+\\u3011\\u3010\\u603b\\u3011\\d{{4}})/);
      var display = pfx ? pfx[1] : (r.title.length > 35 ? r.title.substring(0,35) + '...' : r.title);
      if (display.length > 35) display = display.substring(0,35) + '...';
      if (!seen[display]) {{
        seen[display] = true;
        var item = document.createElement('div');
        item.className = 'psg-item';
        item.textContent = display;
        item.addEventListener('mousedown', function() {{ showPgGroup(display); }});
        div.appendChild(item);
      }}
    }});
    div.style.display = 'block';
  }}, 250);
}}function showPgGroup(title) {{
  var _origSearch = document.getElementById('pgSearch').value || '';
  document.getElementById('pgSearch').value = title;
  document.getElementById('pgSuggest').style.display = 'none';
  // Strategy 1: prefix match
  var m = title.match(/^(\\u3010[^\\u3010]+\\u3011\\u3010\\u603b\\u3011\\d{{4}})/);
  var pfx = m ? m[1] : title;
  var tasks = DATA.filter(function(r) {{ return r.title.indexOf(pfx) === 0; }});
  // Strategy 2: extract keyword and fuzzy match subtasks (always add to Strategy 1 results)
  var kw = title.replace(/^(\\u3010[^\\u3010]+\\u3011)?(\\u3010\\u603b\\u3011)?\\d{{4}}\\s?/, '');
  // If keyword extracted from title is too short, use the original search input as fallback
  if (kw.length < 2) {{
    var searchVal = _origSearch || '';
    var cleanKw = searchVal.replace(/^(\\u3010[^\\u3010]+\\u3011)?(\\u3010\\u603b\\u3011)?\\d{{4}}\\s?/, '');
    if (cleanKw.length >= 2) kw = cleanKw;
  }}
  if (kw.length >= 2) {{
    var kwTasks = DATA.filter(function(r) {{ return fuzzyMatch(r.title, kw); }});
    var existIds = tasks.map(function(r) {{ return r.id; }});
    kwTasks.forEach(function(t) {{
      if (existIds.indexOf(t.id) < 0) {{ tasks.push(t); existIds.push(t.id); }}
    }});
  }}
  // Strategy 3: find children via title pattern matching
  // Parent tasks have 【总】 in their titles; children share the same region+date prefix
  if (tasks.length > 0) {{
    var parentPrefixes = [];
    var existIds = tasks.map(function(r) {{ return r.id; }});
    tasks.forEach(function(r) {{
      var m = r.title.match(/^(\u3010[^\u3010]+\u3011)\u3010\u603b\u3011\d{{4}}/);
      if (m) {{
        var regionPrefix = m[1]; // e.g. 【日服】
        var dateMatch = r.title.match(/\u3010\u603b\u3011(\d{{4}})/);
        if (dateMatch) {{
          parentPrefixes.push(regionPrefix + dateMatch[1]); // e.g. 【日服】0630
        }}
      }}
    }});
    if (parentPrefixes.length > 0) {{
      DATA.forEach(function(r) {{
        if (existIds.indexOf(r.id) >= 0) return; // already included
        for (var i = 0; i < parentPrefixes.length; i++) {{
          if (r.title.indexOf(parentPrefixes[i]) === 0) {{
            tasks.push(r);
            existIds.push(r.id);
            break;
          }}
        }}
      }});
    }}
  }}
  if (tasks.length === 0) tasks = DATA.filter(function(r) {{ return r.title === title; }});
  renderSimpleGantt(tasks, pfx);
}}

function renderParentGantt(filtered, adminFiltered) {{
  var div = document.getElementById('pgResult');
  var title = document.getElementById('pgSearch').value;
  if (title) {{
    showPgGroup(title);
  }} else {{
    div.innerHTML = '<div style=\"padding:30px 12px;text-align:center;color:var(--gray-5);font-size:13px\">\\u5728\\u4e0a\\u65b9\\u8f93\\u5165\\u4efb\\u52a1\\u540d\\u79f0\\uff0c\\u67e5\\u770b\\u540c\\u7248\\u672c\\u6240\\u6709\\u4efb\\u52a1\\u6392\\u671f\\u7518\\u7279\\u56fe</div>';
  }}
}}

function renderSimpleGantt(tasks, label) {{
  var div = document.getElementById('pgResult');
  tasks.sort(function(a,b) {{
    var da = a.endDate ? new Date(a.endDate) : new Date('2099/12/31');
    var db = b.endDate ? new Date(b.endDate) : new Date('2099/12/31');
    return da - db;
  }});
  var ms = null, me = null;
  tasks.forEach(function(r) {{
    var sd = r.startDate ? normalizeDate(r.startDate) : r.endDate ? normalizeDate(r.endDate) : null;
    var ed = r.endDate ? normalizeDate(r.endDate) : r.startDate ? normalizeDate(r.startDate) : null;
    if (sd) {{ var d = new Date(sd); if (!ms || d < ms) ms = d; }}
    if (ed) {{ var d = new Date(ed); if (!me || d > me) me = d; }}
  }});
  if (!ms && !me) {{ div.innerHTML = '<div style=\"padding:20px\">\\u6682\\u65e0\\u65e5\\u671f</div>'; return; }}
  if (!ms) ms = me; if (!me) me = ms;
  var s = new Date(ms); s.setDate(s.getDate() - 7);
  var e = new Date(me); e.setDate(e.getDate() + 14);
  var td = Math.ceil((e - s) / (1000*60*60*24));
  var today = new Date(); today.setHours(0,0,0,0);

  var h = '<div class=\"pg-group-title\">' + label + '</div>';
  h += '<div class=\"pg-group-subtitle\">\\u5171 ' + tasks.length + ' \\u4e2a\\u4efb\\u52a1 | ' + ms.toISOString().substring(0,10) + ' ~ ' + me.toISOString().substring(0,10) + '</div>';
  h += '<div style=\"overflow-x:auto;font-size:12px;border:1px solid var(--gray-3);border-radius:8px\">';

  // Header row
  h += '<div style=\"display:flex;position:sticky;top:0;background:var(--gray-1);z-index:2;border-bottom:1px solid var(--gray-3);min-width:' + (180 + td*16) + 'px\">';
  h += '<div style=\"width:180px;flex-shrink:0;padding:6px 8px;font-weight:600;font-size:12px\">\\u4efb\\u52a1</div>';
  for (var d = new Date(s); d <= e; d.setDate(d.getDate()+1)) {{
    var isWE = d.getDay() === 0 || d.getDay() === 6;
    h += '<div style=\"width:16px;flex-shrink:0;text-align:center;font-size:8px;padding-top:2px;';
    if (isWE) h += 'color:var(--gray-4);';
    h += '\">' + (d.getDate() === 1 ? d.getMonth()+1+'/' : '') + '</div>';
  }}
  h += '</div>';

  // Task rows
  tasks.forEach(function(r) {{
    var sd = r.startDate ? normalizeDate(r.startDate) : r.endDate ? normalizeDate(r.endDate) : null;
    var ed = r.endDate ? normalizeDate(r.endDate) : r.startDate ? normalizeDate(r.startDate) : null;
    var sdd = sd ? new Date(sd) : null;
    var edd = ed ? new Date(ed) : null;

    var clr = 'var(--gray-4)';
    if (r.progress === '\\u8fdb\\u884c\\u4e2d') clr = 'var(--warning)';
    else if (r.progress === 'QA\\u9a8c\\u6536\\u4e2d') clr = 'var(--success)';
    var ts = r.title.length > 22 ? r.title.substring(0,22) + '...' : r.title;

    h += '<div style=\"display:flex;align-items:center;min-width:' + (180 + td*16) + 'px;border-bottom:1px solid var(--gray-3)\">';
    h += '<div style=\"width:180px;flex-shrink:0;padding:3px 8px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:10px\" title=\"' + r.title.replace(/\"/g, '&quot;') + '\">' + ts + '</div>';

    for (var d = new Date(s); d <= e; d.setDate(d.getDate()+1)) {{
      var ds = new Date(d); ds.setHours(0,0,0,0);
      var de2 = new Date(ds); de2.setHours(23,59,59,999);
      var inR = sdd && edd && de2 >= sdd && ds <= edd;
      var isT = ds.getTime() === today.getTime();
      var bg = inR ? clr : 'transparent';
      h += '<div style=\"width:16px;flex-shrink:0;height:18px;background:' + bg + ';';
      if (isT) h += 'border-left:2px solid var(--danger);';
      h += '\"></div>';
    }}
    h += '</div>';
  }});
  h += '</div>';
  div.innerHTML = h;
}}


// ======================== PERSON VIEW ========================
function renderPersonView() {{
  var result = getFilteredData();
  var filtered = result.records.concat(result.adminTasks);
  var div = document.getElementById('personViewInner');
  var statsDiv = document.getElementById('personStats');

  if (filtered.length === 0) {{
    div.innerHTML = '<div class=\"empty-state\"><span class=\"empty-icon\">\👤</span><div>\\u6682\\u65e0\\u6570\\u636e</div></div>';
    return;
  }}

  // Group by assignee
  var peopleMap = {{}};
  filtered.forEach(function(r) {{
    var names = [];
    if (r.assigneeName) {{
      names.push(r.assigneeName);
    }} else if (r.assignee) {{
      r.assignee.forEach(function(p) {{ names.push(p.name); }});
    }}
    if (names.length === 0) names.push('\\u672a\\u5206\\u914d');
    names.forEach(function(n) {{
      if (!peopleMap[n]) peopleMap[n] = [];
      peopleMap[n].push(r);
    }});
  }});

  var people = Object.keys(peopleMap).sort(function(a, b) {{
    return peopleMap[b].length - peopleMap[a].length;
  }});

  var html = '';
  people.forEach(function(person) {{
    var tasks = peopleMap[person];
    var done = tasks.filter(function(t) {{ return t.progress === 'QA\\u9a8c\\u6536\\u4e2d'; }}).length;
    var inProgress = tasks.filter(function(t) {{ return t.progress === '\\u8fdb\\u884c\\u4e2d'; }}).length;
    var notStarted = tasks.length - done - inProgress;

    var dept = '';
    ALL_PEOPLE.forEach(function(ap) {{ if (ap.name === person) dept = ap.dept; }});

    html += '<div class=\"person-card\">';
    html += '<h4>' + person + (dept ? ' <span style=\"font-size:11px;color:var(--gray-5);font-weight:400\">' + dept + '</span>' : '') + '</h4>';
    html += '<div class=\"person-stats\">';
    html += '<div class=\"person-stat\">\\u603b\\u4efb\\u52a1 <strong>' + tasks.length + '</strong></div>';
    if (done > 0) html += '<div class=\"person-stat\">\\u5df2\\u5b8c\\u6210 <strong>' + done + '</strong></div>';
    if (inProgress > 0) html += '<div class=\"person-stat\">\\u8fdb\\u884c\\u4e2d <strong>' + inProgress + '</strong></div>';
    if (notStarted > 0) html += '<div class=\"person-stat\">\\u672a\\u542f\\u52a8 <strong>' + notStarted + '</strong></div>';
    html += '</div>';

    tasks.sort(function(a,b) {{
      var oa = a.progress === '\\u8fdb\\u884c\\u4e2d' ? 0 : a.progress === 'QA\\u9a8c\\u6536\\u4e2d' ? 2 : 1;
      var ob = b.progress === '\\u8fdb\\u884c\\u4e2d' ? 0 : b.progress === 'QA\\u9a8c\\u6536\\u4e2d' ? 2 : 1;
      return oa - ob;
    }});

    tasks.forEach(function(t) {{
      var pc = '';
      if (t.progress === '\\u8fdb\\u884c\\u4e2d') pc = 'var(--warning)';
      else if (t.progress === 'QA\\u9a8c\\u6536\\u4e2d') pc = 'var(--success)';
      else if (t.progress === '\\u672a\\u542f\\u52a8') pc = 'var(--gray-4)';
      var ts = t.title.length > 30 ? t.title.substring(0,30) + '...' : t.title;
      html += '<div class=\"person-task\">' + ts;
      if (t.progress) html += '<span class=\"pt-progress\" style=\"background:' + pc + ';color:#fff\">' + t.progress + '</span>';
      html += '</div>';
    }});
    html += '</div>';
  }});
  div.innerHTML = html;
}}

// ======================== DELETE TASK ========================
function getHiddenIds() {{
  try {{ return JSON.parse(localStorage.getItem('rox_hidden_ids') || '[]'); }} catch(e) {{ return []; }}
}}
function saveHiddenIds(ids) {{
  localStorage.setItem('rox_hidden_ids', JSON.stringify(ids));
}}
function deleteTask(id) {{
  if (!confirm('确定要删除该任务吗？')) return;
  var ids = getHiddenIds();
  if (ids.indexOf(id) === -1) ids.push(id);
  saveHiddenIds(ids);
  render();
  if (currentView === 'person') renderPersonView();
}}
function deleteTaskById(id) {{
  deleteTask(id);
}}
function deleteAdminTask(idx) {{
  if (!confirm('确定要删除该任务吗？')) return;
  adminTasks.splice(idx, 1);
  saveAdminTasks();
  render();
  if (currentView === 'person') renderPersonView();
}}

// ======================== ADD TASK ========================
function toggleAddForm() {{
  var panel = document.getElementById('addTaskPanel');
  if (panel.style.display === 'none') {{
    panel.style.display = 'block';
    var sel = document.getElementById('addTaskPerson');
    if (sel.options.length <= 1) {{
      var deptMap = {{}};
      ALL_PEOPLE.forEach(function(p) {{
        if (!deptMap[p.dept]) deptMap[p.dept] = [];
        deptMap[p.dept].push(p);
      }});
      var sortedDepts = Object.keys(deptMap).sort();
      sortedDepts.forEach(function(dept) {{
        var optg = document.createElement('optgroup');
        optg.label = dept;
        deptMap[dept].sort(function(a,b) {{ return a.name.localeCompare(b.name); }}).forEach(function(p) {{
          var opt = document.createElement('option');
          opt.value = p.name;
          opt.textContent = dept + ' - ' + p.name;
          optg.appendChild(opt);
        }});
        sel.appendChild(optg);
      }});
    }}
    var future = new Date();
    future.setDate(future.getDate() + 7);
    document.getElementById('addTaskDeadline').value = formatDateISO(future);
    setTimeout(function() {{ document.getElementById('addTaskTitle').focus(); }}, 100);
  }} else {{
    panel.style.display = 'none';
  }}
}}

function submitAddTask() {{
  var title = document.getElementById('addTaskTitle').value.trim();
  var assigneeName = document.getElementById('addTaskPerson').value;
  var hours = parseFloat(document.getElementById('addTaskHours').value) || 1;
  var region = document.getElementById('addTaskRegion').value;
  var deadline = document.getElementById('addTaskDeadline').value;
  if (!title) {{ alert('请输入工作内容'); return; }}
  if (!assigneeName) {{ alert('请选择执行人'); return; }}
  var personTasks = DATA.filter(function(r) {{
    return r.assignee && r.assignee.some(function(p) {{ return p.name === assigneeName; }});
  }});
  adminTasks.filter(function(t) {{ return t.assigneeName === assigneeName; }}).forEach(function(t) {{
    personTasks.push({{ startDate: t.scheduledStart, endDate: t.scheduledEnd, title: t.title }});
  }});
  personTasks.sort(function(a, b) {{
    var da = parseDate(normalizeDate(a.startDate));
    var db = parseDate(normalizeDate(b.startDate));
    if (!da && !db) return 0; if (!da) return 1; if (!db) return -1;
    return da - db;
  }});
  var today = new Date(); today.setHours(0,0,0,0);
  var workDaysNeeded = Math.ceil(hours);
  var scheduledStart = null, scheduledEnd = null;
  var deadlineDate = deadline ? parseDate(deadline) : null;
  var candidates = [new Date(today)];
  personTasks.forEach(function(t) {{
    var te = parseDate(normalizeDate(t.endDate));
    if (te) {{ var next = new Date(te); next.setDate(next.getDate() + 1); candidates.push(next); }}
  }});
  candidates.sort(function(a,b) {{ return a - b; }});
  for (var ci = 0; ci < candidates.length; ci++) {{
    var baseStart = new Date(Math.max(candidates[ci].getTime(), today.getTime()));
    for (var d = 0; d < 120; d++) {{
      var slotStart = new Date(baseStart); slotStart.setDate(slotStart.getDate() + d);
      var slotEnd = new Date(slotStart); slotEnd.setDate(slotEnd.getDate() + workDaysNeeded - 1);
      if (deadlineDate && slotEnd > deadlineDate) break;
      var overlap = personTasks.some(function(t) {{
        var ts = parseDate(normalizeDate(t.startDate));
        var te = parseDate(normalizeDate(t.endDate));
        if (!ts || !te) return false;
        return (slotStart <= te && slotEnd >= ts);
      }});
      if (!overlap) {{ scheduledStart = formatDate(slotStart); scheduledEnd = formatDate(slotEnd); break; }}
    }}
    if (scheduledStart) break;
  }}
  if (!scheduledStart) {{ alert('无法找到足够的空闲排期时间，请调整工时或联系管理员'); return; }}
  var resultDiv = document.getElementById('addTaskResult');
  resultDiv.style.display = 'block';
  resultDiv.innerHTML = '✅ 排期结果: <strong>' + assigneeName + '</strong> 于 <strong>' + scheduledStart + ' ~ ' + scheduledEnd + '</strong> 执行「' + title + '」（' + hours + '人天）';
  var newTask = {{
    title: title, hours: hours, priority: 'P2', assigneeName: assigneeName,
    region: region || '', progress: '未启动', scheduledStart: scheduledStart, scheduledEnd: scheduledEnd,
    createdAt: new Date().toISOString()
  }};
  adminTasks.push(newTask);
  saveAdminTasks();
  document.getElementById('addTaskTitle').value = '';
  var future = new Date(); future.setDate(future.getDate() + 7);
  document.getElementById('addTaskDeadline').value = formatDateISO(future);
  render();
  if (currentView === 'person') renderPersonView();
}}

function formatDateISO(d) {{
  var m = d.getMonth() + 1;
  var day = d.getDate();
  return d.getFullYear() + '-' + (m < 10 ? '0' : '') + m + '-' + (day < 10 ? '0' : '') + day;
}}

// ======================== FUZZY MATCH ========================
function fuzzyMatch(text, query) {{
  var t = text.toLowerCase();
  var q = query.toLowerCase();
  if (t.indexOf(q) >= 0) return true;
  var qi = 0;
  for (var ti = 0; ti < t.length && qi < q.length; ti++) {{
    if (t[ti] === q[qi]) qi++;
  }}
  return qi === q.length;
}}

// ======================== VERSION DATA ========================
var allVersions = [];
function initVersions() {{
  var vSet = {{}};
  DATA.forEach(function(r) {{
    var v = r.extVersion || '';
    if (v) {{
      var vn = VER_NAME_MAP[v] || v;
      vSet[vn] = v; // store display name -> record id
    }}
  }});
  var names = Object.keys(vSet).sort(function(a,b) {{ return a.localeCompare(b); }});
  allVersions = names;
  var sel = document.getElementById('filterVersion');
  if (sel && sel.options.length <= 1) {{
    names.forEach(function(vn) {{
      var opt = document.createElement('option');
      opt.value = vn; opt.textContent = vn;
      sel.appendChild(opt);
    }});
  }}
}}

// ======================== SAVE / LOAD VIEWS ========================
function getSavedViews() {{
  try {{ return JSON.parse(localStorage.getItem('rox_saved_views') || '[]'); }}
  catch(e) {{ return []; }}
}}
function saveSavedViews(views) {{
  localStorage.setItem('rox_saved_views', JSON.stringify(views));
}}
function saveCurrentView() {{
  var name = prompt('\u8bf7\u8f93\u5165\u89c6\u56fe\u540d\u79f0\uff1a');
  if (!name || !name.trim()) return;
  name = name.trim();
  var view = {{
    name: name,
    region: document.getElementById('filterRegion').value,
    progress: document.getElementById('filterProgress').value,
    dept: document.getElementById('filterDept').value,
    person: document.getElementById('filterPerson').value,
    version: (document.getElementById('filterVersion') || {{}}).value || 'ALL',
    search: document.getElementById('filterSearch').value,
    currentView: currentView,
    createdAt: new Date().toISOString()
  }};
  var views = getSavedViews();
  var existing = views.findIndex(function(v) {{ return v.name === name; }});
  if (existing >= 0) views[existing] = view;
  else views.push(view);
  saveSavedViews(views);
  renderSavedViews();
  alert('\u89c6\u56fe "' + name + '" \u5df2\u4fdd\u5b58');
}}
function loadSavedView(name) {{
  var views = getSavedViews();
  var view = views.find(function(v) {{ return v.name === name; }});
  if (!view) return;
  document.getElementById('filterRegion').value = view.region || 'ALL';
  document.getElementById('filterProgress').value = view.progress || 'ALL';
  document.getElementById('filterDept').value = view.dept || 'ALL';
  document.getElementById('filterPerson').value = view.person || 'ALL';
  var vSel = document.getElementById('filterVersion');
  if (vSel) vSel.value = view.version || 'ALL';
  document.getElementById('filterSearch').value = view.search || '';
  ['region','progress','dept','person'].forEach(function(key) {{
    var capitalKey = key.charAt(0).toUpperCase() + key.slice(1);
    var val = document.getElementById('filter' + capitalKey).value;
    var selected = val === 'ALL' ? [] : val.split(',');
    _msSelected[key] = selected.slice();
    var box = document.getElementById('msCheckboxes_' + key);
    if (box) {{
      var cbs = box.querySelectorAll('input[type=checkbox]');
      cbs.forEach(function(cb) {{
        cb.checked = selected.length === 0 || selected.indexOf(cb.value) >= 0;
      }});
    }}
    updateMsTrigger(key);
  }});
  if (view.currentView && view.currentView !== currentView) switchView(view.currentView);
  else applyFilters();
}}
function deleteSavedView(name) {{
  if (!confirm('\u786e\u5b9a\u5220\u9664\u89c6\u56fe "' + name + '" \u5417\uff1f')) return;
  var views = getSavedViews().filter(function(v) {{ return v.name !== name; }});
  saveSavedViews(views);
  renderSavedViews();
}}
function renderSavedViews() {{
  var bar = document.getElementById('savedViewsBar');
  if (!bar) return;
  var views = getSavedViews();
  if (views.length === 0) {{ bar.innerHTML = ''; return; }}
  bar.innerHTML = '';
  views.forEach(function(v) {{
    var chip = document.createElement('span');
    chip.className = 'saved-view-chip';
    var safeName = v.name.replace(/'/g, "\\'");
    chip.innerHTML = '\U0001F4CC ' + escapeHtml(v.name) + '<span class="sv-delete" onclick="event.stopPropagation();deleteSavedView(\"' + safeName + '\")">\u2716</span>';
    chip.addEventListener('click', function() {{ loadSavedView(v.name); }});
    bar.appendChild(chip);
  }});
}}

// ======================== CARD EXPAND ========================
function toggleCardExpand(id) {{
  // Close any existing popup
  var existing = document.querySelector('.card-expand-overlay');
  if (existing) {{
    existing.remove();
    return;
  }}
  // Find the card data
  var cardEl = document.querySelector('.task-card[data-id="' + id + '"]');
  if (!cardEl) return;
  var row = DATA.find(function(r) {{ return r.id === id; }});
  if (!row) return;
  // Build popup HTML
  var regionTags = (row.region || []).map(function(x) {{ return '<span class="region-tag">' + x + '</span>'; }}).join('');
  var names = (row.assignee || []).map(function(p) {{ return p.name; }}).join(', ');
  var pTag = row.progress === '\u672a\u542f\u52a8' ? '<span class="tag tag-notstarted">\u672a\u542f\u52a8</span>' :
    row.progress === '\u8fdb\u884c\u4e2d' ? '<span class="tag tag-progress">\u8fdb\u884c\u4e2d</span>' :
    '<span class="tag tag-qa">' + escapeHtml(row.progress) + '</span>';
  var verName = VER_NAME_MAP[row.extVersion] || row.extVersion || '';
  var overlay = document.createElement('div');
  overlay.className = 'card-expand-overlay';
  overlay.innerHTML = '<div class="card-expand-popup">' +
    '<button class="popup-close" onclick="this.closest(\'.card-expand-overlay\').remove()">\u2715</button>' +
    '<div class="popup-title">' + escapeHtml(row.title) + (verName ? ' <span class="version-badge">' + escapeHtml(verName) + '</span>' : '') + '</div>' +
    '<div class="popup-meta">' + pTag + ' ' + regionTags + ' ' + renderJiraHtml(row) + '</div>' +
    buildCardExpandHtml(row) +
    '</div>';
  overlay.addEventListener('click', function(e) {{
    if (e.target === overlay) overlay.remove();
  }});
  document.body.appendChild(overlay);
}}
document.addEventListener('click', function(e) {{
  var card = e.target.closest('.task-card[data-id]');
  if (card && !e.target.closest('.jira-link') && !e.target.closest('a')) {{
    toggleCardExpand(card.getAttribute('data-id'));
  }}
}});
function buildCardExpandHtml(r) {{
  var html = '';
  if (r.jiraKey || r.jiraUrl) {{
    html += '<div class="card-expand-row"><span class="card-expand-label">Jira\u5355\u53f7</span><span class="card-expand-value">' + renderJiraHtml(r) + '</span></div>';
  }}
  if (r.extVersion) {{
    var evn = VER_NAME_MAP[r.extVersion] || r.extVersion;
    html += '<div class="card-expand-row"><span class="card-expand-label">\u5916\u653e\u7248\u672c</span><span class="card-expand-value"><span class="version-badge">' + escapeHtml(evn) + '</span></span></div>';
  }}
  if (r.testDate) {{
    html += '<div class="card-expand-row"><span class="card-expand-label">\u8f6c\u6d4b\u65f6\u95f4</span><span class="card-expand-value">' + r.testDate + '</span></div>';
  }}
  if (r.freezeDate) {{
    html += '<div class="card-expand-row"><span class="card-expand-label">\u5c01\u677f\u65f6\u95f4</span><span class="card-expand-value">' + r.freezeDate + '</span></div>';
  }}
  if (r.onlineDate) {{
    html += '<div class="card-expand-row"><span class="card-expand-label">\u4e0a\u7ebf\u65f6\u95f4</span><span class="card-expand-value">' + normalizeDate(r.onlineDate) + '</span></div>';
  }}
  if (r.parentTask) {{
    html += '<div class="card-expand-row"><span class="card-expand-label">\u7236\u4efb\u52a1</span><span class="card-expand-value">' + escapeHtml(r.parentTask) + '</span></div>';
  }}
  var names = (r.assignee || []).map(function(p) {{ return p.name; }}).join(', ');
  if (names) {{
    html += '<div class="card-expand-row"><span class="card-expand-label">\u6267\u884c\u4eba</span><span class="card-expand-value">' + escapeHtml(names) + '</span></div>';
  }}
  var regions = (r.region || []).join(', ');
  if (regions) {{
    html += '<div class="card-expand-row"><span class="card-expand-label">\u5730\u533a</span><span class="card-expand-value">' + escapeHtml(regions) + '</span></div>';
  }}
  return html;
}}

// ======================== JIRA STATUS ========================
var _jiraStatusCache = {{}};
function getJiraStatus(key) {{
  if (!key) return '';
  if (_jiraStatusCache[key]) return _jiraStatusCache[key];
  try {{
    var cached = JSON.parse(localStorage.getItem('rox_jira_status') || '{{}}');
    _jiraStatusCache = cached;
    return cached[key] || '';
  }} catch(e) {{ return ''; }}
}}
function renderJiraHtml(r) {{
  if (!r.jiraKey && !r.jiraUrl) return '';
  var key = r.jiraKey || '';
  var url = r.jiraUrl || '';
  // Extract URL from markdown format [KEY](URL)
  if (url && url.indexOf('](') >= 0) {{
    // Extract key from markdown first (before URL is replaced)
    if (!key) {{
      var km = url.match(/\[([^\]]+)\]/);
      if (km) key = km[1];
    }}
    // Extract URL from markdown
    var m = url.match(/\]\(([^)]+)\)/);
    if (m) url = m[1];
  }}
  // If jiraUrl is actually a plain URL (no markdown), use it as-is
  // If key is still empty, try to extract from URL path
  if (!key && url) {{
    var lastPart = url.split('/').pop();
    if (lastPart && lastPart.indexOf('ROCN-') === 0) key = lastPart;
  }}
  var status = getJiraStatus(key);
  var statusHtml = '';
  if (status) {{
    var cls = 'todo';
    if (status.indexOf('\u8fdb\u884c') >= 0 || status.indexOf('In Prog') >= 0) cls = 'progress';
    else if (status.indexOf('\u5b8c\u6210') >= 0 || status.indexOf('Done') >= 0 || status.indexOf('Closed') >= 0) cls = 'done';
    statusHtml = '<span class="jira-status ' + cls + '">' + escapeHtml(status) + '</span>';
  }}
  if (url) return '<a class="jira-link" href="' + escapeHtml(url) + '" target="_blank" title="\u6253\u5f00 Jira">\U0001F3AF ' + escapeHtml(key) + statusHtml + '</a>';
  return '<span class="jira-link">\U0001F3AF ' + escapeHtml(key) + statusHtml + '</span>';
}}
function renderVersionHtml(r) {{
  if (!r.extVersion) return '';
  var vn = VER_NAME_MAP[r.extVersion] || r.extVersion;
  return ' <span class="version-badge">' + escapeHtml(vn) + '</span>';
}}

// ======================== JIRA VIEW ========================
var _jiraViewInited = false;
function initJiraView() {{
  if (_jiraViewInited) return;
  _jiraViewInited = true;
  // Populate person filter
  var pSel = document.getElementById('jiraPersonFilter');
  var peopleSet = {{}};
  DATA.forEach(function(r) {{
    (r.assignee || []).forEach(function(p) {{
      if (p.name) peopleSet[p.name] = true;
    }});
  }});
  Object.keys(peopleSet).sort().forEach(function(name) {{
    var opt = document.createElement('option');
    opt.value = name; opt.textContent = name;
    pSel.appendChild(opt);
  }});
  // Populate version filter
  var vSel = document.getElementById('jiraVersionFilter');
  allVersions.forEach(function(v) {{
    var opt = document.createElement('option');
    opt.value = v; opt.textContent = v;
    vSel.appendChild(opt);
  }});
}}

function renderJiraView() {{
  var personVal = document.getElementById('jiraPersonFilter').value;
  var versionVal = document.getElementById('jiraVersionFilter').value;
  var searchVal = (document.getElementById('jiraSearchInput').value || '').toLowerCase().trim();

  // Filter tasks that have Jira keys
  var tasks = DATA.filter(function(r) {{
    if (!r.jiraKey && !r.jiraUrl) return false;
    if (personVal !== 'ALL') {{
      var names = (r.assignee || []).map(function(p) {{ return p.name; }});
      if (names.indexOf(personVal) < 0) return false;
    }}
    if (versionVal !== 'ALL') {{
      var vn = VER_NAME_MAP[r.extVersion] || r.extVersion;
      if (vn !== versionVal) return false;
    }}
    if (searchVal && !fuzzyMatch(r.title, searchVal) && !(r.jiraKey || '').toLowerCase().indexOf(searchVal) >= 0) return false;
    return true;
  }});

  // Stats
  var statsEl = document.getElementById('jiraStats');
  var totalJira = tasks.length;
  var peopleSet = {{}};
  var versionSet = {{}};
  var progressCount = {{ todo: 0, progress: 0, done: 0, other: 0 }};
  tasks.forEach(function(r) {{
    (r.assignee || []).forEach(function(p) {{ if (p.name) peopleSet[p.name] = true; }});
    if (r.extVersion) versionSet[r.extVersion] = true;
    var p = (r.progress || '').toLowerCase();
    if (p.indexOf('\u5b8c\u6210') >= 0 || p.indexOf('done') >= 0 || p.indexOf('closed') >= 0) progressCount.done++;
    else if (p.indexOf('\u8fdb\u884c') >= 0 || p.indexOf('in prog') >= 0) progressCount.progress++;
    else if (p.indexOf('\u672a\u542f\u52a8') >= 0 || p === '') progressCount.todo++;
    else progressCount.other++;
  }});
  statsEl.innerHTML =
    '<div class="stat-item"><span class="stat-num">' + totalJira + '</span><span class="stat-label">Jira\u4efb\u52a1\u603b\u6570</span></div>' +
    '<div class="stat-item"><span class="stat-num">' + Object.keys(peopleSet).length + '</span><span class="stat-label">\u6d89\u53ca\u4eba\u5458</span></div>' +
    '<div class="stat-item"><span class="stat-num">' + Object.keys(versionSet).length + '</span><span class="stat-label">\u6d89\u53ca\u7248\u672c</span></div>' +
    '<div class="stat-item"><span class="stat-num" style="color:cornflowerblue">' + progressCount.progress + '</span><span class="stat-label">\u8fdb\u884c\u4e2d</span></div>' +
    '<div class="stat-item"><span class="stat-num" style="color:mediumseagreen">' + progressCount.done + '</span><span class="stat-label">\u5df2\u5b8c\u6210</span></div>';

  // Table
  var wrap = document.getElementById('jiraTableWrap');
  if (tasks.length === 0) {{
    wrap.innerHTML = '<div class="jira-empty">\u6682\u65e0\u5339\u914d\u7684Jira\u4efb\u52a1</div>';
    return;
  }}
  // Sort by version date desc
  tasks.sort(function(a, b) {{ return (b.versionDate || '').localeCompare(a.versionDate || ''); }});

  var html = '<table class="jira-table"><thead><tr>' +
    '<th>\u5de5\u4f5c\u5185\u5bb9</th>' +
    '<th>Jira\u5355\u53f7</th>' +
    '<th>\u72b6\u6001</th>' +
    '<th>\u6267\u884c\u4eba</th>' +
    '<th>\u5730\u533a</th>' +
    '<th>\u5916\u653e\u7248\u672c</th>' +
    '<th>\u7248\u66f4\u65f6\u95f4</th>' +
    '<th>\u4e0a\u7ebf\u65f6\u95f4</th>' +
    '</tr></thead><tbody>';
  tasks.forEach(function(r) {{
    var pCls = 'todo';
    var p = (r.progress || '');
    if (p.indexOf('\u8fdb\u884c') >= 0) pCls = 'progress';
    else if (p.indexOf('\u5b8c\u6210') >= 0 || p.indexOf('Done') >= 0) pCls = 'done';
    var names = (r.assignee || []).map(function(p) {{ return '<span class="jira-person-badge">' + escapeHtml(p.name) + '</span>'; }}).join(' ');
    var regions = (r.region || []).join(', ');
    html += '<tr>' +
      '<td>' + escapeHtml(r.title) + '</td>' +
      '<td class="jira-key-cell">' + renderJiraHtml(r) + '</td>' +
      '<td><span class="jira-progress-tag ' + pCls + '">' + escapeHtml(p) + '</span></td>' +
      '<td>' + names + '</td>' +
      '<td>' + escapeHtml(regions) + '</td>' +
      '<td>' + (r.extVersion ? '<span class="version-badge">' + escapeHtml(VER_NAME_MAP[r.extVersion] || r.extVersion) + '</span>' : '-') + '</td>' +
      '<td>' + (r.versionDate || '-') + '</td>' +
      '<td>' + normalizeDate(r.onlineDate) + '</td>' +
      '</tr>';
  }});
  html += '</tbody></table>';
  wrap.innerHTML = html;
}}

// ======================== START ========================
// Load admin tasks from local storage
loadAdminTasks();
init();
</script>
</body>
</html>'''

    # ======================== WRITE HTML ========================
    os.makedirs('/tmp/rox-schedule', exist_ok=True)
    with open('/tmp/rox-schedule/index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'Base HTML generated: /tmp/rox-schedule/index.html ({len(html)} bytes)')
    print(f'Total records: {len(records)}')

if __name__ == '__main__':
    main()