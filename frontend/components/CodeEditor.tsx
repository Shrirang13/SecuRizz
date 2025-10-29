import React, { useRef, useEffect } from 'react';
import Editor from '@monaco-editor/react';

interface CodeEditorProps {
  code: string;
  onChange?: (value: string) => void;
  readOnly?: boolean;
  highlightedLines?: number[];
  language?: string;
  height?: string;
}

const CodeEditor: React.FC<CodeEditorProps> = ({
  code,
  onChange,
  readOnly = false,
  highlightedLines = [],
  language = 'solidity',
  height = '400px'
}) => {
  const editorRef = useRef<any>(null);

  const handleEditorDidMount = (editor: any, monaco: any) => {
    editorRef.current = editor;
    
    // Configure Solidity language support
    monaco.languages.register({ id: 'solidity' });
    monaco.languages.setMonarchTokensProvider('solidity', {
      tokenizer: {
        root: [
          [/pragma|contract|function|modifier|event|struct|enum|mapping/, 'keyword'],
          [/uint\d+|int\d+|address|bool|string|bytes\d*/, 'type'],
          [/public|private|internal|external|view|pure|payable/, 'modifier'],
          [/require|assert|revert/, 'function.builtin'],
          [/msg\.sender|msg\.value|block\.timestamp|tx\.origin/, 'variable.predefined'],
          [/\/\/.*$/, 'comment'],
          [/\/\*[\s\S]*?\*\//, 'comment'],
          [/[{}()\[\]]/, 'delimiter'],
          [/\d+/, 'number'],
          [/"[^"]*"/, 'string'],
          [/'.*'/, 'string'],
        ]
      }
    });

    // Set theme
    monaco.editor.defineTheme('securizz-theme', {
      base: 'vs-dark',
      inherit: true,
      rules: [
        { token: 'keyword', foreground: 'C586C0' },
        { token: 'type', foreground: '4EC9B0' },
        { token: 'modifier', foreground: 'DCDCAA' },
        { token: 'function.builtin', foreground: 'DCDCAA' },
        { token: 'variable.predefined', foreground: '569CD6' },
        { token: 'comment', foreground: '6A9955' },
        { token: 'string', foreground: 'CE9178' },
        { token: 'number', foreground: 'B5CEA8' },
      ],
      colors: {
        'editor.background': '#1e1e1e',
        'editor.foreground': '#d4d4d4',
        'editorLineNumber.foreground': '#858585',
        'editor.selectionBackground': '#264f78',
        'editor.inactiveSelectionBackground': '#3a3d41',
      }
    });

    monaco.editor.setTheme('securizz-theme');
  };

  useEffect(() => {
    if (editorRef.current && highlightedLines.length > 0) {
      // Add line highlighting for vulnerabilities
      const decorations = highlightedLines.map(lineNumber => ({
        range: {
          startLineNumber: lineNumber,
          startColumn: 1,
          endLineNumber: lineNumber,
          endColumn: 1
        },
        options: {
          isWholeLine: true,
          className: 'vulnerable-line',
          glyphMarginClassName: 'vulnerable-glyph'
        }
      }));

      editorRef.current.deltaDecorations([], decorations);
    }
  }, [highlightedLines]);

  return (
    <div className="relative">
      <Editor
        height={height}
        language={language}
        value={code}
        onChange={onChange}
        onMount={handleEditorDidMount}
        options={{
          readOnly,
          minimap: { enabled: false },
          fontSize: 14,
          lineNumbers: 'on',
          roundedSelection: false,
          scrollBeyondLastLine: false,
          automaticLayout: true,
          wordWrap: 'on',
          theme: 'securizz-theme',
          renderLineHighlight: 'line',
          cursorStyle: 'line',
          selectOnLineNumbers: true,
          glyphMargin: true,
          folding: true,
          lineDecorationsWidth: 10,
          lineNumbersMinChars: 3,
        }}
      />
      <style jsx global>{`
        .monaco-editor .vulnerable-line {
          background-color: rgba(255, 0, 0, 0.1) !important;
          border-left: 3px solid #ff4444 !important;
        }
        .monaco-editor .vulnerable-glyph {
          background-color: #ff4444 !important;
        }
      `}</style>
    </div>
  );
};

export default CodeEditor;

