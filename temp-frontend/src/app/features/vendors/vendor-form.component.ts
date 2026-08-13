import { CommonModule } from '@angular/common';
import { Component, OnInit, signal } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import {
  VENDOR_CATEGORIES,
  VENDOR_STATUSES,
  VendorCreatePayload,
  VendorService
} from '../../core/services/vendor.service';

@Component({
  selector: 'app-vendor-form',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterLink],
  templateUrl: './vendor-form.component.html',
  styleUrl: './vendor-form.component.css'
})
export class VendorFormComponent implements OnInit {
  readonly categories = signal<readonly string[]>(VENDOR_CATEGORIES);
  readonly statuses = VENDOR_STATUSES;
  readonly isEdit = signal(false);
  readonly vendorId = signal<number | null>(null);
  readonly loading = signal(false);
  readonly saving = signal(false);
  readonly errorMessage = signal('');
  readonly form: FormGroup;

  constructor(
    private readonly fb: FormBuilder,
    private readonly vendorService: VendorService,
    private readonly route: ActivatedRoute,
    private readonly router: Router
  ) {
    this.form = this.fb.nonNullable.group({
      company_name: ['', [Validators.required, Validators.minLength(2)]],
      vendor_category: [''],
      contact_person_name: ['', [Validators.required, Validators.minLength(2)]],
      designation: [''],
      email: ['', [Validators.required, Validators.email]],
      phone_number: ['', [Validators.required, Validators.minLength(7)]],
      alternate_phone: [''],
      gst_number: [''],
      pan_number: [''],
      company_registration_number: [''],
      address_line1: [''],
      address_line2: [''],
      city: [''],
      state: [''],
      country: [''],
      pincode: [''],
      website: [''],
      description: [''],
      bank_account_number: [''],
      ifsc_code: [''],
      payment_terms: [''],
      vendor_status: ['Pending']
    });
  }

  ngOnInit(): void {
    this.loadCategories();
    const idParam = this.route.snapshot.paramMap.get('id');
    if (!idParam) {
      return;
    }

    const id = Number(idParam);
    if (!Number.isFinite(id)) {
      this.errorMessage.set('Invalid vendor id.');
      return;
    }

    this.isEdit.set(true);
    this.vendorId.set(id);
    this.loading.set(true);

    this.vendorService.getVendor(id).subscribe({
      next: (vendor) => {
        this.form.patchValue({
          company_name: vendor.company_name,
          vendor_category: vendor.vendor_category ?? '',
          contact_person_name: vendor.contact_person_name,
          designation: vendor.designation ?? '',
          email: vendor.email,
          phone_number: vendor.phone_number,
          alternate_phone: vendor.alternate_phone ?? '',
          gst_number: vendor.gst_number ?? '',
          pan_number: vendor.pan_number ?? '',
          company_registration_number: vendor.company_registration_number ?? '',
          address_line1: vendor.address_line1 ?? '',
          address_line2: vendor.address_line2 ?? '',
          city: vendor.city ?? '',
          state: vendor.state ?? '',
          country: vendor.country ?? '',
          pincode: vendor.pincode ?? '',
          website: vendor.website ?? '',
          description: vendor.description ?? '',
          bank_account_number: vendor.bank_account_number ?? '',
          ifsc_code: vendor.ifsc_code ?? '',
          payment_terms: vendor.payment_terms ?? '',
          vendor_status: vendor.vendor_status || 'Pending'
        });
        this.loading.set(false);
      },
      error: (err) => {
        this.loading.set(false);
        this.errorMessage.set(this.readError(err, 'Unable to load vendor.'));
      }
    });
  }

  private loadCategories(): void {
    this.vendorService.listCategories().subscribe({
      next: (categories) => this.categories.set(categories.filter((category) => category.isActive !== false).map((category) => category.name)),
      error: () => this.categories.set(VENDOR_CATEGORIES)
    });
  }

  submit(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      this.errorMessage.set('Please fill all required vendor fields.');
      return;
    }

    const raw = this.form.getRawValue();
    const payload: VendorCreatePayload = {
      company_name: raw.company_name.trim(),
      vendor_category: raw.vendor_category?.trim() || null,
      contact_person_name: raw.contact_person_name.trim(),
      designation: raw.designation?.trim() || null,
      email: raw.email.trim().toLowerCase(),
      phone_number: raw.phone_number.trim(),
      alternate_phone: raw.alternate_phone?.trim() || null,
      gst_number: raw.gst_number?.trim() || null,
      pan_number: raw.pan_number?.trim() || null,
      company_registration_number: raw.company_registration_number?.trim() || null,
      address_line1: raw.address_line1?.trim() || null,
      address_line2: raw.address_line2?.trim() || null,
      city: raw.city?.trim() || null,
      state: raw.state?.trim() || null,
      country: raw.country?.trim() || null,
      pincode: raw.pincode?.trim() || null,
      website: raw.website?.trim() || null,
      description: raw.description?.trim() || null,
      bank_account_number: raw.bank_account_number?.trim() || null,
      ifsc_code: raw.ifsc_code?.trim() || null,
      payment_terms: raw.payment_terms?.trim() || null,
      vendor_status: raw.vendor_status || 'Pending'
    };

    this.saving.set(true);
    this.errorMessage.set('');

    const request$ = this.isEdit()
      ? this.vendorService.updateVendor(this.vendorId()!, payload)
      : this.vendorService.createVendor(payload);

    request$.subscribe({
      next: (vendor) => {
        this.saving.set(false);
        this.router.navigate(['/vendors', vendor.id]);
      },
      error: (err) => {
        this.saving.set(false);
        this.errorMessage.set(this.readError(err, 'Unable to save vendor.'));
      }
    });
  }

  control(name: string) {
    return this.form.get(name);
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
