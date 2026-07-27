import { CommonModule } from '@angular/common';
import { Component, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { InvoiceCreatePayload, ProcurementService } from '../../core/services/procurement.service';

@Component({ selector: 'app-invoice-form', standalone: true, imports: [CommonModule, ReactiveFormsModule, RouterLink], templateUrl: './invoice-form.component.html', styleUrl: './invoice-form.component.css' })
export class InvoiceFormComponent {
  private readonly fb = inject(FormBuilder); private readonly route = inject(ActivatedRoute); private readonly router = inject(Router); private readonly procurementService = inject(ProcurementService);
  readonly saving = signal(false); readonly errorMessage = signal('');
  readonly form = this.fb.nonNullable.group({ purchaseOrderId: ['', [Validators.required, Validators.min(1)]], invoiceNumber: ['', [Validators.required, Validators.minLength(2), Validators.maxLength(255)]], invoiceAmount: [0, [Validators.required, Validators.min(0)]], taxAmount: [0, [Validators.required, Validators.min(0)]], supportingInvoiceDocument: [''], invoiceDate: ['', [Validators.required]], dueDate: [''] });
  ngOnInit(): void { const poId = Number(this.route.snapshot.queryParamMap.get('purchaseOrderId')); if (Number.isInteger(poId) && poId > 0) this.form.patchValue({ purchaseOrderId: String(poId) }); }
  submit(): void { if (this.form.invalid) { this.form.markAllAsTouched(); return; } const value = this.form.getRawValue(); const payload: InvoiceCreatePayload = { purchaseOrderId: Number(value.purchaseOrderId), invoiceNumber: value.invoiceNumber.trim(), invoiceAmount: Number(value.invoiceAmount), taxAmount: Number(value.taxAmount), supportingInvoiceDocument: value.supportingInvoiceDocument.trim() || null, invoiceDate: `${value.invoiceDate}T00:00:00`, dueDate: value.dueDate ? `${value.dueDate}T00:00:00` : null }; this.saving.set(true); this.errorMessage.set(''); this.procurementService.createInvoice(payload).subscribe({ next: (invoice) => this.router.navigate(['/procurement/invoices', invoice.id], { state: { successMessage: 'Invoice created successfully.' } }), error: (error: unknown) => { this.errorMessage.set(this.readError(error)); this.saving.set(false); } }); }
  hasError(name: string, error: string): boolean { const control = this.form.get(name); return !!control && control.touched && control.hasError(error); }
  private readError(error: unknown): string { const detail = typeof error === 'object' && error !== null && 'error' in error ? (error as { error?: { detail?: unknown } }).error?.detail : null; return typeof detail === 'string' ? detail : 'Unable to create the invoice. Please try again.'; }
}
