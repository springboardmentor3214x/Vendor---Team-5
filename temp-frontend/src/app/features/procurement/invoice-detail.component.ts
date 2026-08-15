import { CommonModule } from '@angular/common';
import { Component, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule } from '@angular/forms';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';
import { Invoice, PAYMENT_STATUSES, ProcurementService } from '../../core/services/procurement.service';
import { DocumentPanelComponent } from '../../shared/document-panel.component';

type InvoiceAction = 'verify' | 'reject' | 'payment';
@Component({ selector: 'app-invoice-detail', standalone: true, imports: [CommonModule, ReactiveFormsModule, RouterLink, DocumentPanelComponent], templateUrl: './invoice-detail.component.html', styleUrl: './invoice-detail.component.css' })
export class InvoiceDetailComponent {
  private readonly route = inject(ActivatedRoute); private readonly fb = inject(FormBuilder); private readonly procurementService = inject(ProcurementService); private readonly authService = inject(AuthService);
  readonly invoice = signal<Invoice | null>(null); readonly loading = signal(true); readonly acting = signal<InvoiceAction | null>(null); readonly errorMessage = signal(''); readonly successMessage = signal(''); readonly remarksForm = this.fb.nonNullable.group({ remarks: [''] }); readonly paymentForm = this.fb.nonNullable.group({ paymentStatus: ['Approved'] });
  readonly paymentOptions = PAYMENT_STATUSES.filter((status) => status !== 'Pending' && status !== 'Verified');
  ngOnInit(): void { const success = history.state?.successMessage; if (typeof success === 'string') this.successMessage.set(success); const invoiceId = Number(this.route.snapshot.paramMap.get('id')); if (!Number.isInteger(invoiceId) || invoiceId <= 0) { this.errorMessage.set('Invalid invoice id.'); this.loading.set(false); return; } this.load(invoiceId); }
  get canManage(): boolean { return ['Administrator', 'Finance Officer'].includes(this.authService.getStoredUser()?.role ?? ''); }
  get isPending(): boolean { return this.invoice()?.payment_status === 'Pending'; }
  get canUpdatePayment(): boolean { return this.invoice()?.payment_status === 'Verified'; }
  statusClass(status: string | null): string { return `payment-${(status ?? 'unknown').toLowerCase()}`; }
  verify(): void { const invoice = this.invoice(); if (!invoice || !this.isPending || !this.canManage) return; this.runAction('verify', this.procurementService.verifyInvoice(invoice.id, this.remarksForm.getRawValue().remarks.trim() || null), 'Invoice verified successfully.'); }
  reject(): void { const invoice = this.invoice(); if (!invoice || !this.isPending || !this.canManage || !window.confirm('Reject this pending invoice?')) return; this.runAction('reject', this.procurementService.rejectInvoice(invoice.id, this.remarksForm.getRawValue().remarks.trim() || null), 'Invoice rejected successfully.'); }
  updatePayment(): void { const invoice = this.invoice(); if (!invoice || !this.canUpdatePayment || !this.canManage) return; const status = this.paymentForm.getRawValue().paymentStatus; this.runAction('payment', this.procurementService.updateInvoicePaymentStatus(invoice.id, status), `Payment status updated to ${status}.`); }
  private runAction(action: InvoiceAction, call: ReturnType<ProcurementService['getInvoice']>, message: string): void { this.acting.set(action); this.errorMessage.set(''); this.successMessage.set(''); call.subscribe({ next: (invoice) => { this.invoice.set(invoice); this.successMessage.set(message); this.acting.set(null); }, error: (error: unknown) => { this.errorMessage.set(this.readError(error)); this.acting.set(null); } }); }
  private load(invoiceId: number): void { this.procurementService.getInvoice(invoiceId).subscribe({ next: (invoice) => { this.invoice.set(invoice); this.loading.set(false); }, error: (error: unknown) => { this.errorMessage.set(this.readError(error)); this.loading.set(false); } }); }
  private readError(error: unknown): string { const detail = typeof error === 'object' && error !== null && 'error' in error ? (error as { error?: { detail?: unknown } }).error?.detail : null; return typeof detail === 'string' ? detail : 'Unable to update this invoice. Please try again.'; }
}
