import {
  BookOpen,
  MessageSquare,
  Plus,
  Settings,
  Trash2,
  X
} from "lucide-react";

function Sidebar({
  conversations,
  activeChat,
  onNewChat,
  onSelectChat,
  onDeleteChat,
  onNavigate,
  isOpen,
  onClose
}) {
  return (
    <aside
      className={`
        fixed inset-y-0 left-0 z-40
        flex w-72 flex-col
        border-r border-gray-800
        bg-gray-950
        transition-transform duration-200
        lg:static lg:translate-x-0
        ${isOpen ? "translate-x-0" : "-translate-x-full"}
      `}
    >
      {/* Header */}

      <div className="flex h-16 items-center justify-between border-b border-gray-800 px-4">
        <div>
          <h1 className="text-lg font-bold text-white">
            AUTOSAR AI
          </h1>

          <p className="text-xs text-gray-500">
            Document Assistant
          </p>
        </div>

        <button
          onClick={onClose}
          className="rounded-lg p-2 text-gray-400 hover:bg-gray-800 hover:text-white lg:hidden"
        >
          <X size={20} />
        </button>
      </div>

      {/* New Chat */}

      <div className="p-3">
        <button
          onClick={onNewChat}
          className="flex w-full items-center justify-center gap-2 rounded-lg bg-orange-500 px-4 py-3 font-semibold text-white transition hover:bg-orange-600"
        >
          <Plus size={18} />

          New Chat
        </button>
      </div>

      {/* Navigation */}

      <div className="px-3">
        <button
          onClick={() => onNavigate("/chat")}
          className="mb-1 flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm text-gray-300 hover:bg-gray-800 hover:text-white"
        >
          <MessageSquare size={18} />

          Chat
        </button>

        <button
          onClick={() => onNavigate("/knowledge-base")}
          className="mb-1 flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm text-gray-300 hover:bg-gray-800 hover:text-white"
        >
          <BookOpen size={18} />

          Knowledge Base
        </button>
      </div>

      {/* Conversation history */}

      <div className="mt-4 flex-1 overflow-y-auto px-3">
        <p className="mb-2 px-3 text-xs font-semibold uppercase tracking-wider text-gray-500">
          Conversations
        </p>

        {conversations.length === 0 ? (
          <p className="px-3 py-4 text-sm text-gray-600">
            No conversations yet.
          </p>
        ) : (
          <div className="space-y-1">
            {conversations.map((conversation) => {
              const isActive =
                conversation.id === activeChat;

              return (
                <div
                  key={conversation.id}
                  className={`
                    group flex items-center rounded-lg
                    ${
                      isActive
                        ? "bg-gray-800"
                        : "hover:bg-gray-900"
                    }
                  `}
                >
                  <button
                    onClick={() =>
                      onSelectChat(conversation.id)
                    }
                    className="flex min-w-0 flex-1 items-center gap-3 px-3 py-2.5 text-left"
                  >
                    <MessageSquare
                      size={16}
                      className="shrink-0 text-gray-500"
                    />

                    <span className="truncate text-sm text-gray-300">
                      {conversation.title}
                    </span>
                  </button>

                  <button
                    onClick={() =>
                      onDeleteChat(conversation.id)
                    }
                    className="mr-1 hidden rounded p-1.5 text-gray-500 hover:bg-gray-700 hover:text-red-400 group-hover:block"
                  >
                    <Trash2 size={15} />
                  </button>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Bottom navigation */}

      <div className="border-t border-gray-800 p-3">
        <button
          onClick={() => onNavigate("/settings")}
          className="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm text-gray-300 hover:bg-gray-800 hover:text-white"
        >
          <Settings size={18} />

          Settings
        </button>
      </div>
    </aside>
  );
}

export default Sidebar;