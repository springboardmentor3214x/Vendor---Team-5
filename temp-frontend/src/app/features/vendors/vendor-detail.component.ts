import { CommonModule } from '@angular/common';
import { Component, ElementRef, OnInit, ViewChild, signal } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';
import {
  VENDOR_APPROVER_ROLES,
  VENDOR_DOCUMENT_TYPES,
  Vendor,
  VendorDocument,
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
  readonly approvalAction = signal<'approve' | 'reject' | null>(null);
  readonly uploading = signal(false);
  readonly errorMessage = signal('');
  readonly successMessage = signal('');
  readonly remarksForm: FormGroup;
  readonly documentForm: FormGroup;
  readonly selectedFileName = signal('');
  readonly documents = signal<VendorDocument[]>([]);
  readonly documentTypes = VENDOR_DOCUMENT_TYPES;
  readonly vendorApprovalApiAvailable = true;
  readonly vendorDocumentUploadApiAvailable = true;

  @ViewChild('documentFile') private documentFileInput?: ElementRef<HTMLInputElement>;

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
    this.documentForm = this.fb.nonNullable.group({
      document_type: ['', Validators.required]
    });
  }

  get canApprove(): boolean {
    return this.authService.hasRole(...VENDOR_APPROVER_ROLES);
  }

  get canEdit(): boolean {
    return this.authService.hasRole('Administrator', 'Procurement Manager');
  }

  get canViewPerformance(): boolean {
    return this.authService.hasRole('Administrator', 'Procurement Manager', 'Supply Chain Manager', 'Auditor');
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
        this.loadDocuments();
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
    this.approvalAction.set('approve');
    this.errorMessage.set('');
    this.successMessage.set('');

    this.vendorService
      .approveVendor(this.vendorId, { remarks: this.remarksForm.getRawValue().remarks || null })
      .subscribe({
        next: (vendor) => {
          this.vendor.set(vendor);
          this.acting.set(false);
          this.approvalAction.set(null);
          this.remarksForm.reset();
          this.successMessage.set('Vendor approved successfully.');
        },
        error: (err) => {
          this.acting.set(false);
          this.approvalAction.set(null);
          this.errorMessage.set(this.readError(err, 'Unable to approve vendor.'));
        }
      });
  }

  reject(): void {
    if (!this.canApprove) {
      return;
    }

    if (!window.confirm('Reject this vendor? This updates the vendor status to Rejected.')) {
      return;
    }

    this.acting.set(true);
    this.approvalAction.set('reject');
    this.errorMessage.set('');
    this.successMessage.set('');

    this.vendorService
      .rejectVendor(this.vendorId, { remarks: this.remarksForm.getRawValue().remarks || null })
      .subscribe({
        next: (vendor) => {
          this.vendor.set(vendor);
          this.acting.set(false);
          this.approvalAction.set(null);
          this.remarksForm.reset();
          this.successMessage.set('Vendor rejected successfully.');
        },
        error: (err) => {
          this.acting.set(false);
          this.approvalAction.set(null);
          this.errorMessage.set(this.readError(err, 'Unable to reject vendor.'));
        }
      });
  }

  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    this.selectedFileName.set(input.files?.[0]?.name ?? '');
  }

  uploadDocument(): void {
    const file = this.documentFileInput?.nativeElement.files?.[0];
    if (this.documentForm.invalid || !file) {
      this.documentForm.markAllAsTouched();
      this.errorMessage.set('Select a document type and file before uploading.');
      return;
    }

    this.uploading.set(true);
    this.errorMessage.set('');
    this.successMessage.set('');

    this.vendorService
      .uploadDocument(this.vendorId, this.documentForm.getRawValue().document_type, file)
      .subscribe({
        next: (response) => {
          this.uploading.set(false);
          this.successMessage.set(response.message || 'Document uploaded successfully.');
          this.documentForm.reset();
          this.selectedFileName.set('');
          if (this.documentFileInput) {
            this.documentFileInput.nativeElement.value = '';
          }
          this.loadDocuments();
        },
        error: (err) => {
          this.uploading.set(false);
          this.errorMessage.set(this.readError(err, 'Unable to upload document.'));
        }
      });
  }

  private loadDocuments(): void {
    this.vendorService.listDocuments(this.vendorId).subscribe({
      next: (documents) => this.documents.set(documents),
      error: () => this.documents.set([])
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
    if (err instanceof Error && err.message) {
      return err.message;
    }
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
