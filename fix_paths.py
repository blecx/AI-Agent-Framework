import re, pathlib

for f in [p for p in pathlib.Path('.').rglob('*.md') if '.venv' not in p.parts and '_external' not in p.parts]:
    try:
        text = f.read_text()
        # Replace .github/prompts/modules/ux/NAME.md -> .copilot/skills/ux-NAME/SKILL.md
        new_text = re.sub(r'(\.?/?\.github/prompts/modules/ux/)([^.]+)\.md', r'.copilot/skills/ux-\2/SKILL.md', text)
        # Replace .github/prompts/modules/NAME.md -> .copilot/skills/NAME/SKILL.md
        new_text = re.sub(r'(\.?/?\.github/prompts/modules/)([^.]+)\.md', r'.copilot/skills/\2/SKILL.md', new_text)
        if new_text != text:
            f.write_text(new_text)
            print(f'Updated {f}')
    except Exception as e:
        pass
