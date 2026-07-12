import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router } from '@angular/router';

@Component({

  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './add-vendor.html',
  styleUrl: './add-vendor.css'
})
export class AddVendorComponent {
  vendorForm: FormGroup;
  isSaving = false;

  constructor(
    private fb: FormBuilder,
    private router: Router
  ) {
    this.vendorForm = this.fb.group({
      vendorName: ['', Validators.required],
      email: ['', [Validators.required, Validators.email]],
      phone: ['', Validators.required],
      address: ['', Validators.required],
      gstNumber: ['', Validators.required],
      contactNumber: ['', Validators.required],
      company: ['', Validators.required],
      registrationDate: [''],
      status: ['']
    });
  }

  onSave(): void {
    if (this.vendorForm.invalid) {
      this.vendorForm.markAllAsTouched();
      return;
    }

    this.isSaving = true;

    // Replace with a real API call, e.g.:
    // this.vendorService.addVendor(this.vendorForm.value).subscribe({
    //   next: () => {
    //     this.isSaving = false;
    //     this.router.navigate(['/vendor-management']);
    //   },
    //   error: () => {
    //     this.isSaving = false;
    //   }
    // });

    setTimeout(() => {
      this.isSaving = false;
      this.router.navigate(['/vendor-management']);
    }, 800);
  }

  onCancel(): void {
    this.router.navigate(['/vendor-management']);
  }
}