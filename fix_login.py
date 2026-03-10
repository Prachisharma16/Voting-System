import re

# Read the file
with open('d:/Downloads/voting chatbot (4)/voting chatbot/templates/login.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove the onclick attributes and change href="#" to href="/register"
content = re.sub(r' onclick="alert\([^)]+\); return false;"', '', content)
content = content.replace('href="#"', 'href="/register"')

# Write back
with open('d:/Downloads/voting chatbot (4)/voting chatbot/templates/login.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('Fixed!')

