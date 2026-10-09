import {
  Menu,
  ShieldCheck,
  RefreshCw,
  AlertCircle,
  FileText,
} from "lucide-react";

import { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";
import useAuth from "../hooks/useAuth";
import useChat from "../hooks/useChat";

import Sidebar from "../components/sidebar";
import ChatMessage from "../components/ChatMessage";
import ChatInput from "../components/ChatInput";
import LoadingMessage from "../components/LoadingMessage";
import SourceCard from "../components/SourceCard";
import UserMenu from "../components/UserMenu";

function Chat() {
  const navigate = useNavigate();

  const { user, logout } = useAuth();
const [lastQuestion, setLastQuestion] = useState("");

  const {
  conversations,
  activeChat,
  messages,
  loading: conversationsLoading,
  chatError,
  createNewChat,
  selectChat,
  deleteChat,
  addMessage,
} = useChat();

  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const [documents, setDocuments] = useState([]);
  const [selectedDocumentId, setSelectedDocumentId] = useState("");

  const [documentsLoading, setDocumentsLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");
  const [sources, setSources] = useState([]);

  const loadDocuments = useCallback(async () => {
    setDocumentsLoading(true);

    try {
      const response = await api.get("/documents");
      const list = response.data.documents || [];

      setDocuments(list);

      setSelectedDocumentId((currentId) => {
        const current = list.find(
          (document) => String(document.id) === String(currentId)
        );

        if (current && current.status === "processed") {
          return String(current.id);
        }

        const readyDocument = list.find(
          (document) => document.status === "processed"
        );

        return readyDocument ? String(readyDocument.id) : "";
      });
    } catch (err) {
      setError(
        err.response?.data?.error ||
          "Could not load your documents. Check that the backend is running and you are logged in."
      );
    } finally {
      setDocumentsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadDocuments();
  }, [loadDocuments]);

  const handleNewChat = async () => {
  try {
    await createNewChat();
    setInput("");
    setSources([]);
    setError("");
    setSidebarOpen(false);
  } catch (err) {
    setError(
      err.response?.data?.error ||
        "Could not create a conversation."
    );
  }
};

const handleSelectChat = async (id) => {
  try {
    await selectChat(id);
    setInput("");
    setSources([]);
    setError("");
    setLastQuestion("");
    setSidebarOpen(false);
  } catch (err) {
    setError(
      err.response?.data?.error ||
        "Could not load this conversation."
    );
  }
};

const handleDeleteChat = async (id) => {
  try {
    await deleteChat(id);
    setSources([]);
    setError("");
  } catch (err) {
    setError(
      err.response?.data?.error ||
        "Could not delete this conversation."
    );
  }
};

  

  
const handleSend = async () => {
  const question = input.trim();

  if (!question || loading) return;

  if (!selectedDocumentId) {
    setError("Please select a processed PDF before asking a question.");
    return;
  }

  setError("");
  setSources([]);
  setInput("");
  setLoading(true);
  setLastQuestion(question);

  let conversationId = activeChat;

  try {
    // Ensure the question has a database conversation to belong to.
    if (conversationId == null) {
      const created = await createNewChat();
      conversationId = created.id;
    }

    await addMessage(
      {
        role: "user",
        content: question,
      },
      conversationId
    );

    const response = await api.post("/chat/ask", {
      document_id: Number(selectedDocumentId),
      question,
      top_k: 5,
      chunking_strategy: "fixed",
      embedding_model: "minilm",
    });

    const data = response.data;
    const answer =
      data.answer || "The backend returned an empty answer.";

    const citations = data.citations || [];

    await addMessage(
      {
        role: "assistant",
        content: answer,
        citations,
      },
      conversationId
    );

    setSources(
      citations.map((citation, index) => ({
        ...citation,
        id: citation.chunk_id ?? `source-${index + 1}`,
        name:
          citation.filename ||
          citation.original_filename ||
          `Source ${index + 1}`,
        page: citation.page_number,
        preview: citation.excerpt || "",
      }))
    );
  } catch (err) {
    const message =
      err.response?.data?.error ||
      err.response?.data?.details ||
      err.message ||
      "An unexpected error occurred.";

    setError(`Unable to complete the request: ${message}`);
  } finally {
    setLoading(false);
  }
};
 

  const handleFileUpload = async (event) => {
    const file = event.target.files?.[0];

    // Allow selecting the same file again after a failed attempt.
    event.target.value = "";

    if (!file) {
      return;
    }

    if (
      !file.name.toLowerCase().endsWith(".pdf") ||
      (file.type && file.type !== "application/pdf")
    ) {
      setError("Please select a valid PDF file.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    setError("");
    setUploading(true);

    try {
      const response = await api.post(
        "/documents/upload",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
          timeout: 300000,
        }
      );

      const document = response.data.document;

      if (document?.id) {
        await loadDocuments();

        if (document.status === "processed") {
          setSelectedDocumentId(String(document.id));
        }

        addMessage({
          id: `message-${Date.now()}`,
          role: "assistant",
          content:
            response.data.message ||
            `Uploaded ${document.original_filename}.`,
        });

        if (document.status !== "processed") {
          setError(
            response.data.indexing_error ||
              document.error_message ||
              "The PDF was uploaded, but indexing did not complete. Check its status in the Knowledge Base."
          );
        }
      } else {
        await loadDocuments();
        setError("The server did not return the uploaded document details.");
      }
    } catch (err) {
      const message =
        err.response?.data?.error ||
        err.response?.data?.message ||
        err.message ||
        "Upload failed.";

      setError(`PDF upload failed: ${message}`);
      await loadDocuments();
    } finally {
      setUploading(false);
    }
  };

  const handleRegenerate = async () => {
  if (!lastQuestion || !selectedDocumentId || loading) {
    return;
  }

  setError("");
  setLoading(true);

  try {
    const response = await api.post("/chat/ask", {
      document_id: Number(selectedDocumentId),
      question: lastQuestion,
      top_k: 5,
      chunking_strategy: "fixed",
      embedding_model: "minilm",
    });

    const data = response.data;

    addMessage({
      id: `message-${Date.now()}`,
      role: "assistant",
      content: data.answer || "The backend returned an empty answer.",
    });

    setSources(
      (data.citations || []).map((citation, index) => ({
        ...citation,
        id: citation.chunk_id ?? `source-${index + 1}`,
        name:
          citation.filename ||
          citation.original_filename ||
          `Source ${index + 1}`,
        page: citation.page_number,
        preview: citation.excerpt || "",
      }))
    );
  } catch (err) {
    setError(
      err.response?.data?.error ||
        err.response?.data?.details ||
        "Failed to regenerate the answer."
    );
  } finally {
    setLoading(false);
  }
};


  const handleLogout = () => {
    logout();

    navigate("/login", {
      replace: true,
    });
  };

  const readyDocuments = documents.filter(
    (document) => document.status === "processed"
  );

  return (
    <div className="flex h-screen overflow-hidden bg-gray-950 text-white">
      <Sidebar
        conversations={conversations}
        activeChat={activeChat}
        onNewChat={handleNewChat}
        onSelectChat={handleSelectChat}
        onDeleteChat={handleDeleteChat}
        onNavigate={navigate}
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />

      {sidebarOpen && (
        <button
          aria-label="Close sidebar"
          onClick={() => setSidebarOpen(false)}
          className="fixed inset-0 z-30 bg-black/60 lg:hidden"
        />
      )}

      <main className="flex min-w-0 flex-1 flex-col">
        <header className="flex h-16 shrink-0 items-center justify-between border-b border-gray-800 bg-gray-950 px-4">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setSidebarOpen(true)}
              aria-label="Open sidebar"
              className="rounded-lg p-2 text-gray-400 hover:bg-gray-800 hover:text-white lg:hidden"
            >
              <Menu size={21} />
            </button>

            <div>
              <h2 className="text-sm font-semibold text-gray-200">
                AUTOSAR AI Assistant
              </h2>

              <div className="flex items-center gap-1.5 text-xs text-gray-500">
                <span
                  className={`h-1.5 w-1.5 rounded-full ${
                    readyDocuments.length > 0
                      ? "bg-green-500"
                      : "bg-yellow-500"
                  }`}
                />
                {readyDocuments.length > 0
                  ? `${readyDocuments.length} processed document(s)`
                  : "No processed documents"}
              </div>
            </div>
          </div>

          <UserMenu
            user={user}
            onLogout={handleLogout}
            onSettings={() => navigate("/settings")}
          />
        </header>

        <div className="border-b border-gray-800 bg-gray-900/60 px-4 py-3">
          <div className="mx-auto flex max-w-4xl flex-col gap-2 sm:flex-row sm:items-center">
            <label
              htmlFor="chat-document"
              className="flex shrink-0 items-center gap-2 text-sm text-gray-300"
            >
              <FileText size={16} />
              Ask about PDF
            </label>

            <select
              id="chat-document"
              value={selectedDocumentId}
              onChange={(event) => {
                setSelectedDocumentId(event.target.value);
                setSources([]);
                setError("");
              }}
              disabled={documentsLoading || loading || uploading}
              className="min-w-0 flex-1 rounded-lg border border-gray-700 bg-gray-950 px-3 py-2 text-sm text-gray-200 outline-none focus:border-orange-500 disabled:opacity-50"
            >
              <option value="">
                {documentsLoading
                  ? "Loading documents..."
                  : "Select a processed PDF"}
              </option>

              {readyDocuments.map((document) => (
                <option key={document.id} value={String(document.id)}>
                  {document.original_filename}
                </option>
              ))}
            </select>

            <button
              type="button"
              onClick={loadDocuments}
              disabled={documentsLoading || loading || uploading}
              title="Refresh document list"
              className="flex items-center justify-center gap-2 rounded-lg border border-gray-700 px-3 py-2 text-sm text-gray-300 hover:bg-gray-800 disabled:opacity-50"
            >
              <RefreshCw
                size={15}
                className={documentsLoading ? "animate-spin" : ""}
              />
              Refresh
            </button>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto">
          {messages.length === 0 ? (
            <div className="flex min-h-full items-center justify-center px-6 py-10">
              <div className="max-w-xl text-center">
                <div className="mx-auto mb-5 flex h-16 w-16 items-center justify-center rounded-2xl bg-orange-500/10">
                  <ShieldCheck size={32} className="text-orange-400" />
                </div>

                <h2 className="text-2xl font-bold text-white">
                  Ask your AUTOSAR documents
                </h2>

                <p className="mt-3 text-sm leading-6 text-gray-500">
                  Select a processed PDF, ask a question, and receive an answer
                  generated from retrieved document evidence.
                </p>

                {readyDocuments.length === 0 && !documentsLoading && (
                  <p className="mt-4 text-sm text-yellow-400">
                    Upload and process a PDF to get started.
                  </p>
                )}
              </div>
            </div>
          ) : (
            <>
              {messages.map((message) => (
                <ChatMessage
                  key={message.id}
                  message={message}
                  onRegenerate={
                    message.role === "assistant"
                      ? handleRegenerate
                      : undefined
                  }
                />
              ))}

              {loading && <LoadingMessage />}

              {!loading && sources.length > 0 && (
                <div className="mx-auto max-w-4xl px-4 py-6">
                  <h3 className="mb-3 text-sm font-semibold text-gray-300">
                    Retrieved sources
                  </h3>

                  <div className="grid gap-3 md:grid-cols-2">
                    {sources.map((source, index) => (
                      <div key={`${source.id}-${index}`}>
                        <SourceCard source={source} />
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          )}
        </div>

        {error && (
          <div
            role="alert"
            className="mx-auto flex w-full max-w-4xl items-start gap-2 px-4 pb-3 text-sm text-red-300"
          >
            <AlertCircle size={17} className="mt-0.5 shrink-0" />
            <span>{error}</span>
            <button
              type="button"
              onClick={() => setError("")}
              className="ml-auto text-red-200 underline"
            >
              Dismiss
            </button>
          </div>
        )}

        {uploading && (
          <p className="px-4 pb-2 text-center text-xs text-orange-300">
            Uploading, extracting text, and building the document index...
          </p>
        )}

        <ChatInput
          value={input}
          onChange={setInput}
          onSend={handleSend}
          onFileUpload={handleFileUpload}
          disabled={
            loading ||
            uploading ||
            documentsLoading ||
            !selectedDocumentId
          }
        />
      </main>
    </div>
  );
}

export default Chat;