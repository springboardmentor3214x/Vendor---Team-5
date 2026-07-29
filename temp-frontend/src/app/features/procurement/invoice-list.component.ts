import { CommonModule } from '@angular/common';
import { Component, computed, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';
import { Invoice, PAYMENT_STATUSES, ProcurementService } from '../../core/services/procurement.service';

@Component({ selector: 'app-invoice-list', standalone: true, imports: [CommonModule, FormsModule, RouterLink], templateUrl: './invoice-list.component.html', styleUrl: './invoice-list.component.css' })
export class InvoiceListComponent {
  private readonly procurementService = inject(ProcurementService); private readonly authService = inject(AuthService);
  readonly statuses = PAYMENT_STATUSES; readonly invoices = signal<Invoice[]>([]); readonly loading = signal(true); readonly errorMessage = signal(''); readonly search = signal(''); readonly status = signal(''); readonly sort = signal('date_desc'); readonly page = signal(1); readonly pageSize = 8;
  readonly filteredInvoices = computed(() => { const term = this.search().trim().toLowerCase(); return [...this.invoices().filter((invoice) => (!term || [invoice.invoice_number, String(invoice.purchase_order_id)].some((value) => value.toLowerCase().includes(term))) && (!this.status() || invoice.payment_status === this.status()))].sort((a, b) => this.compare(a, b)); });
  readonly totalPages = computed(() => Math.max(1, Math.ceil(this.filteredInvoices().length / this.pageSize))); readonly visibleInvoices = computed(() => { const start = (Math.min(this.page(), this.totalPages()) - 1) * this.pageSize; return this.filteredInvoices().slice(start, start + this.pageSize); });
  get canCreate(): boolean { return ['Administrator', 'Procurement Manager', 'Finance Officer'].includes(this.authService.getStoredUser()?.role ?? ''); }
  ngOnInit(): void { this.loadInvoices(); }
  loadInvoices(): void { this.loading.set(true); this.errorMessage.set(''); this.procurementService.listInvoices().subscribe({ next: (invoices) => { this.invoices.set(invoices); this.loading.set(false); }, error: (error: unknown) => { this.errorMessage.set(this.readError(error)); this.loading.set(false); } }); }
  updateFilters(): void { this.page.set(1); } clear(): void { this.search.set(''); this.status.set(''); this.sort.set('date_desc'); this.page.set(1); } previous(): void { if (this.page() > 1) this.page.update((page) => page - 1); } next(): void { if (this.page() < this.totalPages()) this.page.update((page) => page + 1); } statusClass(status: string | null): string { return `payment-${(status ?? 'unknown').toLowerCase()}`; }
  private compare(a: Invoice, b: Invoice): number { switch (this.sort()) { case 'number_asc': return a.invoice_number.localeCompare(b.invoice_number); case 'amount_desc': return b.total_amount - a.total_amount; case 'date_asc': return (a.invoice_date ?? '').localeCompare(b.invoice_date ?? ''); default: return (b.invoice_date ?? '').localeCompare(a.invoice_date ?? ''); } }
  private readError(error: unknown): string { const detail = typeof error === 'object' && error !== null && 'error' in error ? (error as { error?: { detail?: unknown } }).error?.detail : null; return typeof detail === 'string' ? detail : 'Unable to load invoices. Please try again.'; }
}
