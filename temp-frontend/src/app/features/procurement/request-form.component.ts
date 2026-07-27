import { CommonModule } from '@angular/common';
import { Component, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { PROCUREMENT_PRIORITIES, ProcurementRequest, ProcurementRequestCreatePayload, ProcurementService } from '../../core/services/procurement.service';

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
  private readonly route = inject(ActivatedRoute);
  readonly priorities = PROCUREMENT_PRIORITIES;
  readonly editing = signal(false);
  readonly loading = signal(false);
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

  private requestId: number | null = null;

  ngOnInit(): void {
    const id = Number(this.route.snapshot.paramMap.get('id'));
    if (!Number.isInteger(id) || id <= 0) {
      return;
    }

    this.requestId = id;
    this.editing.set(true);
    this.loading.set(true);
    this.procurementService.getRequest(id).subscribe({
      next: (request) => {
        if (request.approval_status !== 'Sent Back') {
          this.errorMessage.set('Only sent-back requests can be edited and resubmitted.');
          this.loading.set(false);
          return;
        }
        this.patchRequest(request);
        this.loading.set(false);
      },
      error: (error: unknown) => {
        this.errorMessage.set(this.readError(error));
        this.loading.set(false);
      }
    });
  }

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
    const request = this.requestId === null
      ? this.procurementService.createRequest(payload)
      : this.procurementService.updateRequest(this.requestId, payload);
    request.subscribe({
      next: (updated) => this.router.navigate(['/procurement/requests', updated.id], { state: { successMessage: this.editing() ? 'Procurement request resubmitted for review.' : 'Procurement request submitted successfully.' } }),
      error: (error: unknown) => { this.errorMessage.set(this.readError(error)); this.submitting.set(false); }
    });
  }

  hasError(controlName: string, errorName: string): boolean {
    const control = this.form.get(controlName);
    return !!control && control.touched && control.hasError(errorName);
  }

  private patchRequest(request: ProcurementRequest): void {
    this.form.patchValue({
      requestTitle: request.request_title,
      departmentName: request.department_name,
      itemDescription: request.item_description ?? '',
      itemProductName: request.item_product_name ?? '',
      productCategory: request.product_category ?? '',
      quantityRequired: request.quantity_required ?? 1,
      unitOfMeasurement: request.unit_of_measurement ?? '',
      estimatedBudget: request.estimated_budget ?? 0,
      requiredDeliveryDate: request.required_delivery_date?.slice(0, 10) ?? '',
      priority: request.priority ?? 'Medium',
      businessJustification: request.business_justification ?? '',
      additionalRemarks: request.additional_remarks ?? '',
      requestedBy: request.requested_by?.toString() ?? ''
    });
  }

  private readError(error: unknown): string {
    if (typeof error === 'object' && error !== null && 'error' in error) {
      const response = (error as { error?: { detail?: unknown } }).error;
      if (typeof response?.detail === 'string') return response.detail;
    }
    return 'Unable to save the procurement request. Please review the form and try again.';
  }
}
