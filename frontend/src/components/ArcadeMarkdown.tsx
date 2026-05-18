import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

/**
 * Markdown renderer styled to match the arcade aesthetic:
 *   - h1/h2/h3 use Press Start 2P with neon colors
 *   - inline code = green-bordered chip
 *   - code blocks = bordered monospace block with neon-green text
 *   - bold = neon-yellow, em = cyan
 *   - tables = bordered, blockquotes = pink border-left
 *
 * Body text inherits VT323 from the parent container.
 */
export function ArcadeMarkdown({ source }: { source: string }) {
  if (!source) return null;
  return (
    <div className="arcade-md text-[16px] leading-relaxed">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          h1: ({ node, ...props }) => (
            <h1 className="neon-pink font-arcade text-sm mt-4 mb-2" {...props} />
          ),
          h2: ({ node, ...props }) => (
            <h2 className="neon-yellow font-arcade text-xs mt-4 mb-2" {...props} />
          ),
          h3: ({ node, ...props }) => (
            <h3 className="neon-cyan font-arcade text-[10px] uppercase mt-4 mb-1 tracking-widest" {...props} />
          ),
          h4: ({ node, ...props }) => (
            <h4 className="neon-orange font-arcade text-[10px] uppercase mt-3 mb-1 tracking-widest" {...props} />
          ),
          p: ({ node, ...props }) => (
            <p className="my-2 opacity-90" {...props} />
          ),
          strong: ({ node, ...props }) => (
            <strong className="text-pac font-semibold" {...props} />
          ),
          em: ({ node, ...props }) => (
            <em className="text-inky not-italic" {...props} />
          ),
          ul: ({ node, ...props }) => (
            <ul className="list-disc pl-5 space-y-1 my-2" {...props} />
          ),
          ol: ({ node, ...props }) => (
            <ol className="list-decimal pl-5 space-y-1 my-2" {...props} />
          ),
          li: ({ node, ...props }) => (
            <li className="opacity-90" {...props} />
          ),
          blockquote: ({ node, ...props }) => (
            <blockquote
              className="border-l-2 border-pinky pl-3 my-3 text-pinky/90 italic"
              {...props}
            />
          ),
          code({ node, className, children, ...props }: any) {
            const match = /language-(\w+)/.exec(className || "");
            const isInline = !match && !String(children).includes("\n");
            if (isInline) {
              return (
                <code
                  className="px-1.5 py-0.5 mx-0.5 bg-black/60 border border-inky/40 text-inky rounded font-mono text-[13px]"
                  {...props}
                >
                  {children}
                </code>
              );
            }
            return (
              <pre className="my-3 p-3 bg-black/70 border-2 border-maze rounded overflow-x-auto">
                <code
                  className="font-mono text-[12px] text-green-300 leading-snug whitespace-pre"
                  {...props}
                >
                  {String(children).replace(/\n$/, "")}
                </code>
              </pre>
            );
          },
          table: ({ node, ...props }) => (
            <div className="my-3 overflow-x-auto">
              <table
                className="border-collapse border-2 border-maze text-[14px]"
                {...props}
              />
            </div>
          ),
          thead: ({ node, ...props }) => (
            <thead className="bg-maze/30" {...props} />
          ),
          th: ({ node, ...props }) => (
            <th className="border border-maze px-2 py-1 text-left neon-yellow font-arcade text-[10px]" {...props} />
          ),
          td: ({ node, ...props }) => (
            <td className="border border-maze/60 px-2 py-1" {...props} />
          ),
          hr: () => (
            <hr className="my-4 border-0 border-t border-maze/50" />
          ),
          a: ({ node, ...props }) => (
            <a
              className="text-inky underline hover:no-underline"
              target="_blank"
              rel="noreferrer"
              {...props}
            />
          ),
        }}
      >
        {source}
      </ReactMarkdown>
    </div>
  );
}
