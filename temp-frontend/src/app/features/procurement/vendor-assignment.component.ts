import { CommonModule } from '@angular/common';
import { Component, inject, signal } from '@angular/core';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { forkJoin } from 'rxjs';
import { ApprovedProcurementVendor, ProcurementRequest, ProcurementService } from '../../core/services/procurement.service';

@Component({
  selector: 'app-vendor-assignment',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './vendor-assignment.component.html',
  styleUrl: './vendor-assignment.component.css'
})
export class VendorAssignmentComponent {
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly procurementService = inject(ProcurementService);
  readonly request = signal<ProcurementRequest | null>(null);
  readonly vendors = signal<ApprovedProcurementVendor[]>([]);
  readonly selectedVendorId = signal<number | null>(null);
  readonly loading = signal(true);
  readonly assigning = signal(false);
  readonly errorMessage = signal('');

  ngOnInit(): void {
    const requestId = Number(this.route.snapshot.paramMap.get('id'));
    if (!Number.isInteger(requestId) || requestId <= 0) { this.errorMessage.set('Invalid procurement request id.'); this.loading.set(false); return; }
    this.load(requestId);
  }

  get canAssign(): boolean { const request = this.request(); return request?.approval_status === 'Approved' && !request.vendor_id; }

  selectVendor(vendorId: number): void { if (this.canAssign && !this.assigning()) this.selectedVendorId.set(vendorId); }

  assign(): void {
    const request = this.request();
    const vendorId = this.selectedVendorId();
    if (!request || !vendorId || !this.canAssign || this.assigning()) return;
    this.errorMessage.set(''); this.assigning.set(true);
    this.procurementService.assignVendor(request.id, vendorId).subscribe({
      next: (updated) => this.router.navigate(['/procurement/requests', updated.id], { state: { successMessage: 'Vendor assigned successfully.' } }),
      error: (error: unknown) => { this.errorMessage.set(this.readError(error)); this.assigning.set(false); }
    });
  }

  private load(requestId: number): void {
    this.procurementService.getRequest(requestId).subscribe({
      next: (request) => {
        this.request.set(request);
        if (request.approval_status !== 'Approved' || request.vendor_id) { this.loading.set(false); return; }
        this.procurementService.getApprovedVendors(requestId).subscribe({
          next: (vendors) => { this.vendors.set(vendors); this.loading.set(false); },
          error: (error: unknown) => { this.errorMessage.set(this.readError(error)); this.loading.set(false); }
        });
      },
      error: (error: unknown) => { this.errorMessage.set(this.readError(error)); this.loading.set(false); }
    });
  }

  private readError(error: unknown): string {
    if (typeof error === 'object' && error !== null && 'error' in error) {
      const detail = (error as { error?: { detail?: unknown } }).error?.detail;
      if (typeof detail === 'string') return detail;
    }
    return 'Unable to load vendor assignment information. Please try again.';
  }
}
