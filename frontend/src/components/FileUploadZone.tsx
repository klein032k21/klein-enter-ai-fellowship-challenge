import { useRef } from 'react';
import { ImageWithFallback } from './figma/ImageWithFallback';
import { Progress } from './ui/progress';
import type { UploadedFile } from '../types/extraction';

interface FileUploadZoneProps {
  files: UploadedFile[];
  onFilesAdded: (files: File[]) => void;
  onFileRemove: (id: string) => void;
}

export function FileUploadZone({ files, onFilesAdded, onFileRemove }: FileUploadZoneProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();

    const droppedFiles = Array.from(e.dataTransfer.files).filter(
      file => file.type === 'application/pdf'
    );

    if (droppedFiles.length > 0) {
      onFilesAdded(droppedFiles);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const selectedFiles = Array.from(e.target.files);
      onFilesAdded(selectedFiles);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  return (
    <div>
      {/* Upload Zone */}
      <div
        onDragOver={handleDragOver}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className="border-2 border-dashed border-[#ffae35]/30 hover:border-[#ffae35] rounded-2xl p-12 text-center cursor-pointer bg-[#0a0a0a] hover:bg-[#ffae35]/5 transition-all hover:shadow-lg hover:shadow-[#ffae35]/10"
      >
        <div className="flex flex-col items-center gap-4">
          <div className="w-20 h-20 rounded-full overflow-hidden opacity-90 ring-2 ring-[#ffae35]/30">
            <ImageWithFallback
              src="https://images.unsplash.com/photo-1756764609422-928384b73c1e?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxjbG91ZCUyMHVwbG9hZCUyMGFycm93fGVufDF8fHx8MTc2MjUwMTgwN3ww&ixlib=rb-4.1.0&q=80&w=1080"
              alt="Upload"
              className="w-full h-full object-cover"
            />
          </div>
          <div>
            <p className="text-white text-lg mb-2 font-medium">
              Arraste e solte PDFs aqui ou clique para selecionar
            </p>
            <p className="text-[#ffae35]/70 text-sm">Suporta múltiplos arquivos</p>
          </div>
        </div>
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf"
          multiple
          onChange={handleFileSelect}
          className="hidden"
        />
      </div>

      {/* File List */}
      {files.length > 0 && (
        <div className="mt-6 space-y-3">
          {files.map((file) => (
            <div
              key={file.id}
              className="bg-[#0a0a0a] rounded-xl p-4 border border-[#ffae35]/20 hover:border-[#ffae35]/40 transition-all group"
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-3 flex-1">
                  {file.status === 'uploaded' && (
                    <div className="w-6 h-6 rounded overflow-hidden flex-shrink-0 ring-1 ring-[#ffae35]/50">
                      <ImageWithFallback
                        src="https://images.unsplash.com/photo-1551968688-36310764a194?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxncmVlbiUyMGNoZWNrbWFyayUyMHN1Y2Nlc3N8ZW58MXx8fHwxNzYyNTAxODA2fDA&ixlib=rb-4.1.0&q=80&w=1080"
                        alt="Success"
                        className="w-full h-full object-cover"
                      />
                    </div>
                  )}
                  <div className="flex-1 min-w-0">
                    <p className="text-white text-sm truncate font-medium">{file.name}</p>
                    <p className="text-[#ffae35]/60 text-xs">{formatFileSize(file.size)}</p>
                  </div>
                </div>
                <button
                  onClick={() => onFileRemove(file.id)}
                  className="text-white/50 hover:text-red-400 text-sm px-3 py-1 transition-all rounded hover:bg-red-400/10"
                >
                  remover
                </button>
              </div>

              {file.status === 'uploading' && (
                <div className="space-y-1">
                  <Progress value={file.progress} className="h-1.5 bg-[#ffae35]/20" />
                  <p className="text-[#ffae35]/70 text-xs font-medium">{Math.round(file.progress)}%</p>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
