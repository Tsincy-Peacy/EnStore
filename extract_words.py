import pdfplumber
import re
import json

pdf_path = r'C:\Users\Tsinc\Downloads\c31c7a4dccf38609397e740a2cfc5566.pdf'
word_entries = {}  # No -> {word, raw_meaning}

with pdfplumber.open(pdf_path) as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        if not text:
            continue
        lines = text.split('\n')
        for line in lines:
            # Find all occurrences of: number + english word + meaning
            matches = re.findall(
                r'(\d+)\s+([a-zA-Z][a-zA-Z\-]*)\s+((?:[a-z]+\.\s)?[^\d]+?)(?=\s*\d+\s+[a-zA-Z]|$)',
                line
            )
            for match in matches:
                no, word, meaning = match
                no = int(no)
                meaning = meaning.strip().rstrip(';,').strip()
                if word.lower() in ('no', 'word', 'meaning', 'title', 'date', 'classic',
                                    'vocabulary', 'list', 'adj', 'vt', 'vi', 'n', 'v'):
                    continue
                if re.match(r'^[a-zA-Z][a-zA-Z\-]*$', word) and len(word) > 1:
                    if no not in word_entries:
                        word_entries[no] = {'word': word.lower(), 'raw_meaning': meaning}

sorted_words = sorted(word_entries.items())
print(f'Total extracted: {len(sorted_words)}')
for no, entry in sorted_words:
    wrd = entry['word']
    mng = entry['raw_meaning'][:60]
    print(f'{no:3d}. {wrd:20s} | {mng}')

# Save to JSON for next step
with open(r'd:\Workspace\EnStory\extracted_words.json', 'w', encoding='utf-8') as f:
    json.dump(sorted_words, f, ensure_ascii=False, indent=2)
print('\nSaved to extracted_words.json')
