import re
from typing import Dict, Tuple, Optional

class LanguageDetector:
    def __init__(self):
        self.language_patterns = {
            'solidity': [
                r'pragma\s+solidity',
                r'contract\s+\w+',
                r'function\s+\w+\s*\([^)]*\)',
                r'mapping\s*\([^)]*\)\s*[a-zA-Z_][a-zA-Z0-9_]*',
                r'msg\.sender',
                r'block\.timestamp',
                r'require\s*\(',
                r'emit\s+\w+',
                r'payable',
                r'address\s+',
                r'uint\d*',
                r'bytes\d*'
            ],
            'vyper': [
                r'@external',
                r'@view',
                r'@pure',
                r'@payable',
                r'@nonreentrant',
                r'def\s+\w+\s*\([^)]*\)',
                r'struct\s+\w+:',
                r'event\s+\w+',
                r'@public',
                r'@private'
            ],
            'rust': [
                r'use\s+anchor_lang',
                r'#\[program\]',
                r'#\[derive\(Accounts\)\]',
                r'pub\s+fn\s+\w+',
                r'struct\s+\w+\s*\{',
                r'impl\s+\w+',
                r'let\s+\w+:',
                r'->\s*Result<\(\)>',
                r'ctx:\s*Context<',
                r'#\[account\]'
            ],
            'javascript': [
                r'function\s+\w+\s*\([^)]*\)\s*\{',
                r'const\s+\w+\s*=',
                r'let\s+\w+\s*=',
                r'var\s+\w+\s*=',
                r'console\.log',
                r'require\s*\(',
                r'module\.exports',
                r'async\s+function',
                r'await\s+',
                r'\.then\s*\('
            ],
            'python': [
                r'def\s+\w+\s*\([^)]*\):',
                r'import\s+\w+',
                r'from\s+\w+\s+import',
                r'class\s+\w+',
                r'if\s+__name__\s*==\s*["\']__main__["\']',
                r'print\s*\(',
                r'@\w+',
                r'async\s+def',
                r'yield\s+',
                r'lambda\s+'
            ]
        }
        
        self.code_indicators = [
            r'[{}();]',  # Brackets and semicolons
            r'=\s*[^=]',  # Assignment operators
            r'if\s*\(',   # Control structures
            r'for\s*\(',  # Loops
            r'while\s*\(',
            r'function\s+',  # Function declarations
            r'class\s+',     # Class declarations
            r'import\s+',    # Import statements
            r'#include',     # C/C++ includes
            r'#define',      # C/C++ defines
            r'//',           # Comments
            r'/\*',          # Multi-line comments
            r'->',           # Arrow operators
            r'::',           # Scope resolution
            r'\.',           # Method calls
            r'\[',           # Array access
        ]
    
    def detect_language(self, code: str) -> Tuple[str, float]:
        """Detect programming language with confidence score"""
        if not code or not code.strip():
            return 'unknown', 0.0
        
        code = code.strip()
        language_scores = {}
        
        for lang, patterns in self.language_patterns.items():
            score = 0
            total_patterns = len(patterns)
            
            for pattern in patterns:
                if re.search(pattern, code, re.IGNORECASE | re.MULTILINE):
                    score += 1
            
            # Calculate confidence as percentage of patterns matched
            confidence = (score / total_patterns) * 100
            language_scores[lang] = confidence
        
        # Return language with highest confidence
        if language_scores:
            best_lang = max(language_scores, key=language_scores.get)
            best_score = language_scores[best_lang]
            
            # Only return if confidence is above threshold
            if best_score > 20:  # At least 20% pattern match
                return best_lang, best_score / 100
        
        return 'unknown', 0.0
    
    def is_code(self, text: str) -> Tuple[bool, float]:
        """Check if text is code vs plain text"""
        if not text or not text.strip():
            return False, 0.0
        
        text = text.strip()
        
        # Check for code indicators
        code_indicators_found = 0
        total_indicators = len(self.code_indicators)
        
        for pattern in self.code_indicators:
            if re.search(pattern, text):
                code_indicators_found += 1
        
        # Calculate code probability
        code_probability = code_indicators_found / total_indicators
        
        # Additional checks
        has_brackets = bool(re.search(r'[{}();]', text))
        has_keywords = bool(re.search(r'\b(function|class|def|if|for|while|import|const|let|var)\b', text, re.IGNORECASE))
        has_operators = bool(re.search(r'[=+\-*/%<>!&|]', text))
        
        # Boost probability for strong indicators
        if has_brackets and has_keywords:
            code_probability += 0.3
        if has_operators and has_keywords:
            code_probability += 0.2
        
        # Consider it code if probability > 0.3
        is_code_result = code_probability > 0.3
        
        return is_code_result, min(code_probability, 1.0)
    
    def validate_input(self, text: str) -> Dict[str, any]:
        """Comprehensive input validation"""
        result = {
            'is_valid': False,
            'is_code': False,
            'language': 'unknown',
            'confidence': 0.0,
            'code_confidence': 0.0,
            'errors': []
        }
        
        if not text or not text.strip():
            result['errors'].append('Empty input provided')
            return result
        
        # Check if it's code
        is_code, code_confidence = self.is_code(text)
        result['is_code'] = is_code
        result['code_confidence'] = code_confidence
        
        if not is_code:
            result['errors'].append('Input does not appear to be code')
            return result
        
        # Detect language
        language, lang_confidence = self.detect_language(text)
        result['language'] = language
        result['confidence'] = lang_confidence
        
        if language == 'unknown':
            result['errors'].append('Could not detect programming language')
            return result
        
        # Check minimum length
        if len(text.strip()) < 50:
            result['errors'].append('Code too short for meaningful analysis')
            return result
        
        result['is_valid'] = True
        return result

# Global instance
language_detector = LanguageDetector()
