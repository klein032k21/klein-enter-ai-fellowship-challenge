export interface SchemaField {
  id: string;
  name: string;
  description: string;
}

export interface UploadedFile {
  id: string;
  name: string;
  size: number;
  progress: number;
  status: 'uploading' | 'uploaded' | 'error';
}

export interface ExtractionMetadata {
  processingTime: number;
  cost: number;
  tokensInput: number;
  tokensOutput: number;
  cacheHit: boolean;
  examplesUsed: number;
}
