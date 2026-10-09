import { FileText, Quote } from "lucide-react";

function SourceCard({ source }) {
  const filename =
    source.name ||
    source.filename ||
    source.original_filename ||
    "Document source";

  const page = source.page ?? source.page_number;
  const excerpt =
    source.preview ||
    source.excerpt ||
    "No excerpt was provided by the backend.";

  return (
    <div className="rounded-xl border border-gray-800 bg-gray-900 p-4">
      <div className="flex items-start gap-3">
        <div className="rounded-lg bg-gray-800 p-2">
          <FileText size={18} className="text-orange-400" />
        </div>

        <div className="min-w-0 flex-1">
          <h3 className="break-words text-sm font-medium text-gray-200">
            {filename}
          </h3>

          <div className="mt-1 flex flex-wrap gap-2 text-xs text-gray-500">
            {page != null && <span>Page {page}</span>}
            {source.chunk_id != null && (
              <span>Chunk {source.chunk_id}</span>
            )}
          </div>

          <div className="mt-3 flex items-start gap-2">
            <Quote
              size={14}
              className="mt-1 shrink-0 text-orange-400"
            />
            <p className="whitespace-pre-wrap break-words text-xs leading-5 text-gray-400">
              {excerpt}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default SourceCard;