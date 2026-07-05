import React, { useState, useRef } from 'react'
import { UploadCloud, FileText, CheckCircle2, XCircle } from 'lucide-react'


const UploadPanel = ({ onUploaded }) => {
  const [isDragging, setIsDragging] = useState(false)
  const [status, setStatus] = useState('idle') 
  const [fileName, setFileName] = useState(null)
  const inputRef = useRef(null)

  const handleFile = async (file) => {
    if (!file) return
    setFileName(file.name)
    setStatus('uploading')
    try {
      const data = await uploadDocument(file)
      setStatus('done')
      onUploaded?.(data.doc_id, file.name)
    } catch (err) {
      console.error(err)
      setStatus('error')
    }
  }

  const onDrop = (e) => {
    e.preventDefault()
    setIsDragging(false)
    const file = e.dataTransfer.files?.[0]
    handleFile(file)
  }

  return (
    <div className="max-w-xl mx-auto mt-30">
      <div
        onDragOver={(e) => {
          e.preventDefault()
          setIsDragging(true)
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={onDrop}
        onClick={() => inputRef.current?.click()}
        className={`cursor-pointer rounded-2xl border-2 border-dashed px-8 py-14 text-center transition-all ${
          isDragging
            ? 'border-accent bg-accentSoft'
            : 'border-line bg-white hover:border-gray-300'
        }`}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".pdf,.doc,.docx,.txt"
          className="hidden"
          onChange={(e) => handleFile(e.target.files?.[0])}
        />

        <div className="flex justify-center mb-3">
          <div className="h-11 w-11 rounded-xl bg-accentSoft flex items-center justify-center">
            <UploadCloud size={20} className="text-accent" />
          </div>
        </div>

        <p className="text-sm font-medium text-ink">
          Drop a document here, or click to browse
        </p>
        <p className="text-xs text-muted mt-1">PDF, DOCX, or TXT</p>
      </div>

      {fileName && (
        <div className="mt-4 flex items-center justify-between rounded-xl border border-line px-4 py-3">
          <div className="flex items-center gap-3 min-w-0">
            <div className="h-8 w-8 rounded-lg bg-gray-50 flex items-center justify-center shrink-0">
              <FileText size={15} className="text-muted" />
            </div>
            <span className="text-sm text-ink truncate">{fileName}</span>
          </div>

          <div className="flex items-center gap-1.5 shrink-0">
            {status === 'uploading' && (
              <span className="text-xs font-medium text-muted">Uploading…</span>
            )}
            {status === 'done' && (
              <>
                <CheckCircle2 size={15} className="text-green-600" />
                <span className="text-xs font-medium text-green-600">Ready</span>
              </>
            )}
            {status === 'error' && (
              <>
                <XCircle size={15} className="text-red-600" />
                <span className="text-xs font-medium text-red-600">Upload failed</span>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default UploadPanel