import { CommonModule } from '@angular/common';
import { Component, inject, signal } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';
import { ProcurementRequest, ProcurementService } from '../../core/services/procurement.service';
import { DocumentPanelComponent } from '../../shared/document-panel.component';

@Component({
  selector: 'app-request-detail',
  standalone: true,
  imports: [CommonModule, RouterLink, DocumentPanelComponent],
  templateUrl: './request-detail.component.html',
  styleUrl: './request-detail.component.css'
})
export class RequestDetailComponent {
  private readonly route = inject(ActivatedRoute);
  private readonly procurementService = inject(ProcurementService);
  private readonly authService = inject(AuthService);
  readonly request = signal<ProcurementRequest | null>(null);
  readonly loading = signal(true);
  readonly errorMessage = signal('');
  readonly successMessage = signal('');

  ngOnInit(): void {
    const success = history.state?.successMessage;
    if (typeof success === 'string') this.successMessage.set(success);
    const requestId = Number(this.route.snapshot.paramMap.get('id'));
    if (!Number.isInteger(requestId) || requestId <= 0) {
      this.errorMessage.set('Invalid procurement request id.');
      this.loading.set(false);
      return;
    }
    this.loadRequest(requestId);
  }

  statusClass(status: string | null): string { return `status-${(status ?? 'unknown').toLowerCase().replace(/\s+/g, '-')}`; }

  get canManageWorkflow(): boolean {
    return ['Administrator', 'Procurement Manager'].includes(this.authService.getStoredUser()?.role ?? '');
  }

  retry(): void {
    const requestId = Number(this.route.snapshot.paramMap.get('id'));
    if (Number.isInteger(requestId) && requestId > 0) {
      this.loadRequest(requestId);
    }
  }

  private loadRequest(requestId: number): void {
    this.loading.set(true);
    this.errorMessage.set('');
    this.procurementService.getRequest(requestId).subscribe({
      next: (request) => { this.request.set(request); this.loading.set(false); },
      error: (error: unknown) => { this.errorMessage.set(this.readError(error)); this.loading.set(false); }
    });
  }

  private readError(error: unknown): string {
    if (typeof error === 'object' && error !== null && 'error' in error) {
      const response = (error as { error?: { detail?: unknown } }).error;
      if (typeof response?.detail === 'string') return response.detail;
    }
    return 'Unable to load this procurement request.';
  }
}
