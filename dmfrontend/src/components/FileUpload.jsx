import {
  FileUp,
  UploadCloud,
  X
} from "lucide-react";

import { useRef, useState } from "react";

function FileUpload({
  onUpload,
  disabled = false
}) {
  const inputRef = useRef(null);

  const [dragging, setDragging] =
    useState(false);

  const [error, setError] =
    useState("");

  const validateFile = (file) => {
    if (!file) {
      return false;
    }

    if (
      file.type !== "application/pdf" &&
      !file.name.toLowerCase().endsWith(".pdf")
    ) {
      setError("Only PDF files are supported.");
      return false;
    }

    setError("");

    return true;
  };

  const handleFile = (file) => {
    if (validateFile(file)) {
      onUpload(file);
    }
  };

  const handleInputChange = (event) => {
    const file = event.target.files?.[0];

    if (file) {
      handleFile(file);
    }

    event.target.value = "";
  };

  const handleDrop = (event) => {
    event.preventDefault();

    setDragging(false);

    const file =
      event.dataTransfer.files?.[0];

    if (file) {
      handleFile(file);
    }
  };

  return (
    <div>

      <div
        onDragOver={(event) => {
          event.preventDefault();

          if (!disabled) {
            setDragging(true);
          }
        }}
        onDragLeave={() => {
          setDragging(false);
        }}
        onDrop={handleDrop}
        className={`
          rounded-2xl border-2 border-dashed p-8 text-center transition
          ${
            dragging
              ? "border-orange-500 bg-orange-500/5"
              : "border-gray-700 bg-gray-900/50"
          }
          ${
            disabled
              ? "cursor-not-allowed opacity-50"
              : "cursor-pointer hover:border-gray-600"
          }
        `}
        onClick={() => {
          if (!disabled) {
            inputRef.current?.click();
          }
        }}
      >

        <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-xl bg-orange-500/10">
          {dragging ? (
            <UploadCloud
              size={28}
              className="text-orange-400"
            />
          ) : (
            <FileUp
              size={28}
              className="text-orange-400"
            />
          )}
        </div>

        <h3 className="font-semibold text-gray-200">
          Upload AUTOSAR PDF
        </h3>

        <p className="mt-2 text-sm text-gray-500">
          Drag and drop your PDF here, or click to browse
        </p>

        <p className="mt-2 text-xs text-gray-600">
          PDF files only
        </p>

        <input
          ref={inputRef}
          type="file"
          accept=".pdf,application/pdf"
          className="hidden"
          onChange={handleInputChange}
          disabled={disabled}
        />

      </div>

      {error && (
        <div className="mt-3 flex items-center justify-between rounded-lg border border-red-900/50 bg-red-950/30 px-3 py-2 text-sm text-red-400">
          <span>{error}</span>

          <button
            onClick={() => setError("")}
            className="rounded p-1 hover:bg-red-900/30"
          >
            <X size={15} />
          </button>
        </div>
      )}

    </div>
  );
}

export default FileUpload;