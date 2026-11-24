"""Small deterministic prompts; expected answers are only scored with explicit rules."""
PROMPTS = [
 {"id":"arith_01","category":"arithmetic","prompt":"What is 17 + 25? Reply with only the number.","expected":"42","rule":"exact"},
 {"id":"arith_02","category":"arithmetic","prompt":"What is 9 multiplied by 8? Reply with only the number.","expected":"72","rule":"exact"},
 {"id":"arith_03","category":"arithmetic","prompt":"What is 100 minus 37? Reply with only the number.","expected":"63","rule":"exact"},
 {"id":"logic_01","category":"logic","prompt":"All roses are flowers. A red rose is a rose. Is a red rose a flower? Reply yes or no.","expected":"yes","rule":"contains"},
 {"id":"logic_02","category":"logic","prompt":"If today is Tuesday, what day is tomorrow? Reply with one weekday.","expected":"Wednesday","rule":"contains"},
 {"id":"extract_01","category":"extraction","prompt":"Extract the city from: 'The package arrived in Kyoto yesterday.' Reply with only the city.","expected":"Kyoto","rule":"contains"},
 {"id":"extract_02","category":"extraction","prompt":"Extract the date: 'The meeting is scheduled for 2026-12-05 at noon.' Reply with only the date.","expected":"2026-12-05","rule":"contains"},
 {"id":"format_01","category":"formatting","prompt":"Return the colors mentioned, comma-separated: 'The flag is blue, white, and green.'","expected":"blue, white, green","rule":"contains"},
 {"id":"knowledge_01","category":"knowledge","prompt":"How many sides does a hexagon have? Reply with only the number.","expected":"6","rule":"exact"},
 {"id":"summarization_01","category":"summarization","prompt":"Summarize in five words or fewer: 'Plants use sunlight, water, and carbon dioxide to produce sugars and release oxygen.'","expected":None,"rule":None},
 {"id":"generation_01","category":"generation","prompt":"Name one renewable energy source. Reply with a short phrase.","expected":None,"rule":None},
 {"id":"reasoning_01","category":"reasoning","prompt":"A pen costs 3 dollars. How much do 4 pens cost? Reply with only the amount in dollars.","expected":"12","rule":"exact"},
]

def score(answer: str, expected: str | None, rule: str | None):
    if not expected or not rule: return None
    if rule == "exact": return answer.strip().lower().rstrip(".! ") == expected.lower()
    if rule == "contains": return expected.lower() in answer.lower()
    return None
