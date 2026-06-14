#!/usr/bin/env python3
"""
HTML post-processor for ROX schedule board.
Adds person view, FAB add button, add task form, and delete buttons.
Usage: python3 enhance_html.py <input.html> [output.html]
"""
import re
import sys

def enhance_html(html):
    """Apply all enhancements to the HTML content."""

    # 1. ADD CSS for person view, FAB button, add panel, delete btn
    css_blocks = (
        '\n/* ========== PERSON VIEW ========== */\n'
        '.person-dept-group { margin-bottom:16px;background:#fff;border-radius:var(--radius-md);box-shadow:var(--shadow-sm);overflow:hidden }\n'
        '.person-dept-header { background:var(--gray-2);padding:10px 16px;font-size:14px;font-weight:600;color:var(--gray-6);display:flex;align-items:center;gap:8px }\n'
        '.person-dept-header .dept-count { font-weight:400;font-size:12px;color:var(--gray-5) }\n'
        '.person-item { display:flex;align-items:flex-start;padding:10px 16px;border-bottom:1px solid var(--gray-2);transition:var(--transition) }\n'
        '.person-item:last-child { border-bottom:none }\n'
        '.person-item:hover { background:var(--gray-1) }\n'
        '.person-avatar { width:36px;height:36px;border-radius:50%;background:linear-gradient(135deg,var(--primary),var(--primary-light));color:#fff;display:flex;align-items:center;justify-content:center;font-size:14px;font-weight:600;flex-shrink:0;margin-right:12px }\n'
        '.person-info { flex:1;min-width:0 }\n'
        '.person-name { font-size:14px;font-weight:600;color:var(--gray-7);margin-bottom:2px }\n'
        '.person-task-count { font-size:12px;color:var(--gray-5) }\n'
        '.person-tasks { padding-left:48px }\n'
        '.person-task-card { padding:8px 12px;margin:4px 0;background:var(--gray-1);border-radius:var(--radius-sm);border-left:3px solid var(--gray-4);font-size:13px;display:flex;align-items:center;gap:8px }\n'
        '.person-task-card.card-progress { border-left-color:var(--warning) }\n'
        '.person-task-card.card-notstarted { border-left-color:var(--primary) }\n'
        '.person-task-card.card-qa { border-left-color:var(--success) }\n'
        '.person-task-title { flex:1;color:var(--gray-7) }\n'
        '.person-task-meta { font-size:11px;color:var(--gray-5);white-space:nowrap }\n'
        '.person-no-tasks { padding:6px 12px 6px 48px;font-size:12px;color:var(--gray-4);font-style:italic }\n'
        '\n/* ========== FLOATING ADD BUTTON ========== */\n'
        '.fab-add { position:fixed;bottom:28px;right:28px;width:52px;height:52px;border-radius:50%;'
        'background:linear-gradient(135deg,var(--primary),var(--primary-dark));color:#fff;'
        'font-size:28px;font-weight:300;display:flex;align-items:center;justify-content:center;'
        'cursor:pointer;box-shadow:0 4px 16px rgba(51,112,255,0.4);z-index:200;'
        'transition:var(--transition);user-select:none }\n'
        '.fab-add:hover { transform:scale(1.1) rotate(90deg);box-shadow:0 6px 24px rgba(51,112,255,0.5) }\n'
        '\n/* ========== INLINE ADD TASK PANEL ========== */\n'
        '.add-task-panel { position:fixed;bottom:90px;right:24px;width:380px;max-width:92vw;'
        'background:#fff;border-radius:var(--radius-lg);box-shadow:var(--shadow-lg);'
        'z-index:199;overflow:hidden;animation:slideUp .3s ease }\n'
        '@keyframes slideUp { from{opacity:0;transform:translateY(20px)} to{opacity:1;transform:translateY(0)} }\n'
        '.add-task-header { display:flex;align-items:center;justify-content:space-between;padding:12px 16px;background:var(--gray-1);font-size:14px;font-weight:600 }\n'
        '.add-task-close { background:none;border:none;font-size:18px;cursor:pointer;color:var(--gray-5);padding:2px 6px;border-radius:4px }\n'
        '.add-task-close:hover { background:var(--gray-3) }\n'
        '.add-task-body { padding:12px 16px 16px }\n'
        '.add-task-row { margin-bottom:6px }\n'
        '\n/* ========== DELETE BUTTON ========== */\n'
        '.delete-btn { background:none;border:none;cursor:pointer;font-size:14px;color:var(--gray-4);padding:2px 6px;border-radius:4px;transition:var(--transition);opacity:.4;flex-shrink:0 }\n'
        '.delete-btn:hover { color:var(--danger);opacity:1;background:rgba(255,59,48,.08) }\n'
        '.card-delete { position:absolute;top:6px;right:6px }\n'
        '.table-delete { padding:2px 8px }\n'
        '.person-task-card .delete-btn { opacity:.2 }\n'
        '.person-task-card:hover .delete-btn { opacity:.6 }\n'
    )

    css_insert_marker = '/* ========== RESPONSIVE ========== */'
    html = html.replace(css_insert_marker, css_blocks + '\n' + css_insert_marker)

    # 2. ADD person view tab between card and table
    html = html.replace(
        # Insert person view tab after card view tab
        'onclick="switchView(\'card\')">卡片视图</button>',
        'onclick="switchView(\'card\')">卡片视图</button>\n    <button class="view-tab" data-view="person" onclick="switchView(\'person\')">人员视图</button>'
    )


    # 3. ADD personView content div
    html = html.replace(
        '<div id="tableView" class="fade-in" style="display:none"></div>\n'
        '  <div id="ganttView" class="fade-in" style="display:none"></div>',
        '<div id="personView" class="fade-in" style="display:none"></div>\n'
        '  <div id="tableView" class="fade-in" style="display:none"></div>\n'
        '  <div id="ganttView" class="fade-in" style="display:none"></div>'
    )

    # 4. ADD FAB and add-task-panel HTML before GANTT TOOLTIP
    fab_html = (
        '\n<!-- ========== FLOATING ADD BUTTON ========== -->\n'
        '<div class="fab-add" id="fabAddBtn" onclick="toggleAddForm()" title="\u6dfb\u52a0\u4efb\u52a1">+</div>\n'
        '\n<!-- ========== INLINE ADD TASK FORM ========== -->\n'
        '<div class="add-task-panel" id="addTaskPanel" style="display:none">\n'
        '  <div class="add-task-header">\n'
        '    <span>\u2795 \u6dfb\u52a0\u65b0\u4efb\u52a1</span>\n'
        '    <button class="add-task-close" onclick="toggleAddForm()">\u2716</button>\n'
        '  </div>\n'
        '  <div class="add-task-body">\n'
        '    <div class="add-task-row">\n'
        '      <textarea id="addTaskTitle" placeholder="\u8f93\u5165\u4efb\u52a1\u63cf\u8ff0..." rows="2" style="width:100%;padding:8px 10px;border:1.5px solid var(--gray-3);border-radius:8px;font-size:13px;"></textarea>\n'
        '    </div>\n'
        '    <div class="add-task-row" style="display:flex;gap:8px;flex-wrap:wrap">\n'
        '      <select id="addTaskPerson" style="flex:1;min-width:120px;padding:7px 8px;border:1.5px solid var(--gray-3);'
        'border-radius:8px;font-size:13px;"><option value="">\u9009\u62e9\u6267\u884c\u4eba</option></select>\n'
        '      <input type="number" id="addTaskHours" value="1" min="0.5" step="0.5" '
        'style="width:70px;padding:7px 8px;border:1.5px solid var(--gray-3);border-radius:8px;font-size:13px;text-align:center" '
        'title="\u5de5\u65f6\uff08\u5929\uff09">\n'
        '      <select id="addTaskRegion" style="width:80px;padding:7px 8px;border:1.5px solid var(--gray-3);'
        'border-radius:8px;font-size:13px;">\n'
        '        <option value="">\u5730\u533a</option>\n'
        '        <option value="\u56fd\u670d">\u56fd\u670d</option>\n'
        '        <option value="\u65e5\u670d">\u65e5\u670d</option>\n'
        '        <option value="\u7f8e\u670d">\u7f8e\u670d</option>\n'
        '        <option value="\u6b27\u670d">\u6b27\u670d</option>\n'
        '      </select>\n'
        '      <input type="date" id="addTaskDeadline" style="padding:7px 8px;border:1.5px solid var(--gray-3);'
        'border-radius:8px;font-size:13px;">\n'
        '    </div>\n'
        '    <div class="add-task-row" style="display:flex;gap:8px;margin-top:8px">\n'
        '      <button class="btn btn-primary-solid" onclick="submitAddTask()" style="flex:1">\u2795 \u6dfb\u52a0\u5e76\u6392\u671f</button>\n'
        '      <button class="btn btn-outline" onclick="toggleAddForm()" style="color:var(--gray-6);border-color:var(--gray-3)">\u53d6\u6d88</button>\n'
        '    </div>\n'
        '    <div id="addTaskResult" class="schedule-result" style="margin-top:8px"></div>\n'
        '  </div>\n'
        '</div>\n'
    )

    html = html.replace(
        '<!-- ========== GANTT TOOLTIP ========== -->',
        fab_html + '<!-- ========== GANTT TOOLTIP ========== -->'
    )

    # 5. ADD delete buttons on card view
    html = html.replace(
        'html += \'<div class="task-card \' + cls + \'">\';',
        'html += \'<div class="task-card \' + cls + \'" style="position:relative">\';\n    '
        'html += \'<button class="delete-btn card-delete" onclick="deleteTask(\\\'\' + r.id + \'\\\')" title="\u5220\u9664">\u2716</button>\';'
    )

    # Admin task card delete button
    html = html.replace(
        'html += \'<div class="task-card card-progress">\';',
        'html += \'<div class="task-card card-progress" style="position:relative">\';\n        '
        'html += \'<button class="delete-btn card-delete" onclick="deleteAdminTask(\' + adminFiltered.indexOf(t) + \')" title="\u5220\u9664">\u2716</button>\';'
    )

    # 6. ADD delete column in table view header
    html = html.replace(
        "{ key: 'versionDate', label: '\u7248\u66f4\u65f6\u95f4', width: '110px' }",
        "{ key: 'versionDate', label: '\u7248\u66f4\u65f6\u95f4', width: '110px' },\n    { key: '', label: '', width: '40px' }"
    )

    # Add delete button in table row cells
    # Fix: ' + r.versionDate + ' -> add delete btn after
    html = html.replace(
        "+ r.versionDate + '</td></tr>';",
        "+ r.versionDate + '</td>';\n    html += '<td><button class=\"delete-btn table-delete\" onclick=\"deleteTaskById(\\'\" + r.id + \"\\')\" title=\"\u5220\u9664\">\u2716</button></td></tr>';"
    )

    html = html.replace(
        "r.scheduledEnd + '</span></td>';",
        "r.scheduledEnd + '</span></td>';\n      html += '<td><button class=\"delete-btn table-delete\" onclick=\"deleteAdminTask(\" + adminFiltered.indexOf(r) + \")\" title=\"\u5220\u9664\">\u2716</button></td>';"
    )

    # Fix empty state colspan
    html = html.replace('colspan="7"', 'colspan="8"')

    # 7. UPDATE switchView
    html = html.replace(
        "['cardView','tableView','ganttView'].forEach(function(id) {",
        "['cardView','personView','tableView','ganttView'].forEach(function(id) {"
    )

    html = html.replace(
        "if (view === 'table') renderTable(filtered, adminFiltered);",
        "if (view === 'person') renderPersonView();\n  else if (view === 'table') renderTable(filtered, adminFiltered);"
    )

    # Update render() dispatch
    html = html.replace(
        "if (currentView === 'card') renderCard(filtered, adminFiltered);\n  else if (currentView === 'table') renderTable(filtered, adminFiltered);\n  else if (currentView === 'gantt') renderGantt(filtered, adminFiltered);",
        "if (currentView === 'card') renderCard(filtered, adminFiltered);\n  else if (currentView === 'person') renderPersonView();\n  else if (currentView === 'table') renderTable(filtered, adminFiltered);\n  else if (currentView === 'gantt') renderGantt(filtered, adminFiltered);"
    )

    # 8. ADD new JavaScript functions BEFORE the START marker
    # Use X instead of backslash-u to avoid Python unicode issues
    JS_BLOCK = r"""
// ======================== PERSON VIEW ========================
function renderPersonView() {
  var hiddenIds = getHiddenIds();
  var personTaskMap = {};
  DATA.forEach(function(r) {
    if (hiddenIds.indexOf(r.id) >= 0) return;
    var names = (r.assignee || []).map(function(p) { return p.name; });
    if (!names.length) names = ['未分配'];
    names.forEach(function(n) {
      if (!personTaskMap[n]) personTaskMap[n] = [];
      personTaskMap[n].push(r);
    });
  });
  adminTasks.forEach(function(t) {
    var n = t.assigneeName;
    if (!personTaskMap[n]) personTaskMap[n] = [];
    personTaskMap[n].push(t);
  });
  var deptMap = {};
  ALL_PEOPLE.forEach(function(p) {
    if (!deptMap[p.dept]) deptMap[p.dept] = [];
    deptMap[p.dept].push(p);
  });
  var sortedDepts = Object.keys(deptMap).sort();
  var html = '';
  sortedDepts.forEach(function(dept) {
    var people = deptMap[dept].sort(function(a,b) { return a.name.localeCompare(b.name); });
    html += '<div class="person-dept-group">';
    html += '<div class="person-dept-header">' + escapeHtml(dept) + ' <span class="dept-count">(' + people.length + '人)</span></div>';
    people.forEach(function(p) {
      var tasks = personTaskMap[p.name] || [];
      var avatarLetter = p.name.charAt(0);
      var hiddenIdsCheck = getHiddenIds();
      html += '<div class="person-item">';
      html += '<div class="person-avatar">' + escapeHtml(avatarLetter) + '</div>';
      html += '<div class="person-info">';
      html += '<div class="person-name">' + escapeHtml(p.name) + ' <span class="person-task-count">(' + tasks.length + '个任务)</span></div>';
      if (tasks.length > 0) {
        html += '<div class="person-tasks">';
        tasks.forEach(function(t) {
          var title = t.title || '';
          var pCls = 'card-notstarted';
          var pLabel = '未启动';
          if (t.progress === '进行中') { pCls = 'card-progress'; pLabel = '进行中'; }
          else if (t.progress === 'QA验收中') { pCls = 'card-qa'; pLabel = 'QA验收中'; }
          var regionStr = (t.region || []).join ? (t.region || []).join(',') : (t.region || '');
          var tId = t.id || '';
          var isAdmin = t.scheduledStart ? true : false;
          html += '<div class="person-task-card ' + pCls + '">';
          if (isAdmin) {
            html += '<span class="person-task-title">' + escapeHtml(title) + ' <span class="priority-high">\u2605 P2</span></span>';
            html += '<span class="person-task-meta">' + escapeHtml(t.scheduledStart || '') + ' ~ ' + escapeHtml(t.scheduledEnd || '') + '</span>';
            html += '<button class="delete-btn" onclick="deleteAdminTaskByTitle(\'' + escapeHtml(title.replace(/'/g, "\\'")) + '\')" title="删除">\u2716</button>';
          } else {
            if (hiddenIdsCheck.indexOf(tId) >= 0) return;
            html += '<span class="person-task-title">' + escapeHtml(title) + '</span>';
            html += '<span class="person-task-meta">' + escapeHtml(regionStr) + ' | ' + pLabel + '</span>';
            html += '<button class="delete-btn" onclick="deleteTask(\'' + tId + '\')" title="删除">\u2716</button>';
          }
          html += '</div>';
        });
        html += '</div>';
      } else {
        html += '<div class="person-no-tasks">暂无任务</div>';
      }
      html += '</div></div>';
    });
    html += '</div>';
  });
  document.getElementById('personView').innerHTML = html || '<div class="empty-state"><span class="empty-icon">\u{1F465}</span><div>暂无人员数据</div></div>';
  var totalVisible = DATA.filter(function(r) { return getHiddenIds().indexOf(r.id) < 0; }).length + adminTasks.length;
  document.getElementById('filterStats').textContent = '显示 ' + ALL_PEOPLE.length + ' 人 | 任务 ' + totalVisible + ' / ' + (DATA.length + adminTasks.length);
}

function deleteAdminTaskByTitle(title) {
  if (!confirm('确定要删除该任务吗？')) return;
  for (var i = 0; i < adminTasks.length; i++) {
    if (adminTasks[i].title === title) {
      adminTasks.splice(i, 1);
      saveAdminTasks();
      renderPersonView();
      render();
      return;
    }
  }
}

// ======================== DELETE TASK ========================
function getHiddenIds() {
  try { return JSON.parse(localStorage.getItem('rox_hidden_ids') || '[]'); } catch(e) { return []; }
}
function saveHiddenIds(ids) {
  localStorage.setItem('rox_hidden_ids', JSON.stringify(ids));
}
function deleteTask(id) {
  if (!confirm('确定要删除该任务吗？')) return;
  var ids = getHiddenIds();
  if (ids.indexOf(id) === -1) ids.push(id);
  saveHiddenIds(ids);
  render();
  if (currentView === 'person') renderPersonView();
}
function deleteTaskById(id) {
  deleteTask(id);
}

// ======================== ADD TASK ========================
function toggleAddForm() {
  var panel = document.getElementById('addTaskPanel');
  if (panel.style.display === 'none') {
    panel.style.display = 'block';
    var sel = document.getElementById('addTaskPerson');
    if (sel.options.length <= 1) {
      var deptMap = {};
      ALL_PEOPLE.forEach(function(p) {
        if (!deptMap[p.dept]) deptMap[p.dept] = [];
        deptMap[p.dept].push(p);
      });
      var sortedDepts = Object.keys(deptMap).sort();
      sortedDepts.forEach(function(dept) {
        var optg = document.createElement('optgroup');
        optg.label = dept;
        deptMap[dept].sort(function(a,b) { return a.name.localeCompare(b.name); }).forEach(function(p) {
          var opt = document.createElement('option');
          opt.value = p.name;
          opt.textContent = dept + ' - ' + p.name;
          optg.appendChild(opt);
        });
        sel.appendChild(optg);
      });
    }
    var future = new Date();
    future.setDate(future.getDate() + 7);
    document.getElementById('addTaskDeadline').value = formatDateISO(future);
    setTimeout(function() { document.getElementById('addTaskTitle').focus(); }, 100);
  } else {
    panel.style.display = 'none';
  }
}

function submitAddTask() {
  var title = document.getElementById('addTaskTitle').value.trim();
  var assigneeName = document.getElementById('addTaskPerson').value;
  var hours = parseFloat(document.getElementById('addTaskHours').value) || 1;
  var region = document.getElementById('addTaskRegion').value;
  var deadline = document.getElementById('addTaskDeadline').value;
  if (!title) { alert('请输入工作内容'); return; }
  if (!assigneeName) { alert('请选择执行人'); return; }
  var personTasks = DATA.filter(function(r) {
    return r.assignee && r.assignee.some(function(p) { return p.name === assigneeName; });
  });
  adminTasks.filter(function(t) { return t.assigneeName === assigneeName; }).forEach(function(t) {
    personTasks.push({ startDate: t.scheduledStart, endDate: t.scheduledEnd, title: t.title });
  });
  personTasks.sort(function(a, b) {
    var da = parseDate(normalizeDate(a.startDate));
    var db = parseDate(normalizeDate(b.startDate));
    if (!da && !db) return 0; if (!da) return 1; if (!db) return -1;
    return da - db;
  });
  var today = new Date(); today.setHours(0,0,0,0);
  var workDaysNeeded = Math.ceil(hours);
  var scheduledStart = null, scheduledEnd = null;
  var deadlineDate = deadline ? parseDate(deadline) : null;
  var candidates = [new Date(today)];
  personTasks.forEach(function(t) {
    var te = parseDate(normalizeDate(t.endDate));
    if (te) { var next = new Date(te); next.setDate(next.getDate() + 1); candidates.push(next); }
  });
  candidates.sort(function(a,b) { return a - b; });
  for (var ci = 0; ci < candidates.length; ci++) {
    var baseStart = new Date(Math.max(candidates[ci].getTime(), today.getTime()));
    for (var d = 0; d < 120; d++) {
      var slotStart = new Date(baseStart); slotStart.setDate(slotStart.getDate() + d);
      var slotEnd = new Date(slotStart); slotEnd.setDate(slotEnd.getDate() + workDaysNeeded - 1);
      if (deadlineDate && slotEnd > deadlineDate) break;
      var overlap = personTasks.some(function(t) {
        var ts = parseDate(normalizeDate(t.startDate));
        var te = parseDate(normalizeDate(t.endDate));
        if (!ts || !te) return false;
        return (slotStart <= te && slotEnd >= ts);
      });
      if (!overlap) { scheduledStart = formatDate(slotStart); scheduledEnd = formatDate(slotEnd); break; }
    }
    if (scheduledStart) break;
  }
  if (!scheduledStart) { alert('无法找到足够的空闲排期时间，请调整工时或联系管理员'); return; }
  var resultDiv = document.getElementById('addTaskResult');
  resultDiv.style.display = 'block';
  resultDiv.innerHTML = '\u2705 排期结果: <strong>' + escapeHtml(assigneeName) + '</strong> 于 <strong>' + scheduledStart + ' ~ ' + scheduledEnd + '</strong> 执行\u300c' + escapeHtml(title) + '\u300d\uff08' + hours + '人天\uff09';
  var newTask = {
    title: title, hours: hours, priority: 'P2', assigneeName: assigneeName,
    region: region || '', progress: '未启动', scheduledStart: scheduledStart, scheduledEnd: scheduledEnd,
    createdAt: new Date().toISOString()
  };
  adminTasks.push(newTask);
  saveAdminTasks();
  document.getElementById('addTaskTitle').value = '';
  var future = new Date(); future.setDate(future.getDate() + 7);
  document.getElementById('addTaskDeadline').value = formatDateISO(future);
  render();
  if (currentView === 'person') renderPersonView();
}

// ======================== UPDATE applyFilters for person view ========================
function applyFilters() {
  if (currentView === 'person') renderPersonView();
  else render();
}
"""

    # Insert JS before the START marker
    html = html.replace(
        '// ======================== START ========================',
        JS_BLOCK + '\n// ======================== START ========================'
    )

    # 9. Fix original applyFilters
    html = html.replace(
        'function applyFilters() {\n  render();\n}',
        'function applyFilters() {\n  if (currentView === \'person\') renderPersonView();\n  else render();\n}'
    )

    return html


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python3 enhance_html.py <input.html> [output.html]')
        sys.exit(1)

    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        html = f.read()

    enhanced = enhance_html(html)

    output = sys.argv[2] if len(sys.argv) > 2 else sys.argv[1]
    with open(output, 'w', encoding='utf-8') as f:
        f.write(enhanced)

    print(f'Enhanced HTML: {len(enhanced)} bytes -> {output}')