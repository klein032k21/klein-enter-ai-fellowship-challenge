import { useEffect, useState } from 'react';
import { ImageWithFallback } from './figma/ImageWithFallback';

interface LoadingPanelProps {
  elapsedTime: number;
  statusMessage?: string;
}

const STATUS_MESSAGES = [
  'Processando PDF...',
  'Extraindo texto...',
  'Buscando padrões similares...',
  'Consultando modelo de IA...',
];

export function LoadingPanel({ elapsedTime, statusMessage }: LoadingPanelProps) {
  const [currentStatusIndex, setCurrentStatusIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentStatusIndex((prev) => (prev + 1) % STATUS_MESSAGES.length);
    }, 1500);

    return () => clearInterval(interval);
  }, []);

  const displayMessage = statusMessage || STATUS_MESSAGES[currentStatusIndex];

  return (
    <section className="w-full py-12 px-6">
      <div className="max-w-2xl mx-auto">
        <div className="bg-[#0a0a0a] rounded-2xl p-12 border border-white/5">
          {/* Spinner */}
          <div className="flex justify-center mb-8">
            <div className="w-24 h-24 rounded-full overflow-hidden animate-spin">
              <ImageWithFallback
                src="https://images.unsplash.com/photo-1723118641160-15470f0a3d2b?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxsb2FkaW5nJTIwc3Bpbm5lciUyMGNpcmNsZXxlbnwxfHx8fDE3NjI1MDE4MDZ8MA&ixlib=rb-4.1.0&q=80&w=1080"
                alt="Loading"
                className="w-full h-full object-cover"
              />
            </div>
          </div>

          {/* Status Message */}
          <div className="text-center mb-8">
            <p className="text-white text-xl animate-pulse">
              {displayMessage}
            </p>
          </div>

          {/* Timer */}
          <div className="text-center">
            <div className="inline-block bg-black/50 rounded-xl px-8 py-4 border border-[#ffae35]/30">
              <p className="text-white/70 text-sm mb-1">Tempo decorrido</p>
              <p className="text-[#ffae35] text-4xl font-bold">{elapsedTime.toFixed(2)}s</p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
