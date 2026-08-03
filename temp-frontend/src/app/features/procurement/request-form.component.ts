import { CommonModule } from '@angular/common';
import { Component, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { PROCUREMENT_PRIORITIES, ProcurementRequestCreatePayload, ProcurementService } from '../../core/services/procurement.service';

@Component({
  selector: 'app-request-form',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterLink],
  templateUrl: './request-form.component.html',
  styleUrl: './request-form.component.css'
})
export class RequestFormComponent {
  private readonly fb = inject(FormBuilder);
  private readonly procurementService = inject(ProcurementService);
  private readonly router = inject(Router);
  readonly priorities = PROCUREMENT_PRIORITIES;
  readonly submitting = signal(false);
  readonly errorMessage = signal('');
  readonly form = this.fb.nonNullable.group({
    requestTitle: ['', [Validators.required, Validators.minLength(3), Validators.maxLength(255)]],
    departmentName: ['', [Validators.required]],
    itemDescription: ['', [Validators.required, Validators.minLength(3), Validators.maxLength(500)]],
    itemProductName: ['', [Validators.required, Validators.minLength(2), Validators.maxLength(255)]],
    productCategory: ['', [Validators.required]],
    quantityRequired: [1, [Validators.required, Validators.min(1)]],
    unitOfMeasurement: [''],
    estimatedBudget: [0, [Validators.required, Validators.min(0)]],
    requiredDeliveryDate: ['', [Validators.required]],
    priority: ['Medium', [Validators.required]],
    businessJustification: ['', [Validators.required, Validators.minLength(3), Validators.maxLength(1000)]],
    additionalRemarks: [''],
    requestedBy: ['']
  });

  submit(): void {
    this.errorMessage.set('');
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    const value = this.form.getRawValue();
    const payload: ProcurementRequestCreatePayload = {
      ...value,
      quantityRequired: Number(value.quantityRequired),
      estimatedBudget: Number(value.estimatedBudget),
      unitOfMeasurement: value.unitOfMeasurement || null,
      additionalRemarks: value.additionalRemarks || null,
      requestedBy: value.requestedBy === '' ? null : Number(value.requestedBy)
    };

    this.submitting.set(true);
    this.procurementService.createRequest(payload).subscribe({
      next: (request) => this.router.navigate(['/procurement/requests', request.id], { state: { successMessage: 'Procurement request submitted successfully.' } }),
      error: (error: unknown) => { this.errorMessage.set(this.readError(error)); this.submitting.set(false); }
    });
  }

  hasError(controlName: string, errorName: string): boolean {
    const control = this.form.get(controlName);
    return !!control && control.touched && control.hasError(errorName);
  }

  private readError(error: unknown): string {
    if (typeof error === 'object' && error !== null && 'error' in error) {
      const response = (error as { error?: { detail?: unknown } }).error;
      if (typeof response?.detail === 'string') return response.detail;
    }
    return 'Unable to submit the procurement request. Please review the form and try again.';
  }
}
