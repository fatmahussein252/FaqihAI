import re
import json

def parse_json_output(output, is_formatter=False):
    raw_output = output.strip()
    try:
        match = re.search(r'\{.*\}', raw_output, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        return {"question": "خطأ في التنسيق - لم يتم العثور على JSON"} if is_formatter else {"error": "No JSON found", "raw": raw_output}
    except json.JSONDecodeError:
        return {"question": "خطأ في التنسيق - خطأ في فك تشفير JSON"} if is_formatter else {"error": "JSON Decode Error", "raw": raw_output}
    except Exception:
        return {"question": "خطأ في التنسيق - خطأ غير متوقع"} if is_formatter else {"error": "Unexpected Parsing Error", "raw": raw_output}

def is_arabic_text(text):
    return bool(re.search(r'[\u0600-\u06FF]', text.strip()))