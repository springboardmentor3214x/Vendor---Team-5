import { CommonModule } from '@angular/common';
import { Component, Input, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { DocumentLifecycleService, DocumentOwner, LifecycleDocument } from '../core/services/document-lifecycle.service';

@Component({ selector: 'app-document-panel', standalone: true, imports: [CommonModule, FormsModule], template: `
<section class="document-panel"><div class="heading"><div><h3>{{ title }}</h3><p>Upload, download, and replace documents while retaining version history.</p></div><button type="button" class="btn btn-outline-primary" (click)="load()">Refresh</button></div>
<p *ngIf="error()" class="alert alert-danger">{{ error() }}</p><form (ngSubmit)="upload()"><input class="form-control" required name="type" [(ngModel)]="documentType" placeholder="Document type"><input required type="file" (change)="select($event)"><button class="btn btn-primary" [disabled]="busy()">Upload</button></form>
<div *ngIf="documents().length; else empty" class="table-wrap"><table><thead><tr><th>File</th><th>Type</th><th>Version</th><th>Uploaded</th><th></th></tr></thead><tbody><tr *ngFor="let document of documents()"><td>{{ document.file_name }}</td><td>{{ document.document_type }}</td><td>v{{ document.version }}</td><td>{{ document.uploaded_at | date:'mediumDate' }}</td><td><button type="button" class="btn btn-sm btn-outline-primary" (click)="download(document)">Download</button><label class="btn btn-sm btn-outline-secondary">Replace<input hidden type="file" (change)="replace(document, $event)"></label></td></tr></tbody></table></div><ng-template #empty><p class="muted">No current documents have been uploaded.</p></ng-template></section>`, styles: [`.document-panel{border-top:1px solid var(--vr-border);padding-top:1rem}.heading,form{display:flex;justify-content:space-between;gap:.75rem;align-items:center;flex-wrap:wrap}.heading h3{margin:0}.heading p{margin:.25rem 0;color:var(--vr-muted)}form{margin:1rem 0}.table-wrap{overflow:auto}table{width:100%;border-collapse:collapse}th,td{padding:.65rem;border-bottom:1px solid var(--vr-border);text-align:left}td:last-child{white-space:nowrap}.btn-sm{margin-right:.4rem}.muted{color:var(--vr-muted)}`] })
export class DocumentPanelComponent {
  private readonly service = inject(DocumentLifecycleService);
  @Input({ required: true }) owner!: DocumentOwner;
  @Input({ required: true }) entityId!: number;
  @Input() title = 'Documents';
  readonly documents = signal<LifecycleDocument[]>([]); readonly error = signal(''); readonly busy = signal(false);
  documentType = 'Supporting Document'; private file: File | null = null;
  ngOnChanges(): void { if (this.entityId) this.load(); }
  load(): void { if (!this.entityId) return; this.error.set(''); this.service.list(this.owner, this.entityId).subscribe({ next: docs => this.documents.set(docs), error: () => this.error.set('Document service is not available yet.') }); }
  select(event: Event): void { this.file = (event.target as HTMLInputElement).files?.[0] ?? null; }
  upload(): void { if (!this.file || !this.documentType.trim()) return; this.busy.set(true); this.service.upload(this.owner, this.entityId, this.documentType.trim(), this.file).subscribe({ next: () => { this.file = null; this.busy.set(false); this.load(); }, error: () => { this.error.set('Unable to upload document.'); this.busy.set(false); } }); }
  replace(document: LifecycleDocument, event: Event): void { const file = (event.target as HTMLInputElement).files?.[0]; if (!file) return; this.busy.set(true); this.service.replace(this.owner, this.entityId, document.id, document.document_type, file).subscribe({ next: () => { this.busy.set(false); this.load(); }, error: () => { this.error.set('Unable to replace document.'); this.busy.set(false); } }); }
  download(item: LifecycleDocument): void { this.service.download(this.owner, this.entityId, item.id).subscribe({ next: blob => { const link = window.document.createElement('a'); link.href = URL.createObjectURL(blob); link.download = item.file_name; link.click(); URL.revokeObjectURL(link.href); }, error: () => this.error.set('Unable to download document.') }); }
}
