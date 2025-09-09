#!/usr/bin/env python3
import webbrowser
import json
from pathlib import Path
from datetime import datetime

def load_results(results_file="url_results.json"):
    """Load existing results from JSON file"""
    results_path = Path(results_file)
    if results_path.exists():
        try:
            with results_path.open("r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_results(results, results_file="url_results.json"):
    """Save results to JSON file"""
    results_path = Path(results_file)
    with results_path.open("w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

def create_html_table(input_file="generated_codes.txt", output_file="urls_table.html"):
    """Create an HTML table with clickable URLs from the input file"""
    
    input_path = Path(input_file)
    if not input_path.exists():
        print(f"Input file not found: {input_file}")
        return None
    
    # Read URLs from file
    with input_path.open("r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip()]
    
    # Load existing results
    results = load_results()
    
    # Create HTML content
    html_content = f"""
<!DOCTYPE html>
<html dir="rtl" lang="he">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>רשימת כתובות - {len(urls)} לינקים</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #1a1a1a;
            color: #ffffff;
            margin: 0;
            padding: 20px;
            direction: rtl;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        h1 {{
            text-align: center;
            color: #4CAF50;
            margin-bottom: 30px;
            font-size: 2.5em;
        }}
        
        .stats {{
            background-color: #2d2d2d;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            text-align: center;
            font-size: 1.2em;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            background-color: #2d2d2d;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        }}
        
        th {{
            background-color: #4CAF50;
            color: white;
            padding: 15px;
            text-align: center;
            font-size: 1.1em;
            font-weight: bold;
        }}
        
        td {{
            padding: 12px 15px;
            border-bottom: 1px solid #444;
            text-align: center;
        }}
        
        tr:nth-child(even) {{
            background-color: #3a3a3a;
        }}
        
        tr:hover {{
            background-color: #4a4a4a;
        }}
        
        .url-link {{
            color: #64B5F6;
            text-decoration: none;
            font-weight: bold;
            padding: 8px 12px;
            border-radius: 4px;
            background-color: #1e3a5f;
            display: inline-block;
            transition: all 0.3s ease;
            word-break: break-all;
        }}
        
        .url-link:hover {{
            background-color: #2d5a8f;
            color: #90CAF9;
            transform: translateY(-2px);
        }}
        
        .row-number {{
            color: #FFC107;
            font-weight: bold;
            font-size: 1.1em;
        }}
        
        .actions {{
            margin-top: 20px;
            text-align: center;
        }}
        
        .btn {{
            background-color: #4CAF50;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 1.1em;
            margin: 0 10px;
            transition: background-color 0.3s ease;
        }}
        
        .btn:hover {{
            background-color: #45a049;
        }}
        
        .btn-secondary {{
            background-color: #6c757d;
        }}
        
        .btn-secondary:hover {{
            background-color: #5a6268;
        }}
        
        .btn-valid {{
            background-color: #4CAF50;
            margin: 2px;
        }}
        
        .btn-invalid {{
            background-color: #f44336;
            margin: 2px;
        }}
        
        .btn-valid:hover {{
            background-color: #45a049;
        }}
        
        .btn-invalid:hover {{
            background-color: #da190b;
        }}
        
        .status-valid {{
            color: #4CAF50;
            font-weight: bold;
        }}
        
        .status-invalid {{
            color: #f44336;
            font-weight: bold;
        }}
        
        .status-pending {{
            color: #FFC107;
            font-weight: bold;
        }}
        
        .completed-section {{
            margin-top: 30px;
            padding: 20px;
            background-color: #2d2d2d;
            border-radius: 8px;
        }}
        
        .completed-section h3 {{
            color: #4CAF50;
            margin-bottom: 15px;
        }}
        
        .completed-urls {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }}
        
        .completed-url {{
            background-color: #3a3a3a;
            padding: 8px 12px;
            border-radius: 4px;
            font-size: 0.9em;
            word-break: break-all;
        }}
        
        .completed-url.valid {{
            border-left: 4px solid #4CAF50;
        }}
        
        .completed-url.invalid {{
            border-left: 4px solid #f44336;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🎯 רשימת כתובות קידוד</h1>
        
        <div class="stats">
            📊 סה"כ {len(urls)} כתובות | 🕒 נוצר ב-{Path(input_file).stat().st_mtime}
            <br>
            ✅ תקינים: <span id="valid-count">{sum(1 for url in urls if results.get(url, {}).get('status') == 'valid')}</span> | 
            ❌ לא תקינים: <span id="invalid-count">{sum(1 for url in urls if results.get(url, {}).get('status') == 'invalid')}</span> | 
            ⏳ ממתינים: <span id="pending-count">{sum(1 for url in urls if results.get(url, {}).get('status') not in ['valid', 'invalid'])}</span>
        </div>
        
        <div class="actions">
            <button class="btn" onclick="openNextThree()">
                🚀 פתח 3 לינקים הבאים
            </button>
            <button class="btn btn-secondary" onclick="copyAllUrls()">
                📋 העתק את כל הכתובות
            </button>
            <button class="btn btn-secondary" onclick="exportResults()">
                💾 ייצא תוצאות JSON
            </button>
            <button class="btn btn-secondary" onclick="exportValidUrls()">
                ✅ ייצא לינקים תקינים
            </button>
            <button class="btn btn-secondary" onclick="exportInvalidUrls()">
                ❌ ייצא לינקים לא תקינים
            </button>
        </div>
        
        <table>
            <thead>
                <tr>
                    <th>מס'</th>
                    <th>כתובת הקישור</th>
                    <th>סטטוס</th>
                    <th>פעולות</th>
                </tr>
            </thead>
            <tbody>
"""
    
    # Add table rows
    for i, url in enumerate(urls, 1):
        url_result = results.get(url, {})
        status = url_result.get('status', 'pending')
        status_class = f"status-{status}"
        status_text = {"valid": "✅ תקין", "invalid": "❌ לא תקין", "pending": "⏳ ממתין"}.get(status, "⏳ ממתין")
        
        html_content += f"""
                <tr id="row-{i}">
                    <td class="row-number">{i}</td>
                    <td>
                        <a href="{url}" target="_blank" class="url-link">
                            {url}
                        </a>
                    </td>
                    <td>
                        <span class="{status_class}" id="status-{i}">{status_text}</span>
                    </td>
                    <td>
                        <button class="btn" onclick="window.open('{url}', '_blank')">
                            🔗 פתח טאב חדש
                        </button>
                        <button class="btn btn-valid" onclick="markAsValid('{url}', {i})">
                            ✅ תקין
                        </button>
                        <button class="btn btn-invalid" onclick="markAsInvalid('{url}', {i})">
                            ❌ לא תקין
                        </button>
                    </td>
                </tr>
"""
    
    html_content += """
            </tbody>
        </table>
        
        <div class="completed-section" id="completed-section" style="display: none;">
            <h3>✅ לינקים שהושלמו</h3>
            <div class="completed-urls" id="completed-urls">
                <!-- Completed URLs will be added here dynamically -->
            </div>
        </div>
    </div>
    
    <script>
        const urls = """ + str(urls) + """;
        let currentIndex = 0;
        
        function openNextThree() {
            const remainingUrls = urls.slice(currentIndex, currentIndex + 3);
            if (remainingUrls.length === 0) {
                alert('כל הלינקים נפתחו!');
                return;
            }
            
            remainingUrls.forEach(url => {
                window.open(url, '_blank');
            });
            
            currentIndex += 3;
            
            // Update button text
            const button = event.target;
            const remaining = urls.length - currentIndex;
            if (remaining > 0) {
                button.textContent = `🚀 פתח 3 לינקים הבאים (${remaining} נותרו)`;
            } else {
                button.textContent = '✅ כל הלינקים נפתחו';
                button.disabled = true;
            }
        }
        
        function markAsValid(url, rowIndex) {
            moveToCompleted(url, rowIndex, 'valid', '✅ תקין');
            saveResult(url, 'valid');
        }
        
        function markAsInvalid(url, rowIndex) {
            moveToCompleted(url, rowIndex, 'invalid', '❌ לא תקין');
            saveResult(url, 'invalid');
        }
        
        function moveToCompleted(url, rowIndex, status, statusText) {
            // Remove row from main table
            const row = document.getElementById(`row-${rowIndex}`);
            if (row) {
                row.remove();
            }
            
            // Add to completed section
            addToCompleted(url, status, statusText);
            
            // Update counters
            updateCounters();
            
            // Show completed section if it was hidden
            const completedSection = document.getElementById('completed-section');
            completedSection.style.display = 'block';
        }
        
        function addToCompleted(url, status, statusText) {
            const completedUrls = document.getElementById('completed-urls');
            const urlElement = document.createElement('div');
            urlElement.className = `completed-url ${status}`;
            urlElement.innerHTML = `
                <div style="font-weight: bold; margin-bottom: 4px;">${statusText}</div>
                <div style="font-size: 0.8em; color: #ccc;">${url}</div>
            `;
            completedUrls.appendChild(urlElement);
        }
        
        function updateStatus(url, rowIndex, status, statusText) {
            const statusElement = document.getElementById(`status-${rowIndex}`);
            statusElement.textContent = statusText;
            statusElement.className = `status-${status}`;
            
            // Update counters
            updateCounters();
        }
        
        function updateCounters() {
            // Count from main table (pending)
            const pendingCount = document.querySelectorAll('.status-pending').length;
            
            // Count from completed section
            const validCount = document.querySelectorAll('.completed-url.valid').length;
            const invalidCount = document.querySelectorAll('.completed-url.invalid').length;
            
            document.getElementById('valid-count').textContent = validCount;
            document.getElementById('invalid-count').textContent = invalidCount;
            document.getElementById('pending-count').textContent = pendingCount;
        }
        
        function saveResult(url, status) {
            // Send result to server (simplified - in real app you'd use fetch)
            const results = JSON.parse(localStorage.getItem('urlResults') || '{}');
            results[url] = {
                status: status,
                timestamp: new Date().toISOString()
            };
            localStorage.setItem('urlResults', JSON.stringify(results));
        }
        
        function copyAllUrls() {
            const text = urls.join('\\n');
            navigator.clipboard.writeText(text).then(() => {
                alert('כל הכתובות הועתקו ללוח!');
            }).catch(() => {
                // Fallback for older browsers
                const textArea = document.createElement('textarea');
                textArea.value = text;
                document.body.appendChild(textArea);
                textArea.select();
                document.execCommand('copy');
                document.body.removeChild(textArea);
                alert('כל הכתובות הועתקו ללוח!');
            });
        }
        
        function exportResults() {
            const results = JSON.parse(localStorage.getItem('urlResults') || '{}');
            const dataStr = JSON.stringify(results, null, 2);
            const dataBlob = new Blob([dataStr], {type: 'application/json'});
            const url = URL.createObjectURL(dataBlob);
            const link = document.createElement('a');
            link.href = url;
            link.download = 'url_results.json';
            link.click();
            URL.revokeObjectURL(url);
        }
        
        function exportValidUrls() {
            const validElements = document.querySelectorAll('.completed-url.valid');
            const validUrls = Array.from(validElements).map(el => {
                const urlText = el.querySelector('div:last-child').textContent;
                return urlText.trim();
            });
            
            if (validUrls.length === 0) {
                alert('אין לינקים תקינים לייצוא');
                return;
            }
            
            const dataStr = validUrls.join('\\n');
            const dataBlob = new Blob([dataStr], {type: 'text/plain'});
            const url = URL.createObjectURL(dataBlob);
            const link = document.createElement('a');
            link.href = url;
            link.download = 'valid_urls.txt';
            link.click();
            URL.revokeObjectURL(url);
            
            alert(`ייצאו ${validUrls.length} לינקים תקינים לקובץ valid_urls.txt`);
        }
        
        function exportInvalidUrls() {
            const invalidElements = document.querySelectorAll('.completed-url.invalid');
            const invalidUrls = Array.from(invalidElements).map(el => {
                const urlText = el.querySelector('div:last-child').textContent;
                return urlText.trim();
            });
            
            if (invalidUrls.length === 0) {
                alert('אין לינקים לא תקינים לייצוא');
                return;
            }
            
            const dataStr = invalidUrls.join('\\n');
            const dataBlob = new Blob([dataStr], {type: 'text/plain'});
            const url = URL.createObjectURL(dataBlob);
            const link = document.createElement('a');
            link.href = url;
            link.download = 'invalid_urls.txt';
            link.click();
            URL.revokeObjectURL(url);
            
            alert(`ייצאו ${invalidUrls.length} לינקים לא תקינים לקובץ invalid_urls.txt`);
        }
        
        // Add keyboard shortcuts
        document.addEventListener('keydown', function(e) {
            if (e.ctrlKey && e.key === 'a') {
                e.preventDefault();
                copyAllUrls();
            }
            if (e.ctrlKey && e.key === 'o') {
                e.preventDefault();
                openNextThree();
            }
            if (e.ctrlKey && e.key === 'e') {
                e.preventDefault();
                exportResults();
            }
        });
        
        // Load saved results on page load
        window.addEventListener('load', function() {
            const savedResults = JSON.parse(localStorage.getItem('urlResults') || '{}');
            Object.keys(savedResults).forEach(url => {
                const urlIndex = urls.indexOf(url);
                if (urlIndex !== -1) {
                    const result = savedResults[url];
                    updateStatus(url, urlIndex + 1, result.status, 
                        result.status === 'valid' ? '✅ תקין' : '❌ לא תקין');
                }
            });
        });
    </script>
</body>
</html>
"""
    
    # Save HTML file
    output_path = Path(output_file)
    with output_path.open("w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"HTML table created: {output_file}")
    print(f"Total URLs: {len(urls)}")
    
    return str(output_path)

def open_in_browser(html_file):
    """Open the HTML file in the default browser"""
    try:
        webbrowser.open(f"file://{Path(html_file).absolute()}")
        print(f"Opening {html_file} in browser...")
    except Exception as e:
        print(f"Error opening browser: {e}")

if __name__ == "__main__":
    html_file = create_html_table()
    if html_file:
        open_in_browser(html_file)
