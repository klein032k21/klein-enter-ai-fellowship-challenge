import type { ExtractionMetadata } from '../types/extraction';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

export interface ExtractionRequest {
  label: string;
  extraction_schema: Record<string, string>;
  pdf: string; // base64 encoded
}

export interface SSECallbacks {
  onStatus?: (status: string) => void;
  onMetadata?: (metadata: Partial<ExtractionMetadata>) => void;
  onResult?: (data: Record<string, any>) => void;
  onComplete?: (metadata: ExtractionMetadata) => void;
  onError?: (error: Error) => void;
}

export async function fileToBase64(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => {
      const result = reader.result as string;
      // Remove data:application/pdf;base64, prefix
      const base64 = result.split(',')[1];
      resolve(base64);
    };
    reader.onerror = error => reject(error);
  });
}

export async function extractDataStream(
  request: ExtractionRequest,
  callbacks: SSECallbacks
): Promise<void> {
  try {
    const response = await fetch(`${API_BASE_URL}/extract/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    if (!response.body) {
      throw new Error('No response body');
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    // Parse SSE stream
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n\n');

      // Keep last incomplete chunk in buffer
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (!line.trim()) continue;

        try {
          const eventLines = line.split('\n');
          let eventType = 'message';
          let eventData = '';

          for (const eventLine of eventLines) {
            if (eventLine.startsWith('event:')) {
              eventType = eventLine.substring(6).trim();
            } else if (eventLine.startsWith('data:')) {
              eventData = eventLine.substring(5).trim();
            }
          }

          if (!eventData) continue;

          const data = JSON.parse(eventData);

          switch (eventType) {
            case 'status':
              if (callbacks.onStatus) {
                callbacks.onStatus(data.message || data.status || '');
              }
              break;

            case 'metadata':
              if (callbacks.onMetadata) {
                const metadata: Partial<ExtractionMetadata> = {
                  processingTime: parseFloat(data['X-Extraction-Time-Seconds']) || 0,
                  cost: parseFloat(data['X-Extraction-Cost-USD']) || 0,
                  tokensInput: parseInt(data['X-Extraction-Tokens-Input']) || 0,
                  tokensOutput: parseInt(data['X-Extraction-Tokens-Output']) || 0,
                  cacheHit: data['X-Extraction-From-Cache'] === 'true',
                  examplesUsed: parseInt(data['X-Extraction-Used-Examples']) || 0,
                };
                callbacks.onMetadata(metadata);
              }
              break;

            case 'result':
              if (callbacks.onResult) {
                callbacks.onResult(data.extracted_data || data);
              }
              break;

            case 'completed':
              if (callbacks.onComplete) {
                const finalMetadata: ExtractionMetadata = {
                  processingTime: parseFloat(data.metadata?.['X-Extraction-Time-Seconds']) || 0,
                  cost: parseFloat(data.metadata?.['X-Extraction-Cost-USD']) || 0,
                  tokensInput: parseInt(data.metadata?.['X-Extraction-Tokens-Input']) || 0,
                  tokensOutput: parseInt(data.metadata?.['X-Extraction-Tokens-Output']) || 0,
                  cacheHit: data.metadata?.['X-Extraction-From-Cache'] === 'true',
                  examplesUsed: parseInt(data.metadata?.['X-Extraction-Used-Examples']) || 0,
                };

                if (callbacks.onResult && data.extracted_data) {
                  callbacks.onResult(data.extracted_data);
                }

                callbacks.onComplete(finalMetadata);
              }
              break;

            case 'error':
              if (callbacks.onError) {
                callbacks.onError(new Error(data.message || data.error || 'Unknown error'));
              }
              break;
          }
        } catch (parseError) {
          console.error('Error parsing SSE event:', parseError, line);
        }
      }
    }
  } catch (error) {
    if (callbacks.onError) {
      callbacks.onError(error as Error);
    } else {
      throw error;
    }
  }
}

// Fallback: Non-streaming extraction (if SSE doesn't work)
export async function extractData(request: ExtractionRequest): Promise<{
  extracted_data: Record<string, any>;
  metadata: ExtractionMetadata;
}> {
  const response = await fetch(`${API_BASE_URL}/extract`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const data = await response.json();

  // Parse metadata from headers
  const metadata: ExtractionMetadata = {
    processingTime: parseFloat(response.headers.get('X-Extraction-Time-Seconds') || '0'),
    cost: parseFloat(response.headers.get('X-Extraction-Cost-USD') || '0'),
    tokensInput: parseInt(response.headers.get('X-Extraction-Tokens-Input') || '0'),
    tokensOutput: parseInt(response.headers.get('X-Extraction-Tokens-Output') || '0'),
    cacheHit: response.headers.get('X-Extraction-From-Cache') === 'true',
    examplesUsed: parseInt(response.headers.get('X-Extraction-Used-Examples') || '0'),
  };

  return {
    extracted_data: data.extracted_data,
    metadata,
  };
}
