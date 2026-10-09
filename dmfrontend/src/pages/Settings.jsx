import {
  ArrowLeft,
  Database,
  Moon,
  Shield,
  Trash2,
  User
} from "lucide-react";

import { useState } from "react";
import { useNavigate } from "react-router-dom";

import useAuth from "../hooks/useAuth";
import useChat from "../hooks/useChat";

function Settings() {
  const navigate = useNavigate();

  const {
    user,
    logout
  } = useAuth();

  const {
    conversations,
    clearChats
  } = useChat();

  const [message, setMessage] =
    useState("");

  const handleLogout = () => {
    logout();

    navigate("/login", {
      replace: true
    });
  };

  const handleClearChats = () => {
    const confirmed =
      window.confirm(
        "Are you sure you want to clear all local conversations?"
      );

    if (!confirmed) {
      return;
    }

    clearChats();

    setMessage(
      "Conversations cleared successfully."
    );

    setTimeout(() => {
      setMessage("");
    }, 3000);
  };

  return (
    <div className="min-h-screen bg-gray-950 text-white">

      {/* Header */}

      <header className="border-b border-gray-800">

        <div className="mx-auto flex max-w-5xl items-center gap-4 px-6 py-4">

          <button
            onClick={() =>
              navigate("/chat")
            }
            className="rounded-lg p-2 text-gray-400 hover:bg-gray-800 hover:text-white"
            aria-label="Back to chat"
          >
            <ArrowLeft size={20} />
          </button>

          <div>
            <h1 className="text-lg font-bold">
              Settings
            </h1>

            <p className="text-xs text-gray-500">
              Manage your AUTOSAR AI Assistant
            </p>
          </div>

        </div>

      </header>

      {/* Content */}

      <main className="mx-auto max-w-5xl px-6 py-8">

        {/* Account */}

        <section>

          <div className="mb-4">

            <h2 className="text-lg font-semibold">
              Account
            </h2>

            <p className="mt-1 text-sm text-gray-500">
              Your current account information
            </p>

          </div>

          <div className="rounded-2xl border border-gray-800 bg-gray-900/40">

            <div className="flex items-center gap-4 p-5">

              <div className="flex h-12 w-12 items-center justify-center rounded-full bg-orange-500">
                <User
                  size={22}
                  className="text-white"
                />
              </div>

              <div className="min-w-0">

                <p className="truncate font-medium text-gray-200">
                  {user?.name ||
                    "AUTOSAR User"}
                </p>

                <p className="mt-1 truncate text-sm text-gray-500">
                  {user?.email ||
                    "No email available"}
                </p>

              </div>

            </div>

          </div>

        </section>

        {/* Appearance */}

        <section className="mt-8">

          <div className="mb-4">

            <h2 className="text-lg font-semibold">
              Appearance
            </h2>

            <p className="mt-1 text-sm text-gray-500">
              Customize the application interface
            </p>

          </div>

          <div className="rounded-2xl border border-gray-800 bg-gray-900/40">

            <div className="flex items-center justify-between p-5">

              <div className="flex items-center gap-4">

                <div className="rounded-lg bg-gray-800 p-2.5">
                  <Moon
                    size={20}
                    className="text-gray-300"
                  />
                </div>

                <div>

                  <p className="text-sm font-medium text-gray-200">
                    Dark Mode
                  </p>

                  <p className="mt-1 text-xs text-gray-500">
                    Dark theme is currently enabled.
                  </p>

                </div>

              </div>

              <div className="rounded-full bg-orange-500/20 px-3 py-1 text-xs font-medium text-orange-400">
                Active
              </div>

            </div>

          </div>

        </section>

        {/* Knowledge Base */}

        <section className="mt-8">

          <div className="mb-4">

            <h2 className="text-lg font-semibold">
              Knowledge Base
            </h2>

            <p className="mt-1 text-sm text-gray-500">
              Status of your knowledge-base data
            </p>

          </div>

          <div className="rounded-2xl border border-gray-800 bg-gray-900/40">

            <div className="flex items-center justify-between p-5">

              <div className="flex items-center gap-4">

                <div className="rounded-lg bg-gray-800 p-2.5">
                  <Database
                    size={20}
                    className="text-orange-400"
                  />
                </div>

                <div>

                  <p className="text-sm font-medium text-gray-200">
                    Knowledge Base
                  </p>

                  <p className="mt-1 text-xs text-gray-500">
                    Document processing will be connected
                    to the Flask backend later.
                  </p>

                </div>

              </div>

              <span className="text-xs text-green-400">
                Ready
              </span>

            </div>

          </div>

        </section>

        {/* Local Data */}

        <section className="mt-8">

          <div className="mb-4">

            <h2 className="text-lg font-semibold">
              Local Data
            </h2>

            <p className="mt-1 text-sm text-gray-500">
              Manage conversations stored in this browser
            </p>

          </div>

          <div className="rounded-2xl border border-gray-800 bg-gray-900/40">

            <div className="flex flex-col gap-4 p-5 sm:flex-row sm:items-center sm:justify-between">

              <div>

                <p className="text-sm font-medium text-gray-200">
                  Conversations
                </p>

                <p className="mt-1 text-xs text-gray-500">
                  {conversations.length} conversation
                  {conversations.length !== 1
                    ? "s"
                    : ""} stored locally.
                </p>

              </div>

              <button
                onClick={
                  handleClearChats
                }
                className="flex items-center justify-center gap-2 rounded-lg border border-red-900/50 px-4 py-2.5 text-sm text-red-400 hover:bg-red-950/30"
              >
                <Trash2 size={16} />

                Clear Conversations
              </button>

            </div>

          </div>

          {message && (
            <div className="mt-3 rounded-lg border border-green-900/50 bg-green-950/20 px-4 py-3 text-sm text-green-400">
              {message}
            </div>
          )}

        </section>

        {/* Security */}

        <section className="mt-8">

          <div className="mb-4">

            <h2 className="text-lg font-semibold">
              Security
            </h2>

            <p className="mt-1 text-sm text-gray-500">
              Authentication and session management
            </p>

          </div>

          <div className="rounded-2xl border border-gray-800 bg-gray-900/40">

            <div className="flex items-center justify-between p-5">

              <div className="flex items-center gap-4">

                <div className="rounded-lg bg-gray-800 p-2.5">
                  <Shield
                    size={20}
                    className="text-green-400"
                  />
                </div>

                <div>

                  <p className="text-sm font-medium text-gray-200">
                    Current Session
                  </p>

                  <p className="mt-1 text-xs text-gray-500">
                    You are currently signed in.
                  </p>

                </div>

              </div>

              <button
                onClick={
                  handleLogout
                }
                className="rounded-lg border border-gray-700 px-4 py-2 text-sm text-gray-300 hover:bg-gray-800"
              >
                Logout
              </button>

            </div>

          </div>

        </section>

      </main>

    </div>
  );
}

export default Settings;