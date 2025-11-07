import { useState } from 'react';
import { FileUploadZone } from './FileUploadZone';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Trash2, Plus } from 'lucide-react';
import type { SchemaField, UploadedFile } from '../types/extraction';

interface ExtractionFormProps {
  schemaFields: SchemaField[];
  documentLabel: string;
  files: UploadedFile[];
  onSchemaFieldsChange: (fields: SchemaField[]) => void;
  onDocumentLabelChange: (value: string) => void;
  onFilesAdded: (files: File[]) => void;
  onFileRemove: (id: string) => void;
  onSubmit: () => void;
  isProcessing: boolean;
}

export function ExtractionForm({
  schemaFields,
  documentLabel,
  files,
  onSchemaFieldsChange,
  onDocumentLabelChange,
  onFilesAdded,
  onFileRemove,
  onSubmit,
  isProcessing,
}: ExtractionFormProps) {
  const [fieldName, setFieldName] = useState('');
  const [fieldDescription, setFieldDescription] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit();
  };

  const handleAddField = () => {
    if (fieldName.trim()) {
      const newField: SchemaField = {
        id: Math.random().toString(36).substr(2, 9),
        name: fieldName.trim(),
        description: fieldDescription.trim(),
      };
      onSchemaFieldsChange([...schemaFields, newField]);
      setFieldName('');
      setFieldDescription('');
    }
  };

  const handleRemoveField = (id: string) => {
    onSchemaFieldsChange(schemaFields.filter((f) => f.id !== id));
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleAddField();
    }
  };

  const canSubmit = schemaFields.length > 0 && documentLabel.trim() && files.some(f => f.status === 'uploaded');

  return (
    <section className="w-full py-6 px-6">
      <div className="max-w-4xl mx-auto">
        <form onSubmit={handleSubmit} className="space-y-8">
          {/* Schema Fields Builder */}
          <div className="space-y-4">
            <Label className="text-white">
              Campos para Extrair
            </Label>

            {/* Add Field Inputs */}
            <div className="bg-[#0a0a0a] border border-[#ffae35]/20 rounded-xl p-6 space-y-4 hover:border-[#ffae35]/40 transition-all">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Input
                  value={fieldName}
                  onChange={(e) => setFieldName(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Nome do campo (ex: telefone)"
                  className="bg-black/50 border-[#ffae35]/30 focus:border-[#ffae35] text-white placeholder:text-white/40 focus:ring-2 focus:ring-[#ffae35]/20 transition-all"
                  disabled={isProcessing}
                />
                <Input
                  value={fieldDescription}
                  onChange={(e) => setFieldDescription(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Descrição ou localização no documento"
                  className="bg-black/50 border-[#ffae35]/30 focus:border-[#ffae35] text-white placeholder:text-white/40 focus:ring-2 focus:ring-[#ffae35]/20 transition-all"
                  disabled={isProcessing}
                />
              </div>

              <button
                type="button"
                onClick={handleAddField}
                disabled={!fieldName.trim() || !fieldDescription.trim() || isProcessing}
                className="w-full bg-[#ffae35]/10 hover:bg-[#ffae35]/20 border border-[#ffae35]/40 hover:border-[#ffae35] text-[#ffae35] py-3 px-4 rounded-lg transition-all flex items-center justify-center gap-2 disabled:opacity-30 disabled:cursor-not-allowed hover:shadow-lg hover:shadow-[#ffae35]/10"
              >
                <Plus className="w-4 h-4" />
                Adicionar Campo
              </button>
            </div>

            {/* Fields List */}
            {schemaFields.length > 0 && (
              <div className="space-y-2">
                {schemaFields.map((field) => (
                  <div
                    key={field.id}
                    className="bg-[#0a0a0a] border border-[#ffae35]/20 rounded-lg p-4 flex items-start justify-between gap-4 hover:border-[#ffae35]/50 hover:bg-[#ffae35]/5 transition-all group"
                  >
                    <div className="flex-1 min-w-0">
                      <div className="text-[#ffae35] font-medium mb-1">{field.name}</div>
                      {field.description && (
                        <div className="text-white/60 text-sm">{field.description}</div>
                      )}
                    </div>
                    <button
                      type="button"
                      onClick={() => handleRemoveField(field.id)}
                      disabled={isProcessing}
                      className="text-white/40 hover:text-red-400 transition-all disabled:opacity-30 disabled:cursor-not-allowed flex-shrink-0 opacity-0 group-hover:opacity-100"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Document Label */}
          <div className="space-y-3">
            <Label htmlFor="documentLabel" className="text-white text-base font-medium">
              Tipo de Documento
            </Label>
            <Input
              id="documentLabel"
              value={documentLabel}
              onChange={(e) => onDocumentLabelChange(e.target.value)}
              placeholder="ex: carteira_oab, nota_fiscal, contrato"
              className="bg-[#0a0a0a] border-[#ffae35]/30 focus:border-[#ffae35] text-white placeholder:text-white/30 focus:ring-2 focus:ring-[#ffae35]/20 transition-all"
              disabled={isProcessing}
            />
          </div>

          {/* File Upload Zone */}
          <div className="space-y-3">
            <Label className="text-white">Documentos PDF</Label>
            <FileUploadZone
              files={files}
              onFilesAdded={onFilesAdded}
              onFileRemove={onFileRemove}
            />
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={!canSubmit || isProcessing}
            className="w-full bg-[#ffae35] hover:bg-[#ffae35]/90 disabled:bg-[#ffae35]/30 disabled:cursor-not-allowed text-black font-bold py-4 px-8 rounded-xl transition-all text-lg hover:shadow-2xl hover:shadow-[#ffae35]/30 hover:scale-[1.02] active:scale-[0.98]"
          >
            {isProcessing ? 'Processando...' : 'Extrair Dados Agora'}
          </button>
        </form>
      </div>
    </section>
  );
}
