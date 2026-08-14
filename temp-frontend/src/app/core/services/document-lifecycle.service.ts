import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

export type DocumentOwner = 'request' | 'invoice' | 'contract';
export interface LifecycleDocument { id: number; document_type: string; file_name: string; file_size?: number | null; content_type?: string | null; uploaded_at?: string | null; version: number; is_current: boolean; }

@Injectable({ providedIn: 'root' })
export class DocumentLifecycleService {
  private readonly http = inject(HttpClient);
  private readonly api = environment.apiUrl;

  list(owner: DocumentOwner, id: number): Observable<LifecycleDocument[]> { return this.http.get<LifecycleDocument[]>(this.url(owner, id)); }
  upload(owner: DocumentOwner, id: number, type: string, file: File): Observable<LifecycleDocument> {
    const form = new FormData(); form.append('document_type', type); form.append('file', file);
    return this.http.post<LifecycleDocument>(this.url(owner, id), form);
  }
  replace(owner: DocumentOwner, id: number, documentId: number, type: string, file: File): Observable<LifecycleDocument> {
    const form = new FormData(); form.append('document_type', type); form.append('file', file);
    return this.http.post<LifecycleDocument>(`${this.url(owner, id)}/${documentId}/replace`, form);
  }
  download(owner: DocumentOwner, id: number, documentId: number): Observable<Blob> { return this.http.get(`${this.url(owner, id)}/${documentId}/download`, { responseType: 'blob' }); }
  private url(owner: DocumentOwner, id: number): string {
    if (owner === 'contract') return `${this.api}/contracts/${id}/documents`;
    return `${this.api}/procurement/${owner === 'request' ? 'procurement-requests' : 'invoices'}/${id}/documents`;
  }
}
