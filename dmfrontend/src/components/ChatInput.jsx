import {
  ArrowUp,
  Paperclip
} from "lucide-react";

function ChatInput({
  value,
  onChange,
  onSend,
  onFileUpload,
  disabled
}) {
  const handleKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();

      onSend();
    }
  };

  return (
    <div className="border-t border-gray-800 bg-gray-950 p-4">

      <div className="mx-auto max-w-4xl">

        <div className="flex items-end gap-2 rounded-2xl border border-gray-700 bg-gray-900 px-3 py-2 shadow-lg">

          {/* File upload */}

          <label className="cursor-pointer rounded-lg p-2 text-gray-400 hover:bg-gray-800 hover:text-white">
            <Paperclip size={20} />

            <input
              type="file"
              accept=".pdf"
              className="hidden"
              onChange={onFileUpload}
            />
          </label>

          {/* Input */}

          <textarea
            value={value}
            onChange={(event) =>
              onChange(event.target.value)
            }
            onKeyDown={handleKeyDown}
            disabled={disabled}
            rows={1}
            placeholder="Ask a question about your AUTOSAR documents..."
            className="max-h-32 min-h-10 flex-1 resize-none bg-transparent px-2 py-2 text-sm text-white outline-none placeholder:text-gray-500 disabled:cursor-not-allowed"
          />

          {/* Send */}

          <button
            onClick={onSend}
            disabled={
              disabled || !value.trim()
            }
            className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-orange-500 text-white transition hover:bg-orange-600 disabled:cursor-not-allowed disabled:opacity-40"
          >
            <ArrowUp size={19} />
          </button>

        </div>

        <p className="mt-2 text-center text-xs text-gray-600">
          AUTOSAR AI Assistant can make mistakes.
          Verify important information.
        </p>

      </div>

    </div>
  );
}

export default ChatInput;