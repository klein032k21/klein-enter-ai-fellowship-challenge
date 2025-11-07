import { useState, useEffect } from 'react';
import { ChallengeBanner } from './components/ChallengeBanner';
import { HeroSection } from './components/HeroSection';
import { ExtractionForm } from './components/ExtractionForm';
import { LoadingPanel } from './components/LoadingPanel';
import { ResultsPanel } from './components/ResultsPanel';
import { Footer } from './components/Footer';
import { Toaster } from './components/ui/sonner';
import { toast } from 'sonner';
import type { SchemaField, UploadedFile, ExtractionMetadata } from './types/extraction';
import { extractDataStream, fileToBase64 } from './services/api';

type AppState = 'form' | 'processing' | 'results';

export default function App() {
  const [state, setState] = useState<AppState>('form');
  const [schemaFields, setSchemaFields] = useState<SchemaField[]>([]);
  const [documentLabel, setDocumentLabel] = useState('');
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [elapsedTime, setElapsedTime] = useState(0);
  const [extractedData, setExtractedData] = useState<Record<string, any>>({});
  const [metadata, setMetadata] = useState<ExtractionMetadata>({
    processingTime: 0,
    cost: 0,
    tokensInput: 0,
    tokensOutput: 0,
    cacheHit: false,
    examplesUsed: 0,
  });
  const [statusMessage, setStatusMessage] = useState('');

  // Timer for processing state
  useEffect(() => {
    let interval: ReturnType<typeof setInterval>;

    if (state === 'processing') {
      const startTime = Date.now();
      interval = setInterval(() => {
        setElapsedTime((Date.now() - startTime) / 1000);
      }, 10);
    } else {
      setElapsedTime(0);
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [state]);

  const handleFilesAdded = async (newFiles: File[]) => {
    const uploadedFiles: UploadedFile[] = newFiles.map((file) => ({
      id: Math.random().toString(36).substr(2, 9),
      name: file.name,
      size: file.size,
      progress: 0,
      status: 'uploading' as const,
      file,
    } as UploadedFile & { file: File }));

    setFiles((prev) => [...prev, ...uploadedFiles]);

    // Simulate upload progress
    uploadedFiles.forEach((uploadedFile) => {
      simulateUpload(uploadedFile.id);
    });
  };

  const simulateUpload = (fileId: string) => {
    let progress = 0;
    const interval = setInterval(() => {
      progress += Math.random() * 30;

      if (progress >= 100) {
        progress = 100;
        setFiles((prev) =>
          prev.map((f) =>
            f.id === fileId ? { ...f, progress: 100, status: 'uploaded' } : f
          )
        );
        clearInterval(interval);
      } else {
        setFiles((prev) =>
          prev.map((f) => (f.id === fileId ? { ...f, progress } : f))
        );
      }
    }, 200);
  };

  const handleFileRemove = (id: string) => {
    setFiles((prev) => prev.filter((f) => f.id !== id));
  };

  const handleSubmit = async () => {
    try {
      setState('processing');
      setStatusMessage('Preparando arquivos...');

      // Get first uploaded file
      const uploadedFile = files.find(f => f.status === 'uploaded');
      if (!uploadedFile || !(uploadedFile as any).file) {
        throw new Error('Nenhum arquivo foi enviado');
      }

      // Convert schema fields to object format expected by API
      const schemaObject: Record<string, string> = {};
      schemaFields.forEach(field => {
        schemaObject[field.name] = field.description;
      });

      // Convert file to base64
      setStatusMessage('Convertendo PDF...');
      const pdfBase64 = await fileToBase64((uploadedFile as any).file);

      // Call extraction API with SSE
      await extractDataStream(
        {
          label: documentLabel,
          extraction_schema: schemaObject,
          pdf: pdfBase64,
        },
        {
          onStatus: (status) => {
            setStatusMessage(status);
          },
          onMetadata: (meta) => {
            setMetadata(prev => ({ ...prev, ...meta }));
          },
          onResult: (data) => {
            setExtractedData(data);
          },
          onComplete: (finalMetadata) => {
            setMetadata(finalMetadata);
            setState('results');
            toast.success('Extração concluída com sucesso!', {
              description: `Dados extraídos em ${finalMetadata.processingTime.toFixed(2)}s`,
            });
          },
          onError: (error) => {
            console.error('Extraction error:', error);
            setState('form');
            toast.error('Erro na extração', {
              description: error.message || 'Tente novamente',
            });
          },
        }
      );
    } catch (error: any) {
      console.error('Submit error:', error);
      setState('form');
      toast.error('Erro ao processar', {
        description: error.message || 'Tente novamente',
      });
    }
  };

  const handleReset = () => {
    setState('form');
    setSchemaFields([]);
    setDocumentLabel('');
    setFiles([]);
    setExtractedData({});
    setStatusMessage('');
  };

  return (
    <div className="min-h-screen bg-black">
      <Toaster
        position="top-right"
        toastOptions={{
          style: {
            background: '#0a0a0a',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            color: '#FFFFFF',
          },
        }}
      />

      <ChallengeBanner />
      <HeroSection />

      {state === 'form' && (
        <ExtractionForm
          schemaFields={schemaFields}
          documentLabel={documentLabel}
          files={files}
          onSchemaFieldsChange={setSchemaFields}
          onDocumentLabelChange={setDocumentLabel}
          onFilesAdded={handleFilesAdded}
          onFileRemove={handleFileRemove}
          onSubmit={handleSubmit}
          isProcessing={false}
        />
      )}

      {state === 'processing' && (
        <LoadingPanel elapsedTime={elapsedTime} statusMessage={statusMessage} />
      )}

      {state === 'results' && (
        <ResultsPanel
          extractedData={extractedData}
          metadata={metadata}
          onReset={handleReset}
        />
      )}

      <Footer />
    </div>
  );
}
