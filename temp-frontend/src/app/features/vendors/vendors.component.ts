import { CommonModule } from '@angular/common';
import { Component, OnInit, computed, signal } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';
import {
  APPROVAL_STATUSES,
  VENDOR_CATEGORIES,
  VENDOR_STATUSES,
  Vendor,
  VendorService
} from '../../core/services/vendor.service';

type SortKey = 'company_name' | 'vendor_status' | 'approval_status' | 'reliability_score' | 'id';

@Component({
  selector: 'app-vendors',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterLink],
  templateUrl: './vendors.component.html',
  styleUrl: './vendors.component.css'
})
export class VendorsComponent implements OnInit {
  readonly categories = VENDOR_CATEGORIES;
  readonly statuses = VENDOR_STATUSES;
  readonly approvalStatuses = APPROVAL_STATUSES;

  readonly vendors = signal<Vendor[]>([]);
  readonly loading = signal(false);
  readonly errorMessage = signal('');
  readonly sortKey = signal<SortKey>('company_name');
  readonly sortAsc = signal(true);
  readonly page = signal(1);
  readonly pageSize = 8;

  readonly filterForm: FormGroup;

  readonly sortedVendors = computed(() => {
    const key = this.sortKey();
    const asc = this.sortAsc();
    return [...this.vendors()].sort((a, b) => {
      const left = a[key] ?? '';
      const right = b[key] ?? '';
      if (typeof left === 'number' && typeof right === 'number') {
        return asc ? left - right : right - left;
      }
      return asc
        ? String(left).localeCompare(String(right))
        : String(right).localeCompare(String(left));
    });
  });

  readonly totalPages = computed(() =>
    Math.max(1, Math.ceil(this.sortedVendors().length / this.pageSize))
  );

  readonly pagedVendors = computed(() => {
    const start = (this.page() - 1) * this.pageSize;
    return this.sortedVendors().slice(start, start + this.pageSize);
  });

  constructor(
    private readonly fb: FormBuilder,
    private readonly vendorService: VendorService,
    private readonly authService: AuthService
  ) {
    this.filterForm = this.fb.nonNullable.group({
      search: [''],
      category: [''],
      status: [''],
      approval_status: ['']
    });
  }

  ngOnInit(): void {
    this.loadVendors();
  }

  loadVendors(): void {
    this.loading.set(true);
    this.errorMessage.set('');

    const { search, category, status, approval_status } = this.filterForm.getRawValue();

    this.vendorService
      .listVendors({
        search,
        category,
        status,
        approval_status
      })
      .subscribe({
        next: (items) => {
          this.vendors.set(items);
          this.page.set(1);
          this.loading.set(false);
        },
        error: (err) => {
          this.loading.set(false);
          this.errorMessage.set(this.readError(err, 'Unable to load vendors.'));
        }
      });
  }

  applyFilters(): void {
    this.loadVendors();
  }

  clearFilters(): void {
    this.filterForm.reset({
      search: '',
      category: '',
      status: '',
      approval_status: ''
    });
    this.loadVendors();
  }

  setSort(key: SortKey): void {
    if (this.sortKey() === key) {
      this.sortAsc.update((value) => !value);
    } else {
      this.sortKey.set(key);
      this.sortAsc.set(true);
    }
  }

  prevPage(): void {
    this.page.update((value) => Math.max(1, value - 1));
  }

  nextPage(): void {
    this.page.update((value) => Math.min(this.totalPages(), value + 1));
  }

  get canEdit(): boolean {
    return this.authService.hasRole('Administrator', 'Procurement Manager');
  }

  hasActiveFilters(): boolean {
    const { search, category, status, approval_status } = this.filterForm.getRawValue();
    return !!(search.trim() || category || status || approval_status);
  }

  emptyMessage(): string {
    return this.hasActiveFilters()
      ? 'No vendors match the current filters.'
      : 'No vendor records are available yet.';
  }

  sortDirection(key: SortKey): string {
    if (this.sortKey() !== key) {
      return '';
    }
    return this.sortAsc() ? '↑' : '↓';
  }

  statusClass(status: string): string {
    switch (status) {
      case 'Active':
      case 'Approved':
        return 'badge-success';
      case 'Pending':
        return 'badge-warning';
      case 'Rejected':
      case 'Suspended':
        return 'badge-danger';
      default:
        return 'badge-muted';
    }
  }

  private readError(err: unknown, fallback: string): string {
    const detail = (err as { error?: { detail?: unknown } })?.error?.detail;
    if (typeof detail === 'string') {
      return detail;
    }
    if (Array.isArray(detail)) {
      return detail.map((item: { msg?: string }) => item?.msg).filter(Boolean).join(', ');
    }
    return fallback;
  }
}
