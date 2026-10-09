import {
  Bot,
  Copy,
  RefreshCw,
  User,
} from "lucide-react";

import { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

function ChatMessage({ message, onRegenerate }) {
  const [copied, setCopied] = useState(false);

  const isUser = message.role === "user";

  const copyMessage = async () => {
    try {
      await navigator.clipboard.writeText(message.content);
      setCopied(true);

      setTimeout(() => setCopied(false), 1500);
    } catch {
      console.error("Unable to copy message.");
    }
  };

  return (
    <div
      className={`
        w-full border-b border-gray-800/50
        ${isUser ? "bg-gray-950" : "bg-gray-900/50"}
      `}
    >
      <div className="mx-auto flex max-w-4xl gap-4 px-4 py-6">
        {/* Avatar */}
        <div
          className={`
            flex h-8 w-8 shrink-0 items-center justify-center rounded-full
            ${isUser ? "bg-orange-500" : "bg-gray-700"}
          `}
        >
          {isUser ? (
            <User size={17} className="text-white" />
          ) : (
            <Bot size={17} className="text-white" />
          )}
        </div>

        {/* Message */}
        <div className="min-w-0 flex-1">
          <p className="mb-3 text-sm font-semibold text-gray-300">
            {isUser ? "You" : "AUTOSAR AI"}
          </p>

          <div className="break-words text-sm leading-7 text-gray-200">
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={{
                p: ({ children }) => (
                  <p className="mb-3 last:mb-0">{children}</p>
                ),

                h1: ({ children }) => (
                  <h1 className="mb-3 mt-5 text-xl font-bold text-white">
                    {children}
                  </h1>
                ),

                h2: ({ children }) => (
                  <h2 className="mb-3 mt-5 text-lg font-bold text-white">
                    {children}
                  </h2>
                ),

                h3: ({ children }) => (
                  <h3 className="mb-2 mt-4 text-base font-semibold text-white">
                    {children}
                  </h3>
                ),

                ul: ({ children }) => (
                  <ul className="mb-3 ml-6 list-disc space-y-1">
                    {children}
                  </ul>
                ),

                ol: ({ children }) => (
                  <ol className="mb-3 ml-6 list-decimal space-y-1">
                    {children}
                  </ol>
                ),

                li: ({ children }) => (
                  <li className="pl-1">{children}</li>
                ),

                strong: ({ children }) => (
                  <strong className="font-semibold text-white">
                    {children}
                  </strong>
                ),

                em: ({ children }) => (
                  <em className="italic text-gray-100">
                    {children}
                  </em>
                ),

                blockquote: ({ children }) => (
                  <blockquote className="my-3 border-l-2 border-orange-500 pl-4 text-gray-400">
                    {children}
                  </blockquote>
                ),

                code: ({ children, className }) => {
                  const isBlock = Boolean(className);

                  return isBlock ? (
                    <code className={`${className} font-mono text-xs`}>
                      {children}
                    </code>
                  ) : (
                    <code className="rounded bg-gray-800 px-1.5 py-0.5 font-mono text-xs text-orange-300">
                      {children}
                    </code>
                  );
                },

                pre: ({ children }) => (
                  <pre className="my-3 overflow-x-auto rounded-lg border border-gray-800 bg-gray-950 p-4 text-sm">
                    {children}
                  </pre>
                ),

                a: ({ children, href }) => (
                  <a
                    href={href}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-orange-400 underline underline-offset-2 hover:text-orange-300"
                  >
                    {children}
                  </a>
                ),

                hr: () => (
                  <hr className="my-4 border-gray-700" />
                ),

                table: ({ children }) => (
                  <div className="my-4 overflow-x-auto">
                    <table className="w-full border-collapse text-left text-sm">
                      {children}
                    </table>
                  </div>
                ),

                th: ({ children }) => (
                  <th className="border border-gray-700 bg-gray-800 px-3 py-2 font-semibold text-white">
                    {children}
                  </th>
                ),

                td: ({ children }) => (
                  <td className="border border-gray-800 px-3 py-2">
                    {children}
                  </td>
                ),
              }}
            >
              {message.content || ""}
            </ReactMarkdown>
          </div>

          {/* Actions */}
          <div className="mt-4 flex items-center gap-2">
            <button
              type="button"
              onClick={copyMessage}
              className="flex items-center gap-1.5 rounded-md px-2 py-1.5 text-xs text-gray-500 hover:bg-gray-800 hover:text-gray-300"
            >
              <Copy size={14} />
              {copied ? "Copied" : "Copy"}
            </button>

            {!isUser && onRegenerate && (
              <button
                type="button"
                onClick={() => onRegenerate(message)}
                className="flex items-center gap-1.5 rounded-md px-2 py-1.5 text-xs text-gray-500 hover:bg-gray-800 hover:text-gray-300"
              >
                <RefreshCw size={14} />
                Regenerate
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default ChatMessage;