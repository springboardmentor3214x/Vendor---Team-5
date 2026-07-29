import { CommonModule } from '@angular/common';
import { Component, computed, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { forkJoin } from 'rxjs';
import { AuthService } from '../../core/services/auth.service';
import { ProcurementRequest, ProcurementService, PurchaseOrder } from '../../core/services/procurement.service';

@Component({
  selector: 'app-procurement',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './procurement.component.html',
  styleUrl: './procurement.component.css'
})
export class ProcurementComponent {
  private readonly procurementService = inject(ProcurementService);
  private readonly authService = inject(AuthService);

  readonly requests = signal<ProcurementRequest[]>([]);
  readonly purchaseOrders = signal<PurchaseOrder[]>([]);
  readonly loading = signal(true);
  readonly errorMessage = signal('');

  readonly summaryCards = computed(() => {
    const requests = this.requests();
    const orders = this.purchaseOrders();

    return [
      { label: 'Procurement requests', value: requests.length, tone: 'blue' },
      { label: 'Pending approval', value: requests.filter((request) => request.approval_status === 'Pending').length, tone: 'amber' },
      { label: 'Approved requests', value: requests.filter((request) => request.approval_status === 'Approved').length, tone: 'green' },
      { label: 'Purchase orders', value: orders.length, tone: 'violet' },
      { label: 'Open deliveries', value: orders.filter((order) => ['Issued', 'In Progress'].includes(order.po_status ?? '')).length, tone: 'teal' },
      { label: 'Completed orders', value: orders.filter((order) => order.po_status === 'Completed').length, tone: 'slate' }
    ];
  });

  readonly recentRequests = computed(() => this.requests().slice(0, 5));

  get currentRole(): string {
    return this.authService.getStoredUser()?.role ?? 'User';
  }

  get canOpenVendors(): boolean {
    return ['Administrator', 'Procurement Manager', 'Supply Chain Manager'].includes(this.currentRole);
  }

  ngOnInit(): void {
    this.loadDashboard();
  }

  loadDashboard(): void {
    this.loading.set(true);
    this.errorMessage.set('');

    forkJoin({
      requests: this.procurementService.listRequests(),
      purchaseOrders: this.procurementService.listPurchaseOrders()
    }).subscribe({
      next: ({ requests, purchaseOrders }) => {
        this.requests.set(requests);
        this.purchaseOrders.set(purchaseOrders);
        this.loading.set(false);
      },
      error: (error: unknown) => {
        this.errorMessage.set(this.readError(error));
        this.loading.set(false);
      }
    });
  }

  statusClass(status: string | null): string {
    return `status-${(status ?? 'unknown').toLowerCase().replace(/\s+/g, '-')}`;
  }

  private readError(error: unknown): string {
    if (typeof error === 'object' && error !== null && 'error' in error) {
      const response = (error as { error?: { detail?: unknown } }).error;
      if (typeof response?.detail === 'string') return response.detail;
    }
    return 'Unable to load procurement data. Please try again.';
  }
}
