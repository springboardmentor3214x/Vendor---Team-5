import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface VendorIssue { issue_id?: number; id?: number; purchase_order_id?: number | null; category: string; severity: string; status: string; description?: string; reported_date?: string; resolved_date?: string | null; resolution_notes?: string | null; }

@Injectable({ providedIn: 'root' })
export class IssueTrackingService {
  private readonly http = inject(HttpClient);
  private readonly base = `${environment.apiUrl}/performance/vendors`;
  list(vendorId: number): Observable<VendorIssue[]> { return this.http.get<VendorIssue[]>(`${this.base}/${vendorId}/issues`); }
  create(vendorId: number, issue: Pick<VendorIssue, 'category' | 'severity' | 'description' | 'purchase_order_id'>): Observable<VendorIssue> { return this.http.post<VendorIssue>(`${this.base}/${vendorId}/issues`, issue); }
  resolve(vendorId: number, issueId: number, resolutionNotes: string): Observable<VendorIssue> { return this.http.patch<VendorIssue>(`${this.base}/${vendorId}/issues/${issueId}`, { status: 'Resolved', resolutionNotes }); }
}
