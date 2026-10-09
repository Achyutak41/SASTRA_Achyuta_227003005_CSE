import { Bot } from "lucide-react";

function LoadingMessage() {
  return (
    <div className="border-b border-gray-800/50 bg-gray-900/50">
      <div className="mx-auto flex max-w-4xl gap-4 px-4 py-6">

        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-gray-700">
          <Bot size={17} className="text-white" />
        </div>

        <div>
          <p className="mb-3 text-sm font-semibold text-gray-300">
            AUTOSAR AI
          </p>

          <div className="flex gap-1.5">

            <span className="h-2 w-2 animate-bounce rounded-full bg-gray-500" />

            <span
              className="h-2 w-2 animate-bounce rounded-full bg-gray-500"
              style={{ animationDelay: "150ms" }}
            />

            <span
              className="h-2 w-2 animate-bounce rounded-full bg-gray-500"
              style={{ animationDelay: "300ms" }}
            />

          </div>
        </div>

      </div>
    </div>
  );
}

export default LoadingMessage;