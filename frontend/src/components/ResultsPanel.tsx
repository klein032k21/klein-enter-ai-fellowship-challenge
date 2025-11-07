import { ImageWithFallback } from './figma/ImageWithFallback';
import type { ExtractionMetadata } from '../types/extraction';

interface ResultsPanelProps {
  extractedData: Record<string, any>;
  metadata: ExtractionMetadata;
  onReset: () => void;
}

export function ResultsPanel({ extractedData, metadata, onReset }: ResultsPanelProps) {
  return (
    <section className="w-full py-12 px-6">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Extracted Data Card */}
        <div className="bg-[#0a0a0a] rounded-2xl p-8 border border-white/5">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-white text-2xl font-bold">Dados Extraídos</h2>
            <button
              onClick={onReset}
              className="text-[#ffae35] hover:text-[#ffae35]/80 text-sm px-4 py-2 rounded-lg border border-[#ffae35]/30 hover:border-[#ffae35] transition-all"
            >
              Nova Extração
            </button>
          </div>

          <div className="bg-black/50 rounded-xl p-6 border border-white/5">
            <pre className="text-white font-mono text-sm overflow-x-auto whitespace-pre-wrap">
              {JSON.stringify(extractedData, null, 2)}
            </pre>
          </div>
        </div>

        {/* Metadata Card */}
        <div className="bg-[#0a0a0a] rounded-2xl p-8 border border-white/5">
          <h3 className="text-white text-xl font-bold mb-6">Detalhes da Extração</h3>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Processing Time */}
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-lg overflow-hidden flex-shrink-0">
                <ImageWithFallback
                  src="https://images.unsplash.com/photo-1668822434552-13a5ba2aa3e1?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxjbG9jayUyMHRpbWVyfGVufDF8fHx8MTc2MjUwMTgwNHww&ixlib=rb-4.1.0&q=80&w=1080"
                  alt="Clock"
                  className="w-full h-full object-cover"
                />
              </div>
              <div>
                <p className="text-white/50 text-sm">Tempo</p>
                <p className="text-white font-semibold">{metadata.processingTime.toFixed(2)}s</p>
              </div>
            </div>

            {/* Cost */}
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-lg overflow-hidden flex-shrink-0">
                <ImageWithFallback
                  src="https://images.unsplash.com/photo-1682929487361-1c7df090e021?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxtb25leSUyMGRvbGxhciUyMGNvaW5zfGVufDF8fHx8MTc2MjUwMTgwNXww&ixlib=rb-4.1.0&q=80&w=1080"
                  alt="Cost"
                  className="w-full h-full object-cover"
                />
              </div>
              <div>
                <p className="text-white/50 text-sm">Custo</p>
                <p className="text-white font-semibold">${metadata.cost.toFixed(4)}</p>
              </div>
            </div>

            {/* Tokens */}
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-lg overflow-hidden flex-shrink-0">
                <ImageWithFallback
                  src="https://images.unsplash.com/photo-1760539165416-62fd69fcf02d?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxjb21wdXRlciUyMHByb2Nlc3NvciUyMGNoaXB8ZW58MXx8fHwxNzYyNDgzODA2fDA&ixlib=rb-4.1.0&q=80&w=1080"
                  alt="Processor"
                  className="w-full h-full object-cover"
                />
              </div>
              <div>
                <p className="text-white/50 text-sm">Tokens</p>
                <p className="text-white text-sm font-semibold">
                  {metadata.tokensInput.toLocaleString()} entrada / {metadata.tokensOutput.toLocaleString()} saída
                </p>
              </div>
            </div>

            {/* Cache */}
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-lg overflow-hidden flex-shrink-0">
                <ImageWithFallback
                  src="https://images.unsplash.com/photo-1599678927496-7afcfda4f0ee?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxkYXRhYmFzZSUyMHN0b3JhZ2UlMjBzZXJ2ZXJ8ZW58MXx8fHwxNzYyNTAxODA1fDA&ixlib=rb-4.1.0&q=80&w=1080"
                  alt="Database"
                  className="w-full h-full object-cover"
                />
              </div>
              <div>
                <p className="text-white/50 text-sm">Cache</p>
                <p className="text-white font-semibold">
                  {metadata.cacheHit ? 'Acerto ✓' : 'Não encontrado'}
                </p>
              </div>
            </div>

            {/* Examples Used */}
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-lg overflow-hidden flex-shrink-0">
                <ImageWithFallback
                  src="https://images.unsplash.com/photo-1614849963640-9cc74b2a826f?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxib29rcyUyMGxpYnJhcnl8ZW58MXx8fHwxNzYyNDg0MDc5fDA&ixlib=rb-4.1.0&q=80&w=1080"
                  alt="Books"
                  className="w-full h-full object-cover"
                />
              </div>
              <div>
                <p className="text-white/50 text-sm">Exemplos usados</p>
                <p className="text-white font-semibold">{metadata.examplesUsed}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
