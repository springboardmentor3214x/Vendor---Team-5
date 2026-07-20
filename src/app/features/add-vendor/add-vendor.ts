import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';

@Component({
  selector: 'app-add-vendor',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './add-vendor.html',
  styleUrls: ['./add-vendor.css']
})
export class AddVendorComponent {

  constructor(private router: Router) {}

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
    status: ''
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

    console.log('Vendor Details:', this.vendor);

    alert('Vendor added successfully.');

    // Navigate to Vendor List page
    this.router.navigate(['/vendor-list']);
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
      status: ''
    };
  }

}