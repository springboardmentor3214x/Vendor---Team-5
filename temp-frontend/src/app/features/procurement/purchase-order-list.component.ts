import { CommonModule } from '@angular/common';
import { Component, computed, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';
import { PURCHASE_ORDER_STATUSES, ProcurementService, PurchaseOrder } from '../../core/services/procurement.service';

@Component({ selector: 'app-purchase-order-list', standalone: true, imports: [CommonModule, FormsModule, RouterLink], templateUrl: './purchase-order-list.component.html', styleUrl: './purchase-order-list.component.css' })
export class PurchaseOrderListComponent {
  private readonly procurementService = inject(ProcurementService);
  private readonly authService = inject(AuthService);
  readonly statuses = PURCHASE_ORDER_STATUSES;
  readonly orders = signal<PurchaseOrder[]>([]); readonly loading = signal(true); readonly errorMessage = signal('');
  readonly search = signal(''); readonly status = signal(''); readonly sort = signal('created_desc'); readonly page = signal(1); readonly pageSize = 8;
  readonly filteredOrders = computed(() => {
    const term = this.search().trim().toLowerCase();
    return [...this.orders().filter((order) => (!term || [order.po_number, String(order.procurement_request_id ?? ''), String(order.vendor_id ?? '')].some((value) => value.toLowerCase().includes(term))) && (!this.status() || order.po_status === this.status()))]
      .sort((a, b) => this.sortOrders(a, b));
  });
  readonly totalPages = computed(() => Math.max(1, Math.ceil(this.filteredOrders().length / this.pageSize)));
  readonly visibleOrders = computed(() => { const start = (Math.min(this.page(), this.totalPages()) - 1) * this.pageSize; return this.filteredOrders().slice(start, start + this.pageSize); });
  ngOnInit(): void { this.loadOrders(); }
  get canCreate(): boolean { return ['Administrator', 'Procurement Manager'].includes(this.authService.getStoredUser()?.role ?? ''); }
  loadOrders(): void { this.loading.set(true); this.errorMessage.set(''); this.procurementService.listPurchaseOrders().subscribe({ next: (orders) => { this.orders.set(orders); this.loading.set(false); }, error: (error: unknown) => { this.errorMessage.set(this.readError(error)); this.loading.set(false); } }); }
  updateFilters(): void { this.page.set(1); }
  clearFilters(): void { this.search.set(''); this.status.set(''); this.sort.set('created_desc'); this.page.set(1); }
  previousPage(): void { if (this.page() > 1) this.page.update((page) => page - 1); }
  nextPage(): void { if (this.page() < this.totalPages()) this.page.update((page) => page + 1); }
  statusClass(status: string | null): string { return `status-${(status ?? 'unknown').toLowerCase().replace(/\s+/g, '-')}`; }
  private sortOrders(a: PurchaseOrder, b: PurchaseOrder): number { switch (this.sort()) { case 'number_asc': return a.po_number.localeCompare(b.po_number); case 'cost_desc': return (b.total_cost ?? 0) - (a.total_cost ?? 0); case 'date_asc': return (a.po_date ?? '').localeCompare(b.po_date ?? ''); default: return (b.po_date ?? '').localeCompare(a.po_date ?? ''); } }
  private readError(error: unknown): string { const detail = typeof error === 'object' && error !== null && 'error' in error ? (error as { error?: { detail?: unknown } }).error?.detail : null; return typeof detail === 'string' ? detail : 'Unable to load purchase orders. Please try again.'; }
}
