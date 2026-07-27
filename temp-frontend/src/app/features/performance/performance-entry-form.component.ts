import { CommonModule } from '@angular/common';
import { Component, computed, inject, signal } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { ProcurementService, PurchaseOrder } from '../../core/services/procurement.service';
import {
  CommunicationPerformancePayload,
  DeliveryPerformancePayload,
  PerformanceService,
  QualityPerformancePayload,
  ServiceRatingPayload
} from '../../core/services/performance.service';

type EntryType = 'delivery' | 'quality' | 'communication' | 'service-rating';

@Component({ selector: 'app-performance-entry-form', standalone: true, imports: [CommonModule, ReactiveFormsModule, RouterLink], templateUrl: './performance-entry-form.component.html', styleUrl: './performance-entry-form.component.css' })
export class PerformanceEntryFormComponent {
  private readonly route = inject(ActivatedRoute); private readonly router = inject(Router); private readonly fb = inject(FormBuilder); private readonly performanceService = inject(PerformanceService); private readonly procurementService = inject(ProcurementService);
  readonly vendorId = signal<number | null>(null); readonly entryType = signal<EntryType | null>(null); readonly eligibleOrders = signal<PurchaseOrder[]>([]); readonly loadingOrders = signal(true); readonly submitting = signal(false); readonly errorMessage = signal('');
  readonly title = computed(() => ({ delivery: 'Record delivery performance', quality: 'Record product quality evaluation', communication: 'Record communication performance', 'service-rating': 'Submit service rating' }[this.entryType() ?? 'delivery']));
  readonly description = computed(() => ({ delivery: 'Record delivery data for delivered or completed procurement activity.', quality: 'Record an inspection for delivered or completed procurement activity.', communication: 'Record vendor response timing for delivered or completed procurement activity.', 'service-rating': 'Submit service feedback for delivered or completed procurement activity.' }[this.entryType() ?? 'delivery']));
  readonly deliveryForm = this.fb.nonNullable.group({ purchaseOrderId: ['', Validators.required], expectedDeliveryDate: ['', Validators.required], actualDeliveryDate: ['', Validators.required], remarks: [''] });
  readonly qualityForm = this.fb.nonNullable.group({ purchaseOrderId: ['', Validators.required], inspectionDate: [''], materialQuality: [0, [Validators.required, Validators.min(0), Validators.max(5)]], packagingQuality: [0, [Validators.required, Validators.min(0), Validators.max(5)]], quantityAccuracy: [0, [Validators.required, Validators.min(0), Validators.max(5)]], specificationCompliance: [0, [Validators.required, Validators.min(0), Validators.max(5)]], productDefects: [0, [Validators.required, Validators.min(0), Validators.pattern('^[0-9]+$')]], inspectorRemarks: [''] });
  readonly communicationForm = this.fb.nonNullable.group({ purchaseOrderId: ['', Validators.required], messageSentTime: ['', Validators.required], vendorResponseTime: ['', Validators.required], remarks: [''] });
  readonly serviceForm = this.fb.nonNullable.group({ purchaseOrderId: ['', Validators.required], professionalism: [0, [Validators.required, Validators.min(0), Validators.max(5)]], customerSupport: [0, [Validators.required, Validators.min(0), Validators.max(5)]], documentationQuality: [0, [Validators.required, Validators.min(0), Validators.max(5)]], flexibility: [0, [Validators.required, Validators.min(0), Validators.max(5)]], communicationEffectiveness: [0, [Validators.required, Validators.min(0), Validators.max(5)]], issueResolution: [0, [Validators.required, Validators.min(0), Validators.max(5)]], comments: [''] });

  ngOnInit(): void {
    const vendorId = Number(this.route.snapshot.paramMap.get('id')); const type = this.route.snapshot.paramMap.get('type');
    if (!Number.isInteger(vendorId) || vendorId <= 0 || !this.isEntryType(type)) { this.errorMessage.set('Invalid vendor or performance entry type.'); this.loadingOrders.set(false); return; }
    this.vendorId.set(vendorId); this.entryType.set(type); this.loadEligibleOrders(vendorId);
  }

  get hasEligibleOrders(): boolean { return this.eligibleOrders().length > 0; }
  refreshEligibleOrders(): void { const vendorId = this.vendorId(); if (vendorId) { this.errorMessage.set(''); this.loadEligibleOrders(vendorId); } }
  prefillDeliveryDates(): void {
    const purchaseOrderId = Number(this.deliveryForm.controls.purchaseOrderId.value);
    const order = this.eligibleOrders().find((item) => item.id === purchaseOrderId);
    if (!order) return;
    this.deliveryForm.patchValue({ expectedDeliveryDate: this.toDateTimeLocal(order.expected_delivery_date), actualDeliveryDate: this.toDateTimeLocal(order.actual_delivery_date) });
  }
  submit(): void {
    const vendorId = this.vendorId(); const type = this.entryType(); if (!vendorId || !type || this.submitting() || !this.hasEligibleOrders) return;
    const form = this.activeForm(); if (form.invalid) { form.markAllAsTouched(); return; }
    this.submitting.set(true); this.errorMessage.set('');
    const request = type === 'delivery' ? this.performanceService.recordDeliveryPerformance(this.deliveryPayload(vendorId))
      : type === 'quality' ? this.performanceService.recordQualityPerformance(this.qualityPayload(vendorId))
      : type === 'communication' ? this.performanceService.recordCommunicationPerformance(this.communicationPayload(vendorId))
      : this.performanceService.recordServiceRating(this.servicePayload(vendorId));
    request.subscribe({ next: () => this.router.navigate(['/performance/vendors', vendorId], { state: { successMessage: 'Performance record submitted successfully.' } }), error: (error: unknown) => { this.errorMessage.set(this.readError(error)); this.submitting.set(false); } });
  }
  hasError(control: string, error: string): boolean { const item = this.activeForm().get(control); return !!item && item.touched && item.hasError(error); }
  private loadEligibleOrders(vendorId: number): void { this.loadingOrders.set(true); this.procurementService.listPurchaseOrders({ vendor_id: vendorId }).subscribe({ next: (orders) => { this.eligibleOrders.set(orders.filter((order) => ['Delivered', 'Completed'].includes(order.po_status ?? ''))); this.loadingOrders.set(false); }, error: (error: unknown) => { this.errorMessage.set(this.readError(error)); this.loadingOrders.set(false); } }); }
  private activeForm(): FormGroup { const type = this.entryType(); return type === 'delivery' ? this.deliveryForm : type === 'quality' ? this.qualityForm : type === 'communication' ? this.communicationForm : this.serviceForm; }
  private deliveryPayload(vendorId: number): DeliveryPerformancePayload { const value = this.deliveryForm.getRawValue(); return { vendorId, purchaseOrderId: Number(value.purchaseOrderId), expectedDeliveryDate: this.toIso(value.expectedDeliveryDate)!, actualDeliveryDate: this.toIso(value.actualDeliveryDate)!, remarks: value.remarks.trim() || null }; }
  private qualityPayload(vendorId: number): QualityPerformancePayload { const value = this.qualityForm.getRawValue(); return { vendorId, purchaseOrderId: Number(value.purchaseOrderId), inspectionDate: this.toIso(value.inspectionDate), materialQuality: Number(value.materialQuality), packagingQuality: Number(value.packagingQuality), quantityAccuracy: Number(value.quantityAccuracy), specificationCompliance: Number(value.specificationCompliance), productDefects: Number(value.productDefects), inspectorRemarks: value.inspectorRemarks.trim() || null }; }
  private communicationPayload(vendorId: number): CommunicationPerformancePayload { const value = this.communicationForm.getRawValue(); return { vendorId, purchaseOrderId: Number(value.purchaseOrderId), messageSentTime: this.toIso(value.messageSentTime)!, vendorResponseTime: this.toIso(value.vendorResponseTime)!, remarks: value.remarks.trim() || null }; }
  private servicePayload(vendorId: number): ServiceRatingPayload { const value = this.serviceForm.getRawValue(); return { vendorId, purchaseOrderId: Number(value.purchaseOrderId), professionalism: Number(value.professionalism), customerSupport: Number(value.customerSupport), documentationQuality: Number(value.documentationQuality), flexibility: Number(value.flexibility), communicationEffectiveness: Number(value.communicationEffectiveness), issueResolution: Number(value.issueResolution), comments: value.comments.trim() || null }; }
  private toIso(value: string): string | null { return value ? new Date(value).toISOString() : null; }
  private toDateTimeLocal(value: string | null): string { return value ? value.slice(0, 16) : ''; }
  private isEntryType(value: string | null): value is EntryType { return value === 'delivery' || value === 'quality' || value === 'communication' || value === 'service-rating'; }
  private readError(error: unknown): string { const detail = typeof error === 'object' && error !== null && 'error' in error ? (error as { error?: { detail?: unknown } }).error?.detail : null; return typeof detail === 'string' ? detail : 'Unable to load eligible delivered or completed purchase orders, or submit this performance record.'; }
}
