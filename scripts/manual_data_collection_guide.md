# Manual Data Collection Guide for Rust/Solana Vulnerabilities

## Current Status
- ✅ Hugging Face: 205 contracts extracted
- ✅ Mock data: 150 contracts generated
- **Total: 355 contracts**

## Next Steps to Expand Dataset

### 1. **Direct GitHub Repository Mining** (Recommended)
```bash
# Clone major Solana repositories
git clone https://github.com/solana-labs/solana-program-library.git
git clone https://github.com/coral-xyz/anchor.git
git clone https://github.com/project-serum/anchor.git

# Search for security-related issues and PRs
cd solana-program-library
git log --grep="security\|vulnerability\|exploit\|bug\|fix" --oneline
git log --grep="unsafe\|panic\|overflow\|validation" --oneline
```

### 2. **Manual Collection from Security Reports**

#### **Rekt.news** (High Priority)
- Visit: https://rekt.news/
- Look for Solana/Rust exploits
- Copy code snippets from reports
- Common vulnerabilities: Account validation, PDA issues, CPI bugs

#### **Immunefi Reports** (High Priority)
- Visit: https://immunefi.com/explore/
- Filter by "Solana" or "Rust"
- Extract vulnerable code from bug bounty reports

#### **SlowMist Hacked** (Medium Priority)
- Visit: https://hacked.slowmist.io/en/
- Search for Solana-related hacks
- Extract code examples

### 3. **CVE Database Mining**
```bash
# Search for Rust-related CVEs
curl "https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch=rust&resultsPerPage=100"
curl "https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch=solana&resultsPerPage=100"
```

### 4. **Audit Reports** (High Value)
- **Trail of Bits**: https://github.com/trailofbits/publications
- **OtterSec**: https://github.com/ottersec
- **Halborn**: https://www.halborn.com/resources
- **Quantstamp**: https://quantstamp.com/blog

### 5. **Community Resources**
- **Solana Security Discord**: Look for vulnerability discussions
- **Reddit r/solana**: Security-related posts
- **Twitter**: Follow @solana, @anchor_lang for security updates

## Data Format for Manual Addition

When you find vulnerable code, add it to `datasets/raw/manual_vulnerable_contracts.json`:

```json
[
  {
    "contract_id": "manual_rekt_001",
    "source_code": "use anchor_lang::prelude::*;\n\n#[program]\npub mod vulnerable_contract {\n    // ... vulnerable code here ...\n}",
    "vulnerabilities": ["account_validation", "signature_verification"],
    "severity": ["high"],
    "source": "manual_rekt_news",
    "file_path": "manual_rekt_001.rs",
    "url": "https://rekt.news/example-hack",
    "description": "Brief description of the vulnerability"
  }
]
```

## Automated Extraction Scripts

### For GitHub Repositories:
```bash
# Extract all .rs files from a repository
find solana-program-library -name "*.rs" -exec grep -l "unsafe\|panic\|unwrap\|expect" {} \; > vulnerable_files.txt

# Extract code blocks from issues
gh issue list --repo solana-labs/solana-program-library --label "security" --json body,title,number
```

### For Web Scraping (if needed):
```python
# Use the extract_vulnerable_contracts.py script
python scripts/extract_vulnerable_contracts.py --source rekt
python scripts/extract_vulnerable_contracts.py --source immunefi
```

## Target Numbers

- **Current**: 355 contracts
- **Target**: 2,000+ contracts
- **Breakdown**:
  - 1,000 vulnerable contracts
  - 1,000 safe contracts
  - 15+ vulnerability types represented
  - 300+ examples per major vulnerability type

## Priority Order

1. **High Priority**: Rekt.news, Immunefi, Audit reports
2. **Medium Priority**: GitHub issues, CVE database
3. **Low Priority**: Community discussions, social media

## Quality Checklist

- [ ] Code is actually Rust/Solana
- [ ] Vulnerability is clearly identified
- [ ] Code is complete (not just snippets)
- [ ] Source is documented
- [ ] Severity is appropriate
- [ ] No duplicate code

## Integration with Existing Dataset

After collecting new data:
```bash
# Merge with existing dataset
python scripts/merge_datasets.py \
  --existing ../datasets/processed/unified_rust_dataset.json \
  --new datasets/raw/manual_vulnerable_contracts.json \
  --output ../datasets/processed/unified_rust_dataset_expanded.json
```

## Expected Timeline

- **Week 1**: Manual collection from Rekt.news, Immunefi (target: +200 contracts)
- **Week 2**: GitHub repository mining (target: +300 contracts)
- **Week 3**: Audit reports and CVE database (target: +200 contracts)
- **Week 4**: Community sources and quality review (target: +150 contracts)

**Total target**: 1,200+ contracts by end of month

