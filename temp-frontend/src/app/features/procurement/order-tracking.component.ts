import { CommonModule } from '@angular/common';
import { Component, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule } from '@angular/forms';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { forkJoin } from 'rxjs';
import { AuthService } from '../../core/services/auth.service';
import { DELIVERY_STATUSES, OrderTracking, OrderTrackingUpdatePayload, ProcurementService, PurchaseOrder } from '../../core/services/procurement.service';

@Component({ selector: 'app-order-tracking', standalone: true, imports: [CommonModule, ReactiveFormsModule, RouterLink], templateUrl: './order-tracking.component.html', styleUrl: './order-tracking.component.css' })
export class OrderTrackingComponent {
  private readonly route = inject(ActivatedRoute); private readonly fb = inject(FormBuilder); private readonly procurementService = inject(ProcurementService); private readonly authService = inject(AuthService);
  readonly deliveryStatuses = DELIVERY_STATUSES; readonly order = signal<PurchaseOrder | null>(null); readonly tracking = signal<OrderTracking | null>(null); readonly loading = signal(true); readonly saving = signal(false); readonly errorMessage = signal(''); readonly successMessage = signal('');
  readonly form = this.fb.nonNullable.group({ dispatchDate: [''], actualDeliveryDate: [''], deliveryStatus: ['Awaiting Shipment'], remarks: [''] });
  ngOnInit(): void { const poId = Number(this.route.snapshot.paramMap.get('id')); if (!Number.isInteger(poId) || poId <= 0) { this.errorMessage.set('Invalid purchase order id.'); this.loading.set(false); return; } this.load(poId); }
  get canManage(): boolean { return ['Administrator', 'Procurement Manager'].includes(this.authService.getStoredUser()?.role ?? ''); }
  get isDelayed(): boolean { const tracking = this.tracking(); if (!tracking) return false; if (tracking.delay_days > 0) return true; const expected = this.toDate(tracking.expected_delivery_date); const actual = this.toDate(tracking.actual_delivery_date); if (!expected) return false; if (actual) return actual.getTime() > expected.getTime(); return !['Delivered', 'Completed'].includes(tracking.delivery_status ?? '') && expected.getTime() < this.startOfToday().getTime(); }
  get delayMessage(): string { const tracking = this.tracking(); if (!tracking) return ''; if (tracking.delay_days > 0) return `${tracking.delay_days} day(s) delayed according to backend tracking data.`; return tracking.actual_delivery_date ? 'Actual delivery is later than the expected delivery date.' : 'Expected delivery date has passed and delivery is not complete.'; }
  save(): void { if (!this.canManage || this.saving()) return; const poId = this.order()?.id; if (!poId) return; const value = this.form.getRawValue(); const payload: OrderTrackingUpdatePayload = { dispatchDate: this.toDateTime(value.dispatchDate), actualDeliveryDate: this.toDateTime(value.actualDeliveryDate), deliveryStatus: value.deliveryStatus || null, remarks: value.remarks.trim() || null }; this.saving.set(true); this.errorMessage.set(''); this.successMessage.set(''); this.procurementService.updateOrderTracking(poId, payload).subscribe({ next: (tracking) => { this.tracking.set(tracking); this.patchForm(tracking); this.successMessage.set('Tracking information updated successfully.'); this.saving.set(false); }, error: (error: unknown) => { this.errorMessage.set(this.readError(error)); this.saving.set(false); } }); }
  statusClass(status: string | null): string { return `delivery-${(status ?? 'unknown').toLowerCase().replace(/\s+/g, '-')}`; }
  private load(poId: number): void { this.loading.set(true); this.errorMessage.set(''); forkJoin({ order: this.procurementService.getPurchaseOrder(poId), tracking: this.procurementService.getOrderTracking(poId) }).subscribe({ next: ({ order, tracking }) => { this.order.set(order); this.tracking.set(tracking); this.patchForm(tracking); this.loading.set(false); }, error: (error: unknown) => { this.errorMessage.set(this.readError(error)); this.loading.set(false); } }); }
  private patchForm(tracking: OrderTracking): void { this.form.patchValue({ dispatchDate: this.dateInputValue(tracking.dispatch_date), actualDeliveryDate: this.dateInputValue(tracking.actual_delivery_date), deliveryStatus: tracking.delivery_status || 'Awaiting Shipment', remarks: tracking.remarks || '' }); }
  private dateInputValue(value: string | null): string { return value ? value.slice(0, 10) : ''; }
  private toDateTime(value: string): string | null { return value ? `${value}T00:00:00` : null; }
  private toDate(value: string | null): Date | null { if (!value) return null; const parsed = new Date(value); return Number.isNaN(parsed.getTime()) ? null : parsed; }
  private startOfToday(): Date { const today = new Date(); today.setHours(0, 0, 0, 0); return today; }
  private readError(error: unknown): string { const detail = typeof error === 'object' && error !== null && 'error' in error ? (error as { error?: { detail?: unknown } }).error?.detail : null; return typeof detail === 'string' ? detail : 'Unable to load or update order tracking. Please try again.'; }
}
