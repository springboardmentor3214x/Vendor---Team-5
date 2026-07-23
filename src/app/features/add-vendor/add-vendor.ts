import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { VendorService } from '../../services/vendor.service';

@Component({
  selector: 'app-add-vendor',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './add-vendor.html',
  styleUrls: ['./add-vendor.css']
})
export class AddVendorComponent {

  constructor(
    private router: Router,
    private vendorService: VendorService
  ) {}

  vendor = {
    companyName: '',
    vendorCategory: '',
    contactPerson: '',
    destination: '',
    email: '',
    phone: '',
    alternatePhone: '',
    gstNumber: '',
    panNumber: '',
    registrationNumber: '',
    address1: '',
    address2: '',
    city: '',
    state: '',
    country: '',
    pincode: '',
    website: '',
    description: '',
    bankAccountNumber: '',
    ifscCode: '',
    paymentTerms: '',
    status: 'pending'
  };

  saveVendor() {

    if (
      !this.vendor.companyName ||
      !this.vendor.vendorCategory ||
      !this.vendor.contactPerson ||
      !this.vendor.email
    ) {
      alert('Please fill all required fields.');
      return;
    }

    this.vendorService.addVendor(this.vendor as any).subscribe({

      next: () => {
        alert('Vendor added successfully.');
        this.router.navigate(['/vendor-list']);
      },

      error: (err) => {
        console.error(err);
        alert('Failed to add vendor.');
      }

    });

  }

  cancel() {

    this.vendor = {
      companyName: '',
      vendorCategory: '',
      contactPerson: '',
      destination: '',
      email: '',
      phone: '',
      alternatePhone: '',
      gstNumber: '',
      panNumber: '',
      registrationNumber: '',
      address1: '',
      address2: '',
      city: '',
      state: '',
      country: '',
      pincode: '',
      website: '',
      description: '',
      bankAccountNumber: '',
      ifscCode: '',
      paymentTerms: '',
      status: 'pending'
    };

  }

}