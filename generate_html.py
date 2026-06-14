#!/usr/bin/env python3
"""
Generate ROX project schedule HTML from clean_data.json
"""

import json
import os

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
            'id': r.get('_id', '')
        })

    # Serialize to JSON string for safe embedding
    # Use ensure_ascii=False so Chinese chars remain readable in the HTML source
    data_json_str = json.dumps(records, ensure_ascii=False)
    # Escape for embedding in a <script type="application/json"> block
    # Only need to escape </script> which would break HTML parsing
    data_json_safe = data_json_str.replace('</', '<\\/')

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
:root {{
  --primary: #3370FF;
  --primary-light: #5890FF;
  --primary-dark: #2858CC;
  --primary-bg: #F0F5FF;
  --success: #34C759;
  --warning: #FF9500;
  --danger: #FF3B30;
  --gray-1: #F7F8FA;
  --gray-2: #F2F3F5;
  --gray-3: #E5E6EB;
  --gray-4: #C9CDD4;
  --gray-5: #86909C;
  --gray-6: #4E5969;
  --gray-7: #1D2129;
  --radius-sm: 6px;
  --radius-md: 10px;
  --radius-lg: 14px;
  --shadow-sm: 0 1px 3px rgba(0,0,0,0.06);
  --shadow-md: 0 4px 12px rgba(0,0,0,0.08);
  --shadow-lg: 0 8px 24px rgba(0,0,0,0.12);
  --font: -apple-system, "PingFang SC", "Noto Sans SC", "Microsoft YaHei", sans-serif;
  --transition: all 0.25s ease;
}}
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{
  font-family: var(--font);
  background: var(--gray-1);
  color: var(--gray-7);
  line-height: 1.6;
  min-height: 100vh;
}}

/* ========== HEADER ========== */
.header {{
  background: linear-gradient(135deg, var(--primary), var(--primary-dark));
  color: #fff;
  padding: 18px 32px;
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 2px 8px rgba(51,112,255,0.3);
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
  font-size: 20px;
  font-weight: 600;
  letter-spacing: 0.5px;
}}
.header h1 small {{
  font-weight: 300;
  opacity: 0.85;
  font-size: 13px;
  margin-left: 10px;
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
}}

/* ========== BUTTONS ========== */
.btn {{
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 7px 16px;
  border: none;
  border-radius: var(--radius-sm);
  font-size: 13px;
  font-family: var(--font);
  cursor: pointer;
  transition: var(--transition);
  font-weight: 500;
  white-space: nowrap;
}}
.btn-primary {{
  background: #fff;
  color: var(--primary);
}}
.btn-primary:hover {{
  background: var(--primary-bg);
  transform: translateY(-1px);
}}
.btn-outline {{
  background: transparent;
  color: #fff;
  border: 1.5px solid rgba(255,255,255,0.5);
}}
.btn-outline:hover {{
  border-color: #fff;
  background: rgba(255,255,255,0.1);
}}
.btn-sm {{
  padding: 4px 10px;
  font-size: 12px;
}}
.btn-primary-solid {{
  background: var(--primary);
  color: #fff;
}}
.btn-primary-solid:hover {{
  background: var(--primary-dark);
}}
.btn-danger {{
  background: var(--danger);
  color: #fff;
}}
.btn-danger:hover {{
  opacity: 0.85;
}}
.btn-success {{
  background: var(--success);
  color: #fff;
}}
.btn-success:hover {{
  opacity: 0.85;
}}

/* ========== STAT CARDS ========== */
.stats-row {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 14px;
  margin-bottom: 20px;
}}
.stat-card {{
  background: #fff;
  border-radius: var(--radius-md);
  padding: 18px 20px;
  box-shadow: var(--shadow-sm);
  border-left: 4px solid var(--primary);
  transition: var(--transition);
}}
.stat-card:hover {{
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}}
.stat-card .label {{
  font-size: 13px;
  color: var(--gray-5);
  margin-bottom: 6px;
}}
.stat-card .value {{
  font-size: 28px;
  font-weight: 700;
  color: var(--gray-7);
}}
.stat-card .sub {{
  font-size: 12px;
  color: var(--gray-5);
  margin-top: 4px;
}}
.stat-card:nth-child(1) {{ border-left-color: var(--primary); }}
.stat-card:nth-child(2) {{ border-left-color: var(--warning); }}
.stat-card:nth-child(3) {{ border-left-color: var(--success); }}
.stat-card:nth-child(4) {{ border-left-color: var(--gray-5); }}
.stat-card:nth-child(5) {{ border-left-color: var(--danger); }}
.stat-card:nth-child(6) {{ border-left-color: var(--gray-7); }}

/* ========== FILTER BAR ========== */
.filter-bar {{
  background: #fff;
  border-radius: var(--radius-md);
  padding: 14px 18px;
  box-shadow: var(--shadow-sm);
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
  font-size: 13px;
  color: var(--gray-6);
  font-weight: 500;
  white-space: nowrap;
}}
.filter-group select {{
  padding: 5px 10px;
  border: 1px solid var(--gray-3);
  border-radius: var(--radius-sm);
  font-size: 13px;
  font-family: var(--font);
  background: #fff;
  color: var(--gray-7);
  cursor: pointer;
  outline: none;
  min-width: 100px;
}}
.filter-group select:focus {{
  border-color: var(--primary);
  box-shadow: 0 0 0 2px var(--primary-bg);
}}
.filter-search {{
  padding: 5px 10px;
  border: 1px solid var(--gray-3);
  border-radius: var(--radius-sm);
  font-size: 13px;
  font-family: var(--font);
  outline: none;
  flex: 1;
  min-width: 160px;
}}
.filter-search:focus {{
  border-color: var(--primary);
  box-shadow: 0 0 0 2px var(--primary-bg);
}}
.filter-stats {{
  font-size: 12px;
  color: var(--gray-5);
  margin-left: auto;
  white-space: nowrap;
}}

/* ========== VIEW TABS ========== */
.view-tabs {{
  display: flex;
  gap: 4px;
  margin-bottom: 16px;
  background: var(--gray-2);
  border-radius: var(--radius-sm);
  padding: 3px;
  width: fit-content;
}}
.view-tab {{
  padding: 7px 18px;
  border: none;
  border-radius: 4px;
  font-size: 13px;
  font-family: var(--font);
  cursor: pointer;
  transition: var(--transition);
  background: transparent;
  color: var(--gray-6);
  font-weight: 500;
}}
.view-tab.active {{
  background: #fff;
  color: var(--primary);
  box-shadow: var(--shadow-sm);
}}
.view-tab:hover:not(.active) {{
  color: var(--gray-7);
}}

/* ========== TABLE VIEW ========== */
.table-wrapper {{
  background: #fff;
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
  overflow-x: auto;
}}
table {{
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}}
table th, table td {{
  padding: 10px 14px;
  text-align: left;
  border-bottom: 1px solid var(--gray-3);
  white-space: nowrap;
}}
table th {{
  background: var(--gray-1);
  font-weight: 600;
  color: var(--gray-6);
  position: sticky;
  top: 0;
  cursor: pointer;
  user-select: none;
}}
table th:hover {{
  color: var(--primary);
}}
table th .sort-icon {{
  margin-left: 4px;
  font-size: 10px;
  opacity: 0.4;
}}
table th .sort-icon.active {{
  opacity: 1;
  color: var(--primary);
}}
table tr:hover td {{
  background: var(--primary-bg);
}}
table tr:last-child td {{
  border-bottom: none;
}}

/* ========== TAGS ========== */
.tag {{
  display: inline-block;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 500;
}}
.tag-notstarted {{
  background: #F2F3F5;
  color: var(--gray-5);
}}
.tag-progress {{
  background: #FFF7E8;
  color: #B8860B;
}}
.tag-qa {{
  background: #E8F5E9;
  color: #2E7D32;
}}
.region-tag {{
  display: inline-block;
  padding: 1px 6px;
  border-radius: 4px;
  font-size: 11px;
  background: var(--gray-2);
  color: var(--gray-6);
  margin-right: 2px;
}}
.assignee-name {{
  font-weight: 500;
}}

/* ========== CARD VIEW ========== */
.card-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 12px;
}}
.task-card {{
  background: #fff;
  border-radius: var(--radius-md);
  padding: 14px 16px;
  box-shadow: var(--shadow-sm);
  border-left: 4px solid var(--gray-3);
  transition: var(--transition);
  cursor: default;
}}
.task-card:hover {{
  box-shadow: var(--shadow-md);
}}
.task-card.card-notstarted {{ border-left-color: var(--gray-3); }}
.task-card.card-progress {{ border-left-color: var(--warning); }}
.task-card.card-qa {{ border-left-color: var(--success); }}
.task-card .card-title {{
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 8px;
  line-height: 1.4;
}}
.task-card .card-meta {{
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  font-size: 12px;
  color: var(--gray-5);
}}
.task-card .card-meta span {{
  display: flex;
  align-items: center;
  gap: 3px;
}}

/* ========== GANTT ========== */
.gantt-wrapper {{
  background: #fff;
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
  padding: 16px;
  overflow-x: auto;
}}
.gantt-container {{
  min-width: 100%;
  position: relative;
}}
.gantt-header {{
  display: flex;
  position: sticky;
  top: 0;
  z-index: 10;
  background: #fff;
  border-bottom: 2px solid var(--gray-3);
}}
.gantt-person-col {{
  min-width: 120px;
  max-width: 120px;
  padding: 8px 10px;
  font-weight: 600;
  font-size: 13px;
  color: var(--gray-6);
  border-right: 1px solid var(--gray-3);
  flex-shrink: 0;
}}
.gantt-timeline {{
  flex: 1;
  display: flex;
  position: relative;
  min-height: 36px;
}}
.gantt-week-label {{
  flex: 1;
  text-align: center;
  padding: 6px 0;
  font-size: 11px;
  color: var(--gray-5);
  border-right: 1px solid var(--gray-3);
  font-weight: 500;
}}
.gantt-week-label.today {{
  background: var(--primary-bg);
  font-weight: 700;
  color: var(--primary);
}}
.gantt-person-group {{
  display: flex;
  border-bottom: 1px solid var(--gray-2);
}}
.gantt-person-group:hover {{
  background: #FAFBFF;
}}
.gantt-person-name {{
  min-width: 120px;
  max-width: 120px;
  padding: 8px 10px;
  font-size: 13px;
  font-weight: 500;
  color: var(--gray-7);
  border-right: 1px solid var(--gray-3);
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 4px;
}}
.gantt-person-name .dept-tag {{
  font-size: 10px;
  color: var(--gray-5);
  font-weight: 400;
}}
.gantt-row-timeline {{
  flex: 1;
  position: relative;
  min-height: 44px;
}}
.gantt-bar {{
  position: absolute;
  height: 26px;
  border-radius: 4px;
  top: 9px;
  cursor: pointer;
  transition: var(--transition);
  display: flex;
  align-items: center;
  padding: 0 6px;
  font-size: 10px;
  color: #fff;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  z-index: 2;
}}
.gantt-bar:hover {{
  filter: brightness(1.15);
  transform: scaleY(1.1);
  z-index: 5;
}}
.gantt-bar.progress-notstarted {{ background: var(--gray-4); color: var(--gray-6); }}
.gantt-bar.progress-progress {{ background: var(--warning); }}
.gantt-bar.progress-qa {{ background: var(--success); }}
.gantt-milestone {{
  position: absolute;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  top: 17px;
  z-index: 3;
  cursor: pointer;
  transform: translateX(-50%);
}}
.gantt-milestone.test {{ background: var(--danger); border: 2px solid #fff; box-shadow: 0 0 0 1px var(--danger); }}
.gantt-milestone.freeze {{ background: var(--warning); border: 2px solid #fff; box-shadow: 0 0 0 1px var(--warning); }}
.gantt-milestone.version {{ background: var(--primary); border: 2px solid #fff; box-shadow: 0 0 0 1px var(--primary); }}
.gantt-tooltip {{
  position: fixed;
  background: var(--gray-7);
  color: #fff;
  padding: 10px 14px;
  border-radius: var(--radius-sm);
  font-size: 12px;
  line-height: 1.5;
  z-index: 9999;
  max-width: 360px;
  pointer-events: none;
  box-shadow: var(--shadow-lg);
  display: none;
}}
.gantt-tooltip .tt-title {{
  font-weight: 600;
  font-size: 13px;
  margin-bottom: 4px;
}}
.gantt-tooltip .tt-row {{
  display: flex;
  justify-content: space-between;
  gap: 12px;
  opacity: 0.85;
}}
.gantt-gridlines {{
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 0;
  display: flex;
}}
.gantt-gridline {{
  flex: 1;
  border-right: 1px dashed var(--gray-2);
}}
.gantt-gridline:last-child {{ border-right: none; }}

/* ========== MODALS ========== */
.modal-overlay {{
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.5);
  z-index: 200;
  display: none;
  align-items: center;
  justify-content: center;
}}
.modal-overlay.active {{
  display: flex;
}}
.modal {{
  background: #fff;
  border-radius: var(--radius-lg);
  padding: 28px 32px;
  max-width: 520px;
  width: 90%;
  box-shadow: var(--shadow-lg);
  max-height: 90vh;
  overflow-y: auto;
}}
.modal h2 {{
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 18px;
  color: var(--gray-7);
}}
.form-group {{
  margin-bottom: 14px;
}}
.form-group label {{
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: var(--gray-6);
  margin-bottom: 4px;
}}
.form-group input, .form-group select, .form-group textarea {{
  width: 100%;
  padding: 8px 12px;
  border: 1px solid var(--gray-3);
  border-radius: var(--radius-sm);
  font-size: 13px;
  font-family: var(--font);
  outline: none;
  transition: var(--transition);
}}
.form-group input:focus, .form-group select:focus, .form-group textarea:focus {{
  border-color: var(--primary);
  box-shadow: 0 0 0 2px var(--primary-bg);
}}
.form-group textarea {{
  min-height: 60px;
  resize: vertical;
}}
.form-row {{
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}}
.form-actions {{
  display: flex;
  gap: 8px;
  justify-content: flex-end;
  margin-top: 18px;
}}

/* ========== ADMIN TASK LIST ========== */
.admin-task-list {{
  max-height: 300px;
  overflow-y: auto;
  margin-bottom: 10px;
}}
.admin-task-item {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px 8px;
  border-bottom: 1px solid var(--gray-2);
  font-size: 12px;
}}
.admin-task-item:last-child {{ border-bottom: none; }}
.admin-task-item .at-title {{
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}}
.admin-task-item .at-actions {{
  display: flex;
  gap: 4px;
}}

/* ========== EMPTY STATE ========== */
.empty-state {{
  text-align: center;
  padding: 60px 20px;
  color: var(--gray-5);
}}
.empty-state .empty-icon {{
  font-size: 48px;
  margin-bottom: 12px;
  display: block;
  opacity: 0.4;
}}

/* ========== MISC ========== */
.fade-in {{ animation: fadeIn 0.3s ease; }}
@keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(8px); }} to {{ opacity: 1; transform: translateY(0); }} }}
.badge {{
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 20px;
  height: 20px;
  padding: 0 6px;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 600;
}}
.badge-primary {{ background: var(--primary-bg); color: var(--primary); }}
.badge-warning {{ background: #FFF7E8; color: #B8860B; }}
.badge-success {{ background: #E8F5E9; color: #2E7D32; }}
.priority-high {{ color: var(--danger); font-weight: 600; }}
.priority-medium {{ color: var(--warning); font-weight: 600; }}
.priority-low {{ color: var(--gray-5); }}
.schedule-result {{
  background: var(--primary-bg);
  border-radius: var(--radius-sm);
  padding: 10px 12px;
  font-size: 13px;
  margin-bottom: 10px;
  display: none;
}}

/* ========== RESPONSIVE ========== */
@media (max-width: 768px) {{
  .header-inner {{ flex-direction: column; align-items: flex-start; }}
  .header-actions {{ width: 100%; }}
  .stats-row {{ grid-template-columns: repeat(2, 1fr); }}
  .filter-bar {{ flex-direction: column; align-items: stretch; }}
  .filter-stats {{ margin-left: 0; }}
  .form-row {{ grid-template-columns: 1fr; }}
  .card-grid {{ grid-template-columns: 1fr; }}
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
    <div class="filter-group">
      <label>\u5730\u533a</label>
      <select id="filterRegion" onchange="applyFilters()">
        <option value="">\u5168\u90e8</option>
      </select>
    </div>
    <div class="filter-group">
      <label>\u8fdb\u5c55</label>
      <select id="filterProgress" onchange="applyFilters()">
        <option value="">\u5168\u90e8</option>
      </select>
    </div>
    <div class="filter-group">
      <label>\u6267\u884c\u4eba</label>
      <select id="filterPerson" onchange="applyFilters()">
        <option value="">\u5168\u90e8</option>
      </select>
    </div>
    <div class="filter-group">
      <label>\u641c\u7d22</label>
      <input type="text" class="filter-search" id="filterSearch" placeholder="\u641c\u7d22\u5de5\u4f5c\u5185\u5bb9..." oninput="applyFilters()">
    </div>
    <div class="filter-stats" id="filterStats"></div>
  </div>

  <!-- View Tabs -->
  <div class="view-tabs">
    <button class="view-tab active" data-view="card" onclick="switchView('card')">\u5361\u7247\u89c6\u56fe</button>
    <button class="view-tab" data-view="table" onclick="switchView('table')">\u8868\u683c\u89c6\u56fe</button>
    <button class="view-tab" data-view="gantt" onclick="switchView('gantt')">\u7518\u7279\u56fe</button>
  </div>

  <!-- Content Area -->
  <div id="cardView" class="fade-in"></div>
  <div id="tableView" class="fade-in" style="display:none"></div>
  <div id="ganttView" class="fade-in" style="display:none"></div>
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

<!-- ========== GANTT TOOLTIP ========== -->
<div class="gantt-tooltip" id="ganttTooltip"></div>

<!-- ========== DATA EMBEDDED AS JSON ========== -->
<script id="__DATA__" type="application/json">{data_json_safe}</script>
<script id="__PEOPLE__" type="application/json">{people_json_safe}</script>

<!-- ========== APPLICATION SCRIPT ========== -->
<script>
// ======================== DATA LOADING ========================
var DATA = JSON.parse(document.getElementById('__DATA__').textContent);
var ALL_PEOPLE = JSON.parse(document.getElementById('__PEOPLE__').textContent);


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
  // Order progress in a meaningful way
  var progOrder = ['\\u672a\\u542f\\u52a8', '\\u8fdb\\u884c\\u4e2d', 'QA\\u9a8c\\u6536\\u4e2d'];
  allProgress = progOrder.filter(function(p) {{ return progSet[p]; }});
  if (allProgress.length === 0) allProgress = Object.keys(progSet);
  // allPeople derived from ALL_PEOPLE
  allPeople = ALL_PEOPLE.map(function(p) {{ return p.name; }});

  // Populate filter selects
  var selRegion = document.getElementById('filterRegion');
  allRegions.forEach(function(r) {{
    var opt = document.createElement('option');
    opt.value = r; opt.textContent = r;
    selRegion.appendChild(opt);
  }});
  var selProg = document.getElementById('filterProgress');
  allProgress.forEach(function(p) {{
    var opt = document.createElement('option');
    opt.value = p; opt.textContent = p;
    selProg.appendChild(opt);
  }});

  // Populate person filter from ALL_PEOPLE, grouped by department
  var selPerson = document.getElementById('filterPerson');
  // Group by dept
  var deptMap = {{}};
  ALL_PEOPLE.forEach(function(p) {{
    if (!deptMap[p.dept]) deptMap[p.dept] = [];
    deptMap[p.dept].push(p);
  }});
  var sortedDepts = Object.keys(deptMap).sort();
  sortedDepts.forEach(function(dept) {{
    var optgroup = document.createElement('optgroup');
    optgroup.label = dept;
    deptMap[dept].sort(function(a,b) {{ return a.name.localeCompare(b.name); }}).forEach(function(p) {{
      var opt = document.createElement('option');
      opt.value = p.name;
      opt.textContent = dept + ' - ' + p.name;
      optgroup.appendChild(opt);
    }});
    selPerson.appendChild(optgroup);
  }});

  // Populate person select for admin form (use same grouped list)
  var selAP = document.getElementById('newTaskPerson');
  sortedDepts.forEach(function(dept) {{
    var optgroup = document.createElement('optgroup');
    optgroup.label = dept;
    deptMap[dept].sort(function(a,b) {{ return a.name.localeCompare(b.name); }}).forEach(function(p) {{
      var opt = document.createElement('option');
      opt.value = p.name;
      opt.textContent = dept + ' - ' + p.name;
      optgroup.appendChild(opt);
    }});
    selAP.appendChild(optgroup);
  }});

  // Set default deadline to 7 days from now
  var deadlineEl = document.getElementById('newTaskDeadline');
  var future = new Date();
  future.setDate(future.getDate() + 7);
  deadlineEl.value = formatDateISO(future);

  document.getElementById('headerInfo').textContent = DATA.length + ' \\u4e2a\\u4efb\\u52a1 | ' + allPeople.length + ' \\u4eba';

  render();
}}

// ======================== FILTER ========================
function getFilteredData() {{
  var region = document.getElementById('filterRegion').value;
  var progress = document.getElementById('filterProgress').value;
  var person = document.getElementById('filterPerson').value;
  var search = document.getElementById('filterSearch').value.trim().toLowerCase();

  var filtered = DATA.filter(function(r) {{
    if (region && (!r.region || r.region.indexOf(region) === -1)) return false;
    if (progress && r.progress !== progress) return false;
    if (person) {{
      if (!r.assignee || !r.assignee.some(function(p) {{ return p.name === person; }})) return false;
    }} else {{
      // When "\u5168\u90e8" is selected, show all (default behavior)
    }}
    if (search && r.title.toLowerCase().indexOf(search) === -1) return false;
    return true;
  }});

  // Include admin tasks in filtered results
  var adminFiltered = adminTasks.filter(function(t) {{
    if (region && t.region !== region) return false;
    if (progress && t.progress !== progress) return false;
    if (person && t.assigneeName !== person) return false;
    if (search && t.title.toLowerCase().indexOf(search) === -1) return false;
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

  if (currentView === 'card') renderCard(filtered, adminFiltered);
  else if (currentView === 'table') renderTable(filtered, adminFiltered);
  else if (currentView === 'gantt') renderGantt(filtered, adminFiltered);
}}

function applyFilters() {{
  render();
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
    if (r.startDate) dates.push('\\u{{1F4C5}} ' + normalizeDate(r.startDate));
    if (r.freezeDate) dates.push('\\u{{1F4C4}} \\u5c01\\u677f: ' + r.freezeDate);
    if (r.versionDate) dates.push('\\u{{1F4C5}} \\u7248\\u66f4: ' + r.versionDate);

    html += '<div class="task-card ' + cls + '">';
    html += '<div class="card-title">' + escapeHtml(r.title) + '</div>';
    html += '<div class="card-meta">' + pTag + regionTags + '</div>';
    html += '<div class="card-meta" style="margin-top:4px"><span>\\u{{1F465}} ' + escapeHtml(names) + '</span></div>';
    if (dates.length) html += '<div class="card-meta" style="margin-top:4px">' + dates.join(' | ') + '</div>';
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
    {{ key: 'freezeDate', label: '\\u5c01\\u677f\\u65f6\\u95f4', width: '110px' }},
    {{ key: 'versionDate', label: '\\u7248\\u66f4\\u65f6\\u95f4', width: '110px' }}
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
    html += '<td>' + (r.freezeDate || '') + '</td>';
    html += '<td>' + (r.versionDate || '') + '</td></tr>';
  }});

  if (!all.length) {{
    html += '<tr><td colspan="7" style="text-align:center;padding:40px;color:var(--gray-5)">\\u6682\\u65e0\\u5339\\u914d\\u7684\\u4efb\\u52a1</td></tr>';
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
    html += '<div class="gantt-person-name">' + escapeHtml(pName) + ' <span class="dept-tag">(' + tasks.length + ')</span></div>';
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
  ['cardView','tableView','ganttView'].forEach(function(id) {{
    document.getElementById(id).style.display = id.indexOf(view) === 0 ? 'block' : 'none';
  }});
  render();
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
    print(f'HTML generated: /tmp/rox-schedule/index.html ({len(html)} bytes)')
    print(f'Total records: {len(records)}')

if __name__ == '__main__':
    main()