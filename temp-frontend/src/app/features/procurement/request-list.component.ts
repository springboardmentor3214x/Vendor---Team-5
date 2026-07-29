import { CommonModule } from '@angular/common';
import { Component, computed, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { PROCUREMENT_APPROVAL_STATUSES, PROCUREMENT_PRIORITIES, ProcurementRequest, ProcurementService } from '../../core/services/procurement.service';

@Component({
  selector: 'app-request-list',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './request-list.component.html',
  styleUrl: './request-list.component.css'
})
export class RequestListComponent {
  private readonly procurementService = inject(ProcurementService);
  readonly priorities = PROCUREMENT_PRIORITIES;
  readonly statuses = PROCUREMENT_APPROVAL_STATUSES;
  readonly requests = signal<ProcurementRequest[]>([]);
  readonly loading = signal(true);
  readonly errorMessage = signal('');
  readonly search = signal('');
  readonly department = signal('');
  readonly status = signal('');
  readonly priority = signal('');
  readonly sort = signal('created_desc');
  readonly page = signal(1);
  readonly pageSize = 8;

  readonly departments = computed(() => [...new Set(this.requests().map((request) => request.department_name).filter(Boolean))].sort());
  readonly filteredRequests = computed(() => {
    const term = this.search().trim().toLowerCase();
    const filtered = this.requests().filter((request) => {
      const matchesSearch = !term || [request.request_number, request.request_title, request.department_name]
        .some((value) => value.toLowerCase().includes(term));
      return matchesSearch
        && (!this.department() || request.department_name === this.department())
        && (!this.status() || request.approval_status === this.status())
        && (!this.priority() || request.priority === this.priority());
    });

    return [...filtered].sort((a, b) => this.compareRequests(a, b));
  });
  readonly totalPages = computed(() => Math.max(1, Math.ceil(this.filteredRequests().length / this.pageSize)));
  readonly visibleRequests = computed(() => {
    const safePage = Math.min(this.page(), this.totalPages());
    const start = (safePage - 1) * this.pageSize;
    return this.filteredRequests().slice(start, start + this.pageSize);
  });

  ngOnInit(): void { this.loadRequests(); }

  loadRequests(): void {
    this.loading.set(true);
    this.errorMessage.set('');
    this.procurementService.listRequests().subscribe({
      next: (requests) => { this.requests.set(requests); this.loading.set(false); },
      error: (error: unknown) => { this.errorMessage.set(this.readError(error)); this.loading.set(false); }
    });
  }

  updateFilter(): void { this.page.set(1); }
  clearFilters(): void {
    this.search.set(''); this.department.set(''); this.status.set(''); this.priority.set(''); this.sort.set('created_desc'); this.page.set(1);
  }
  previousPage(): void { if (this.page() > 1) this.page.update((page) => page - 1); }
  nextPage(): void { if (this.page() < this.totalPages()) this.page.update((page) => page + 1); }
  statusClass(status: string | null): string { return `status-${(status ?? 'unknown').toLowerCase().replace(/\s+/g, '-')}`; }

  private compareRequests(a: ProcurementRequest, b: ProcurementRequest): number {
    switch (this.sort()) {
      case 'number_asc': return a.request_number.localeCompare(b.request_number);
      case 'title_asc': return a.request_title.localeCompare(b.request_title);
      case 'budget_desc': return (b.estimated_budget ?? 0) - (a.estimated_budget ?? 0);
      case 'created_asc': return (a.created_at ?? '').localeCompare(b.created_at ?? '');
      default: return (b.created_at ?? '').localeCompare(a.created_at ?? '');
    }
  }

  private readError(error: unknown): string {
    if (typeof error === 'object' && error !== null && 'error' in error) {
      const response = (error as { error?: { detail?: unknown } }).error;
      if (typeof response?.detail === 'string') return response.detail;
    }
    return 'Unable to load procurement requests. Please try again.';
  }
}
