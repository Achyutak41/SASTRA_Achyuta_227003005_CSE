import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { UserPlus } from "lucide-react";

import useAuth from "../hooks/useAuth";

function Register() {
  const navigate = useNavigate();

  const { register } = useAuth();

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();

    setError("");
    setSubmitting(true);

    try {
      await register(
        name,
        email,
        password
      );

      navigate("/chat", {
        replace: true
      });
    } catch (err) {
      setError(
        err.message || "Unable to create account."
      );
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-950 px-4">

      <div className="w-full max-w-md rounded-2xl border border-gray-800 bg-gray-900 p-8 shadow-2xl">

        <div className="mb-8 text-center">

          <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-orange-500">
            <UserPlus className="h-6 w-6 text-white" />
          </div>

          <h1 className="text-3xl font-bold text-white">
            Create Account
          </h1>

          <p className="mt-2 text-sm text-gray-400">
            Start using AUTOSAR AI Assistant
          </p>

        </div>

        {error && (
          <div className="mb-5 rounded-lg border border-red-800 bg-red-950/40 px-4 py-3 text-sm text-red-300">
            {error}
          </div>
        )}

        <form
          onSubmit={handleSubmit}
          className="space-y-5"
        >

          <div>

            <label className="mb-2 block text-sm text-gray-300">
              Name
            </label>

            <input
              type="text"
              required
              value={name}
              onChange={(event) =>
                setName(event.target.value)
              }
              placeholder="Your name"
              className="w-full rounded-lg border border-gray-700 bg-gray-800 px-4 py-3 text-white outline-none placeholder:text-gray-500 focus:border-orange-500"
            />

          </div>

          <div>

            <label className="mb-2 block text-sm text-gray-300">
              Email
            </label>

            <input
              type="email"
              required
              value={email}
              onChange={(event) =>
                setEmail(event.target.value)
              }
              placeholder="you@example.com"
              className="w-full rounded-lg border border-gray-700 bg-gray-800 px-4 py-3 text-white outline-none placeholder:text-gray-500 focus:border-orange-500"
            />

          </div>

          <div>

            <label className="mb-2 block text-sm text-gray-300">
              Password
            </label>

            <input
              type="password"
              required
              value={password}
              onChange={(event) =>
                setPassword(event.target.value)
              }
              placeholder="Create a password"
              className="w-full rounded-lg border border-gray-700 bg-gray-800 px-4 py-3 text-white outline-none placeholder:text-gray-500 focus:border-orange-500"
            />

          </div>

          <button
            type="submit"
            disabled={submitting}
            className="w-full rounded-lg bg-orange-500 py-3 font-semibold text-white transition hover:bg-orange-600 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {submitting
              ? "Creating account..."
              : "Create Account"}
          </button>

        </form>

        <p className="mt-6 text-center text-sm text-gray-400">

          Already have an account?{" "}

          <Link
            to="/login"
            className="font-medium text-orange-400 hover:text-orange-300"
          >
            Sign in
          </Link>

        </p>

      </div>

    </div>
  );
}

export default Register;