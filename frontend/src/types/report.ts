export interface KeyStat {
  label: string;
  value: string;
  context: string;
}

export interface ReportPreview {
  overview: string;
  key_statistics: KeyStat[];
}

export interface ReportState {
  loading: boolean;
  error: string | null;
  preview: ReportPreview | null;
  pdfBlob: Blob | null;
}
