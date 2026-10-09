
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";

import api from "../services/api";

const ChatContext = createContext(null);

export function ChatProvider({ children }) {
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
          saved.some((chat) => String(chat.id) === String(currentId))
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

  useEffect(() => {
    // The Axios interceptor reads the existing autosar_token.
    if (!localStorage.getItem("autosar_token")) {
      setConversations([]);
      setActiveChat(null);
      setLoading(false);
      return;
    }

    loadConversations().catch(() => {});
  }, [loadConversations]);

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

    setConversations((previous) => [created, ...previous]);
    setActiveChat(created.id);

    return created;
  }, []);

  // Retrieve messages from the database when a chat is selected.
  const selectChat = useCallback(async (chatId) => {
    setChatError("");

    const response = await api.get(`/conversations/${chatId}`);
    const detail = response.data.conversation;
    const savedMessages = response.data.messages || [];

    const restored = {
      ...detail,
      messages: savedMessages.map((message) => ({
        ...message,
        id: message.id,
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

  // Persist first, then update the React state.
  const addMessage = useCallback(async (message, conversationId) => {
    const targetId = conversationId ?? activeChat;

    if (targetId == null) {
      throw new Error("Create or select a conversation first.");
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
      id: response.data.message.id,
      role: response.data.message.role,
      content: response.data.message.content,
      citations: response.data.message.citations || [],
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
              ? message.content.replace(/\s+/g, " ").trim().slice(0, 45)
              : chat.title,
          updated_at: saved.created_at,
          messages: [...(chat.messages || []), saved],
          message_count: (chat.message_count || 0) + 1,
        };
      })
    );

    return saved;
  }, [activeChat]);

  const addMessages = useCallback(async (newMessages) => {
    for (const message of newMessages) {
      await addMessage(message);
    }
  }, [addMessage]);

  const setCurrentMessages = useCallback(
    (newMessages) => {
      // Message replacement is intentionally not persisted implicitly.
      // Use addMessage for durable writes to avoid accidental duplicates.
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

  const deleteChat = useCallback(async (chatId) => {
    setChatError("");

    await api.delete(`/conversations/${chatId}`);

    setConversations((previous) =>
      previous.filter(
        (chat) => String(chat.id) !== String(chatId)
      )
    );

    setActiveChat((current) =>
      String(current) === String(chatId) ? null : current
    );
  }, []);

  const clearChats = useCallback(async () => {
    const current = [...conversations];

    for (const chat of current) {
      await api.delete(`/conversations/${chat.id}`);
    }

    setConversations([]);
    setActiveChat(null);
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
