#!/usr/bin/env python3
"""
Test extraction with different export formats.
"""

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.extract_learnings import LearningsExtractor


def test_markdown_export():
    """Test extraction from markdown export."""
    print("Testing Markdown export format...")
    
    markdown_content = """# Issue #99 Test Chat Export

## Phase 1: Context Gathering

Reading the issue requirements.

### Problem: Build failed

Solution: Run npm install

## Phase 2: Planning

Created planning document.

```bash
npm install
npm run build
```

Time spent: 2.5 hours
Estimated: 2 hours
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(markdown_content)
        temp_path = Path(f.name)
    
    try:
        extractor = LearningsExtractor(knowledge_base_dir=Path("agents/knowledge"))
        learnings = extractor.extract_from_export(temp_path)
        
        assert learnings, "Failed to extract learnings from markdown"
        assert learnings['issue_num'] == 99, f"Wrong issue number: {learnings['issue_num']}"
        assert len(learnings['workflow_phases']) > 0, "No phases extracted"
        assert len(learnings['problems_solved']) > 0, "No problems extracted"
        assert len(learnings['command_sequences']) > 0, "No commands extracted"
        
        print("  ✅ Markdown format: PASS")
        return True
    
    finally:
        temp_path.unlink()


def test_json_export():
    """Test extraction from JSON export."""
    print("Testing JSON export format...")
    
    json_data = {
        "issue": 99,
        "content": """# Issue #99 Test
        
## Phase 1: Context
Reading issue.

### Problem: Tests failed
Solution: Fix test syntax

```bash
pytest
```

Time: 1.5 hours
"""
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(json_data, f)
        temp_path = Path(f.name)
    
    try:
        extractor = LearningsExtractor(knowledge_base_dir=Path("agents/knowledge"))
        learnings = extractor.extract_from_export(temp_path)
        
        assert learnings, "Failed to extract learnings from JSON"
        assert learnings['issue_num'] == 99, f"Wrong issue number: {learnings['issue_num']}"
        
        print("  ✅ JSON format: PASS")
        return True
    
    finally:
        temp_path.unlink()


def test_json_messages_format():
    """Test extraction from JSON messages format."""
    print("Testing JSON messages format...")
    
    json_data = {
        "issue": 99,
        "messages": [
            {"role": "user", "content": "I'm working on Issue #99"},
            {"role": "assistant", "content": "## Phase 1: Context\nLet's start by reading the issue."},
            {"role": "user", "content": "Problem: Build fails"},
            {"role": "assistant", "content": "Solution: Run npm install\n```bash\nnpm install\n```"},
        ]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(json_data, f)
        temp_path = Path(f.name)
    
    try:
        extractor = LearningsExtractor(knowledge_base_dir=Path("agents/knowledge"))
        learnings = extractor.extract_from_export(temp_path)
        
        assert learnings, "Failed to extract learnings from JSON messages"
        assert learnings['issue_num'] == 99, f"Wrong issue number: {learnings['issue_num']}"
        
        print("  ✅ JSON messages format: PASS")
        return True
    
    finally:
        temp_path.unlink()


def main():
    print("🧪 Testing Multi-Format Export Support\n")
    
    tests = [
        test_markdown_export,
        test_json_export,
        test_json_messages_format,
    ]
    
    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"  ❌ {test_func.__name__} FAILED: {e}")
            results.append(False)
    
    print(f"\n📊 Results: {sum(results)}/{len(results)} tests passed")
    
    if all(results):
        print("✅ Multi-format support working correctly")
        return 0
    else:
        print("❌ Some format tests failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
