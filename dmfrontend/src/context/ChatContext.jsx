
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";

import api from "../services/api";
import useAuth from "../hooks/useAuth";

const ChatContext = createContext(null);

export function ChatProvider({ children }) {
  // Hooks must be called inside the component function.
  const {
    isAuthenticated,
    loading: authLoading,
  } = useAuth();

  const [conversations, setConversations] = useState([]);
  const [activeChat, setActiveChat] = useState(null);
  const [loading, setLoading] = useState(true);
  const [chatError, setChatError] = useState("");

  // Load conversations belonging to the authenticated user.
  const loadConversations = useCallback(async () => {
    setLoading(true);
    setChatError("");

    try {
      const response = await api.get("/conversations");
      const saved = response.data.conversations || [];

      setConversations(saved);

      setActiveChat((currentId) => {
        if (
          currentId != null &&
          saved.some(
            (chat) => String(chat.id) === String(currentId)
          )
        ) {
          return currentId;
        }

        return saved[0]?.id ?? null;
      });

      return saved;
    } catch (error) {
      setChatError(
        error.response?.data?.error ||
          "Could not load saved conversations."
      );
      throw error;
    } finally {
      setLoading(false);
    }
  }, []);

  // Load history when authentication restoration finishes
  // or when the user becomes authenticated.
  useEffect(() => {
    if (authLoading) {
      setLoading(true);
      return;
    }

    if (!isAuthenticated) {
      setConversations([]);
      setActiveChat(null);
      setChatError("");
      setLoading(false);
      return;
    }

    let cancelled = false;

    const fetchConversations = async () => {
      try {
        await loadConversations();
      } catch {
        // The error is recorded by loadConversations.
      }
    };

    fetchConversations();

    return () => {
      cancelled = true;
    };
  }, [isAuthenticated, authLoading, loadConversations]);

  const currentChat = useMemo(
    () =>
      conversations.find(
        (chat) => String(chat.id) === String(activeChat)
      ) || null,
    [conversations, activeChat]
  );

  const messages = currentChat?.messages || [];

  // Create the conversation in SQLite before using it.
  const createNewChat = useCallback(async () => {
    setChatError("");

    const response = await api.post("/conversations", {
      title: "New conversation",
    });

    const created = {
      ...response.data.conversation,
      messages: [],
    };

    setConversations((previous) => [
      created,
      ...previous,
    ]);

    setActiveChat(created.id);

    return created;
  }, []);

  // Retrieve saved messages when a conversation is selected.
  const selectChat = useCallback(async (chatId) => {
    setChatError("");

    const response = await api.get(
      `/conversations/${chatId}`
    );

    const detail = response.data.conversation;
    const savedMessages = response.data.messages || [];

    const restored = {
      ...detail,
      messages: savedMessages.map((message) => ({
        ...message,
        role: message.role,
        content: message.content,
        citations: message.citations || [],
      })),
    };

    setConversations((previous) => [
      restored,
      ...previous.filter(
        (chat) => String(chat.id) !== String(chatId)
      ),
    ]);

    setActiveChat(restored.id);

    return restored;
  }, []);

  // Persist a message before updating React state.
  const addMessage = useCallback(
    async (message, conversationId) => {
      const targetId = conversationId ?? activeChat;

      if (targetId == null) {
        throw new Error(
          "Create or select a conversation first."
        );
      }

      const response = await api.post(
        `/conversations/${targetId}/messages`,
        {
          role: message.role,
          content: message.content,
          citations: message.citations || [],
        }
      );

      const saved = {
        ...response.data.message,
        role: response.data.message.role,
        content: response.data.message.content,
        citations:
          response.data.message.citations || [],
      };

      setConversations((previous) =>
        previous.map((chat) => {
          if (String(chat.id) !== String(targetId)) {
            return chat;
          }

          return {
            ...chat,
            title:
              message.role === "user" &&
              chat.title === "New conversation"
                ? message.content
                    .replace(/\s+/g, " ")
                    .trim()
                    .slice(0, 45)
                : chat.title,
            updated_at: saved.created_at,
            messages: [
              ...(chat.messages || []),
              saved,
            ],
            message_count:
              (chat.message_count || 0) + 1,
          };
        })
      );

      return saved;
    },
    [activeChat]
  );

  const addMessages = useCallback(
    async (newMessages) => {
      for (const message of newMessages) {
        await addMessage(message);
      }
    },
    [addMessage]
  );

  // Update displayed messages without implicitly saving duplicates.
  const setCurrentMessages = useCallback(
    (newMessages) => {
      setConversations((previous) =>
        previous.map((chat) =>
          String(chat.id) === String(activeChat)
            ? { ...chat, messages: newMessages }
            : chat
        )
      );
    },
    [activeChat]
  );

  // Delete a conversation belonging to the current user.
  const deleteChat = useCallback(async (chatId) => {
    setChatError("");

    await api.delete(`/conversations/${chatId}`);

    setConversations((previous) =>
      previous.filter(
        (chat) => String(chat.id) !== String(chatId)
      )
    );

    setActiveChat((current) =>
      String(current) === String(chatId)
        ? null
        : current
    );
  }, []);

  // Delete all conversations currently loaded for this user.
  const clearChats = useCallback(async () => {
    const current = [...conversations];

    for (const chat of current) {
      await api.delete(`/conversations/${chat.id}`);
    }

    setConversations([]);
    setActiveChat(null);
    setChatError("");
  }, [conversations]);

  return (
    <ChatContext.Provider
      value={{
        conversations,
        activeChat,
        currentChat,
        messages,
        loading,
        chatError,
        loadConversations,
        createNewChat,
        selectChat,
        deleteChat,
        addMessage,
        addMessages,
        setCurrentMessages,
        clearChats,
      }}
    >
      {children}
    </ChatContext.Provider>
  );
}

export function useChatContext() {
  return useContext(ChatContext);
}
