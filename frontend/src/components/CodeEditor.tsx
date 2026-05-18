import Editor from "@monaco-editor/react";

interface Props {
  value: string;
  onChange: (v: string) => void;
  readOnly?: boolean;
}

export function CodeEditor({ value, onChange, readOnly = false }: Props) {
  return (
    <div className="h-full w-full border-2 border-maze">
      <Editor
        height="100%"
        defaultLanguage="python"
        value={value}
        onChange={(v) => onChange(v ?? "")}
        theme="vs-dark"
        options={{
          readOnly,
          fontFamily: "ui-monospace, SFMono-Regular, Menlo, monospace",
          fontSize: 14,
          minimap: { enabled: false },
          scrollBeyondLastLine: false,
          tabSize: 4,
          lineNumbers: "on",
          renderLineHighlight: "gutter",
          padding: { top: 12, bottom: 12 },
        }}
      />
    </div>
  );
}
