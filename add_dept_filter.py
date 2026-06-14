#!/usr/bin/env python3
"""Add department filter to ROX schedule board HTML."""
import sys

def add_dept_filter(html):
    changes = 0

    # 1. Add department filter dropdown in the filter bar (before 搜索)
    old_filter = '</div>\n    <div class="filter-group">\n      <label>\u641c\u7d22</label>'
    dept_filter = (
        '</div>\n'
        '    <div class="filter-group">\n'
        '      <label>\u90e8\u95e8</label>\n'
        '      <select id="filterDept" onchange="applyFilters()">\n'
        '        <option value="">\u5168\u90e8</option>\n'
        '      </select>\n'
        '    </div>\n'
        '    <div class="filter-group">\n'
        '      <label>\u641c\u7d22</label>'
    )
    if old_filter in html:
        html = html.replace(old_filter, dept_filter, 1)
        changes += 1
        print("✅ Filter dropdown added")
    else:
        print("❌ Step 1 failed")

    # 2. Add dept filter in DATA.filter section
    old_person = (
        "if (person) {\n"
        "      if (!r.assignee || !r.assignee.some(function(p) { return p.name === person; })) return false;\n"
        "    } else {\n"
        "      // When \"\u5168\u90e8\" is selected, show all (default behavior)\n"
        "    }"
    )
    new_person = old_person + (
        "\n"
        "    var dept = document.getElementById('filterDept').value;\n"
        "    if (dept) {\n"
        "      if (!r.assignee || !r.assignee.some(function(p) { return p.dept === dept; })) return false;\n"
        "    }"
    )
    if old_person in html:
        html = html.replace(old_person, new_person, 1)
        changes += 1
        print("✅ DATA.filter dept check added")
    else:
        print("❌ Step 2 failed")

    # 3. Add dept filter in adminTasks filter section
    old_admin = (
        "if (person && t.assigneeName !== person) return false;\n"
        "    if (search && t.title.toLowerCase().indexOf(search) === -1) return false;"
    )
    new_admin = (
        "if (person && t.assigneeName !== person) return false;\n"
        "    if (dept) {\n"
        "      var tDept = '';\n"
        "      ALL_PEOPLE.some(function(p) { if (p.name === t.assigneeName) { tDept = p.dept; return true; } return false; });\n"
        "      if (tDept !== dept) return false;\n"
        "    }\n"
        "    if (search && t.title.toLowerCase().indexOf(search) === -1) return false;"
    )
    if old_admin in html:
        html = html.replace(old_admin, new_admin, 1)
        changes += 1
        print("✅ Admin filter dept check added")
    else:
        print("❌ Step 3 failed")

    # 4. Add dept filter population in init()
    # Insert before the headerInfo line (last line before render())
    old_stats = "document.getElementById('headerInfo').textContent = DATA.length + ' \\u4e2a\\u4efb\\u52a1 | ' + allPeople.length + ' \\u4eba';"
    dept_pop = (
        "// Populate department filter\n"
        "  var selDept = document.getElementById('filterDept');\n"
        "  sortedDepts.forEach(function(dept) {\n"
        "    var opt = document.createElement('option');\n"
        "    opt.value = dept;\n"
        "    opt.textContent = dept;\n"
        "    selDept.appendChild(opt);\n"
        "  });\n"
        "\n"
        "  document.getElementById('headerInfo').textContent = DATA.length + ' \\u4e2a\\u4efb\\u52a1 | ' + allPeople.length + ' \\u4eba';"
    )
    if old_stats in html:
        html = html.replace(old_stats, dept_pop, 1)
        changes += 1
        print("✅ Init dept population added")
    else:
        print("❌ Step 4 failed")

    # 5. Update renderPersonView to respect dept filter
    # Find the FIRST occurrence of sortedDepts that is in renderPersonView
    # renderPersonView builds its own deptMap, so we need to filter it there
    idx = html.find("function renderPersonView()")
    if idx >= 0:
        # Find the sortedDepts after renderPersonView
        sub = html[idx:]
        sd_idx = sub.find("var sortedDepts = Object.keys(deptMap).sort();")
        if sd_idx >= 0:
            old_line = "var sortedDepts = Object.keys(deptMap).sort();"
            new_block = (
                "  var filterDeptVal = document.getElementById('filterDept').value;\n"
                "  if (filterDeptVal) {\n"
                "    var filteredDeptMap = {};\n"
                "    filteredDeptMap[filterDeptVal] = deptMap[filterDeptVal] || [];\n"
                "    deptMap = filteredDeptMap;\n"
                "  }\n"
                "  var sortedDepts = Object.keys(deptMap).sort();\n"
            )
            # Replace only in the sub-section
            actual_idx = idx + sd_idx
            html = html[:actual_idx] + new_block + html[actual_idx + len(old_line):]
            changes += 1
            print("✅ renderPersonView dept filter added")
        else:
            print("❌ Step 5b: sortedDepts not found in renderPersonView")
    else:
        print("❌ Step 5a: renderPersonView not found")

    print(f"\nTotal changes: {changes}")
    return html


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 add_dept_filter.py <input.html> [output.html]")
        sys.exit(1)

    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        html = f.read()

    result = add_dept_filter(html)

    output = sys.argv[2] if len(sys.argv) > 2 else sys.argv[1]
    with open(output, 'w', encoding='utf-8') as f:
        f.write(result)

    print(f"Output: {len(result)} bytes -> {output}")