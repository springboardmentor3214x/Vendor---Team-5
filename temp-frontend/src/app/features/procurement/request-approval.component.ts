import { CommonModule } from '@angular/common';
import { Component, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { forkJoin } from 'rxjs';
import { AuthService } from '../../core/services/auth.service';
import { ProcurementRequest, ProcurementService, ProcurementStatusHistoryEntry } from '../../core/services/procurement.service';

type ApprovalAction = 'approve' | 'reject' | 'send-back';

@Component({
  selector: 'app-request-approval',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterLink],
  templateUrl: './request-approval.component.html',
  styleUrl: './request-approval.component.css'
})
export class RequestApprovalComponent {
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly formBuilder = inject(FormBuilder);
  private readonly procurementService = inject(ProcurementService);
  private readonly authService = inject(AuthService);
  readonly request = signal<ProcurementRequest | null>(null);
  readonly history = signal<ProcurementStatusHistoryEntry[]>([]);
  readonly loading = signal(true);
  readonly submitting = signal<ApprovalAction | null>(null);
  readonly errorMessage = signal('');
  readonly remarksForm = this.formBuilder.nonNullable.group({ remarks: [''] });

  ngOnInit(): void {
    const requestId = Number(this.route.snapshot.paramMap.get('id'));
    if (!Number.isInteger(requestId) || requestId <= 0) { this.errorMessage.set('Invalid procurement request id.'); this.loading.set(false); return; }
    this.load(requestId);
  }

  get canAct(): boolean { return this.request()?.approval_status === 'Pending'; }
  statusClass(status: string | null): string { return `status-${(status ?? 'unknown').toLowerCase().replace(/\s+/g, '-')}`; }

  submit(action: ApprovalAction): void {
    const request = this.request();
    if (!request || !this.canAct || this.submitting()) return;
    if (action === 'reject' && !window.confirm('Reject this procurement request? This action cannot be undone from the current frontend workflow.')) return;
    this.errorMessage.set('');
    this.submitting.set(action);
    const payload = { approvedBy: this.authService.getStoredUser()?.id ?? null, remarks: this.remarksForm.getRawValue().remarks.trim() || null };
    const call = action === 'approve' ? this.procurementService.approveRequest(request.id, payload)
      : action === 'reject' ? this.procurementService.rejectRequest(request.id, payload)
      : this.procurementService.sendBackRequest(request.id, payload);
    call.subscribe({
      next: (updated) => this.router.navigate(['/procurement/requests', updated.id], { state: { successMessage: `Request ${action === 'send-back' ? 'sent back' : `${action}d`} successfully.` } }),
      error: (error: unknown) => { this.errorMessage.set(this.readError(error)); this.submitting.set(null); }
    });
  }

  private load(requestId: number): void {
    forkJoin({ request: this.procurementService.getRequest(requestId), history: this.procurementService.getRequestStatusHistory(requestId) }).subscribe({
      next: ({ request, history }) => { this.request.set(request); this.history.set(history); this.loading.set(false); },
      error: (error: unknown) => { this.errorMessage.set(this.readError(error)); this.loading.set(false); }
    });
  }

  private readError(error: unknown): string {
    if (typeof error === 'object' && error !== null && 'error' in error) {
      const detail = (error as { error?: { detail?: unknown } }).error?.detail;
      if (typeof detail === 'string') return detail;
    }
    return 'Unable to complete the approval action. Please try again.';
  }
}
