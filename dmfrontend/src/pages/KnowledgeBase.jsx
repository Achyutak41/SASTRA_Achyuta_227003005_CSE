import {
  ArrowLeft,
  CheckCircle2,
  FileText,
  Loader2,
  RefreshCw,
  Trash2,
  Upload,
  XCircle
} from "lucide-react";

import {
  useEffect,
  useRef,
  useState
} from "react";

import { useNavigate } from "react-router-dom";

import documentService from "../services/documentService";


function formatFileSize(bytes) {
  if (!bytes) {
    return "0 B";
  }

  const units = [
    "B",
    "KB",
    "MB",
    "GB"
  ];

  const index = Math.floor(
    Math.log(bytes) /
      Math.log(1024)
  );

  const value =
    bytes /
    Math.pow(
      1024,
      index
    );

  return `${value.toFixed(
    index === 0 ? 0 : 2
  )} ${units[index]}`;
}


function formatDate(dateString) {
  if (!dateString) {
    return "-";
  }

  const date =
    new Date(
      dateString.replace(
        " ",
        "T"
      ) + "Z"
    );

  if (
    Number.isNaN(
      date.getTime()
    )
  ) {
    return dateString;
  }

  return date.toLocaleString();
}


function KnowledgeBase() {
  const navigate =
    useNavigate();

  const fileInputRef =
    useRef(null);

  const [documents, setDocuments] =
    useState([]);

  const [loading, setLoading] =
    useState(true);

  const [uploading, setUploading] =
    useState(false);

  const [dragging, setDragging] =
    useState(false);

  const [error, setError] =
    useState("");

  const [success, setSuccess] =
    useState("");


  const loadDocuments =
    async () => {
      setLoading(true);
      setError("");

      try {
        const response =
          await documentService.getDocuments();

        setDocuments(
          response.documents || []
        );
      } catch (requestError) {
        setError(
          requestError.response?.data?.error ||
          requestError.message ||
          "Unable to load documents."
        );
      } finally {
        setLoading(false);
      }
    };


  useEffect(() => {
    loadDocuments();
  }, []);


  const uploadFile =
    async (file) => {
      if (!file) {
        return;
      }

      setError("");
      setSuccess("");

      if (
        file.type !==
        "application/pdf"
      ) {
        setError(
          "Only PDF files are allowed."
        );

        return;
      }

      setUploading(true);

      try {
        const response =
          await documentService.uploadDocument(
            file
          );

        const uploadedDocument =
          response.document;

        setDocuments(
          (previous) => [
            uploadedDocument,
            ...previous
          ]
        );

        setSuccess(
          `"${file.name}" uploaded and processed successfully.`
        );
      } catch (requestError) {
        setError(
          requestError.response?.data?.error ||
          requestError.message ||
          "PDF upload failed."
        );
      } finally {
        setUploading(false);
      }
    };


  const handleFileChange =
    async (event) => {
      const file =
        event.target.files?.[0];

      await uploadFile(file);

      event.target.value = "";
    };


  const handleDrop =
    async (event) => {
      event.preventDefault();

      setDragging(false);

      const file =
        event.dataTransfer.files?.[0];

      await uploadFile(file);
    };


  const handleDelete =
    async (documentId) => {
      const confirmed =
        window.confirm(
          "Are you sure you want to delete this document?"
        );

      if (!confirmed) {
        return;
      }

      setError("");
      setSuccess("");

      try {
        await documentService.deleteDocument(
          documentId
        );

        setDocuments(
          (previous) =>
            previous.filter(
              (document) =>
                document.id !==
                documentId
            )
        );

        setSuccess(
          "Document deleted successfully."
        );
      } catch (requestError) {
        setError(
          requestError.response?.data?.error ||
          requestError.message ||
          "Unable to delete document."
        );
      }
    };


  return (
    <div className="min-h-screen bg-gray-950 text-white">

      <header className="border-b border-gray-800">
        <div className="mx-auto flex max-w-6xl items-center gap-4 px-6 py-4">

          <button
            onClick={() =>
              navigate("/chat")
            }
            className="rounded-lg p-2 text-gray-400 transition hover:bg-gray-800 hover:text-white"
            aria-label="Back to chat"
          >
            <ArrowLeft size={20} />
          </button>

          <div>
            <h1 className="text-lg font-bold">
              Knowledge Base
            </h1>

            <p className="text-xs text-gray-500">
              Manage your AUTOSAR PDF documents
            </p>
          </div>

        </div>
      </header>


      <main className="mx-auto max-w-6xl px-6 py-8">

        <section>

          <div className="mb-5">
            <h2 className="text-xl font-semibold">
              Upload Documents
            </h2>

            <p className="mt-1 text-sm text-gray-500">
              Upload AUTOSAR PDF documents to build your knowledge base.
            </p>
          </div>


          <div
            onDragOver={(event) => {
              event.preventDefault();
              setDragging(true);
            }}
            onDragLeave={() =>
              setDragging(false)
            }
            onDrop={handleDrop}
            className={`rounded-2xl border-2 border-dashed p-10 text-center transition ${
              dragging
                ? "border-orange-500 bg-orange-500/10"
                : "border-gray-800 bg-gray-900/40 hover:border-gray-700"
            }`}
          >

            <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-orange-500/10">
              {uploading ? (
                <Loader2
                  size={28}
                  className="animate-spin text-orange-400"
                />
              ) : (
                <Upload
                  size={28}
                  className="text-orange-400"
                />
              )}
            </div>


            <h3 className="mt-4 text-base font-semibold text-gray-200">
              {uploading
                ? "Processing PDF..."
                : "Upload an AUTOSAR PDF"}
            </h3>


            <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-gray-500">
              Drag and drop a PDF here, or select one from your computer.
            </p>


            <button
              type="button"
              disabled={uploading}
              onClick={() =>
                fileInputRef.current?.click()
              }
              className="mt-5 inline-flex items-center gap-2 rounded-lg bg-orange-500 px-5 py-2.5 text-sm font-medium text-white transition hover:bg-orange-600 disabled:cursor-not-allowed disabled:opacity-50"
            >
              <Upload size={16} />
              {uploading
                ? "Processing..."
                : "Choose PDF"}
            </button>


            <input
              ref={fileInputRef}
              type="file"
              accept="application/pdf,.pdf"
              onChange={handleFileChange}
              className="hidden"
            />

          </div>

        </section>


        {error && (
          <div className="mt-5 flex items-start gap-3 rounded-xl border border-red-900/50 bg-red-950/20 px-4 py-3 text-sm text-red-400">
            <XCircle
              size={18}
              className="mt-0.5 shrink-0"
            />

            <span>
              {error}
            </span>
          </div>
        )}


        {success && (
          <div className="mt-5 flex items-start gap-3 rounded-xl border border-green-900/50 bg-green-950/20 px-4 py-3 text-sm text-green-400">
            <CheckCircle2
              size={18}
              className="mt-0.5 shrink-0"
            />

            <span>
              {success}
            </span>
          </div>
        )}


        <section className="mt-10">

          <div className="mb-5 flex items-center justify-between">

            <div>
              <h2 className="text-xl font-semibold">
                Your Documents
              </h2>

              <p className="mt-1 text-sm text-gray-500">
                {documents.length} document
                {documents.length !== 1
                  ? "s"
                  : ""} in your knowledge base
              </p>
            </div>


            <button
              onClick={loadDocuments}
              disabled={loading}
              className="flex items-center gap-2 rounded-lg border border-gray-800 px-3 py-2 text-sm text-gray-400 transition hover:bg-gray-900 hover:text-white disabled:opacity-50"
            >
              <RefreshCw
                size={16}
                className={
                  loading
                    ? "animate-spin"
                    : ""
                }
              />
              Refresh
            </button>

          </div>


          {loading ? (

            <div className="flex min-h-40 items-center justify-center rounded-2xl border border-gray-800 bg-gray-900/40">
              <div className="flex items-center gap-3 text-sm text-gray-500">
                <Loader2
                  size={18}
                  className="animate-spin"
                />
                Loading documents...
              </div>
            </div>

          ) : documents.length === 0 ? (

            <div className="flex min-h-52 flex-col items-center justify-center rounded-2xl border border-gray-800 bg-gray-900/40 px-6 text-center">

              <FileText
                size={32}
                className="text-gray-600"
              />

              <h3 className="mt-4 font-medium text-gray-300">
                No documents yet
              </h3>

              <p className="mt-1 text-sm text-gray-600">
                Upload your first AUTOSAR PDF to start building the knowledge base.
              </p>

            </div>

          ) : (

            <div className="grid gap-4">

              {documents.map(
                (document) => (

                  <div
                    key={document.id}
                    className="rounded-2xl border border-gray-800 bg-gray-900/40 p-5"
                  >

                    <div className="flex flex-col gap-5 sm:flex-row sm:items-center sm:justify-between">

                      <div className="flex min-w-0 items-center gap-4">

                        <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-red-500/10">
                          <FileText
                            size={22}
                            className="text-red-400"
                          />
                        </div>


                        <div className="min-w-0">

                          <h3 className="truncate text-sm font-medium text-gray-200">
                            {document.original_filename}
                          </h3>

                          <p className="mt-1 text-xs text-gray-500">
                            Uploaded{" "}
                            {formatDate(
                              document.created_at
                            )}
                          </p>

                        </div>

                      </div>


                      <div className="flex items-center gap-3">

                        <span
                          className={`rounded-full px-3 py-1 text-xs font-medium ${
                            document.status ===
                            "processed"
                              ? "bg-green-500/10 text-green-400"
                              : "bg-red-500/10 text-red-400"
                          }`}
                        >
                          {document.status ===
                          "processed"
                            ? "Processed"
                            : document.status}
                        </span>


                        <button
                          onClick={() =>
                            handleDelete(
                              document.id
                            )
                          }
                          className="rounded-lg p-2 text-gray-500 transition hover:bg-red-950/30 hover:text-red-400"
                          aria-label={`Delete ${document.original_filename}`}
                        >
                          <Trash2
                            size={17}
                          />
                        </button>

                      </div>

                    </div>


                    <div className="mt-5 grid grid-cols-2 gap-3 border-t border-gray-800 pt-4 sm:grid-cols-4">

                      <div>
                        <p className="text-xs text-gray-600">
                          Size
                        </p>

                        <p className="mt-1 text-sm text-gray-300">
                          {formatFileSize(
                            document.file_size
                          )}
                        </p>
                      </div>


                      <div>
                        <p className="text-xs text-gray-600">
                          Pages
                        </p>

                        <p className="mt-1 text-sm text-gray-300">
                          {document.page_count}
                        </p>
                      </div>


                      <div>
                        <p className="text-xs text-gray-600">
                          Extracted Text
                        </p>

                        <p className="mt-1 text-sm text-gray-300">
                          {document.extracted_text_length.toLocaleString()}{" "}
                          chars
                        </p>
                      </div>


                      <div>
                        <p className="text-xs text-gray-600">
                          Document ID
                        </p>

                        <p className="mt-1 text-sm text-gray-300">
                          #{document.id}
                        </p>
                      </div>

                    </div>

                  </div>

                )
              )}

            </div>

          )}

        </section>

      </main>

    </div>
  );
}


export default KnowledgeBase;