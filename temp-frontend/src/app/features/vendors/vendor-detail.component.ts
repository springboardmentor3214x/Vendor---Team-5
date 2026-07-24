import { CommonModule } from '@angular/common';
import { Component, OnInit, signal } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';
import {
  VENDOR_APPROVER_ROLES,
  Vendor,
  VendorService
} from '../../core/services/vendor.service';

@Component({
  selector: 'app-vendor-detail',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterLink],
  templateUrl: './vendor-detail.component.html',
  styleUrl: './vendor-detail.component.css'
})
export class VendorDetailComponent implements OnInit {
  readonly vendor = signal<Vendor | null>(null);
  readonly loading = signal(true);
  readonly acting = signal(false);
  readonly errorMessage = signal('');
  readonly successMessage = signal('');
  readonly remarksForm: FormGroup;

  private vendorId = 0;

  constructor(
    private readonly fb: FormBuilder,
    private readonly vendorService: VendorService,
    private readonly authService: AuthService,
    private readonly route: ActivatedRoute
  ) {
    this.remarksForm = this.fb.nonNullable.group({
      remarks: ['']
    });
  }

  get canApprove(): boolean {
    return this.authService.hasRole(...VENDOR_APPROVER_ROLES);
  }

  ngOnInit(): void {
    const id = Number(this.route.snapshot.paramMap.get('id'));
    if (!Number.isFinite(id)) {
      this.loading.set(false);
      this.errorMessage.set('Invalid vendor id.');
      return;
    }

    this.vendorId = id;
    this.loadVendor();
  }

  loadVendor(): void {
    this.loading.set(true);
    this.errorMessage.set('');

    this.vendorService.getVendor(this.vendorId).subscribe({
      next: (vendor) => {
        this.vendor.set(vendor);
        this.loading.set(false);
      },
      error: (err) => {
        this.loading.set(false);
        this.errorMessage.set(this.readError(err, 'Unable to load vendor details.'));
      }
    });
  }

  approve(): void {
    if (!this.canApprove) {
      return;
    }

    this.acting.set(true);
    this.errorMessage.set('');
    this.successMessage.set('');

    this.vendorService
      .approveVendor(this.vendorId, { remarks: this.remarksForm.getRawValue().remarks || null })
      .subscribe({
        next: (vendor) => {
          this.vendor.set(vendor);
          this.acting.set(false);
          this.successMessage.set('Vendor approved successfully.');
        },
        error: (err) => {
          this.acting.set(false);
          this.errorMessage.set(this.readError(err, 'Unable to approve vendor.'));
        }
      });
  }

  reject(): void {
    if (!this.canApprove) {
      return;
    }

    this.acting.set(true);
    this.errorMessage.set('');
    this.successMessage.set('');

    this.vendorService
      .rejectVendor(this.vendorId, { remarks: this.remarksForm.getRawValue().remarks || null })
      .subscribe({
        next: (vendor) => {
          this.vendor.set(vendor);
          this.acting.set(false);
          this.successMessage.set('Vendor rejected successfully.');
        },
        error: (err) => {
          this.acting.set(false);
          this.errorMessage.set(this.readError(err, 'Unable to reject vendor.'));
        }
      });
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