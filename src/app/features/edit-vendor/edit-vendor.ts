import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';

@Component({
  selector: 'app-edit-vendor',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './edit-vendor.html',
  styleUrls: ['./edit-vendor.css']
})
export class EditVendorComponent {

  constructor(private router: Router) {}

  vendor = {

    companyName: 'Tech Solution PVT LTD',

    category: 'IT Services',

    contactPerson: 'Ramesh Kumar',

    destination: 'Hyderabad',

    email: 'techsolution@gmail.com',

    phone: '9876543210',

    altPhone: '9876500000',

    gst: '36ABCDE1234F1Z5',

    pan: 'ABCDE1234F',

    registration: 'REG123456789',

    address1: 'Madhapur',

    address2: 'Hitech City',

    city: 'Hyderabad',

    state: 'Telangana',

    country: 'India',

    pincode: '500081',

    website: 'www.techsolution.com',

    description: 'IT Software Services',

    bankAccount: '123456789012',

    ifsc: 'SBIN0001234',

    paymentTerms: '30 Days',

    status: 'Active'

  };

  saveVendor(): void {

    console.log('Vendor Saved', this.vendor);

    alert('Vendor details saved successfully.');

  }

  updateVendor(): void {

    console.log('Vendor Updated', this.vendor);

    alert('Vendor updated successfully.');

  }

  resetForm(): void {

    this.vendor = {

      companyName: '',

      category: '',

      contactPerson: '',

      destination: '',

      email: '',

      phone: '',

      altPhone: '',

      gst: '',

      pan: '',

      registration: '',

      address1: '',

      address2: '',

      city: '',

      state: '',

      country: '',

      pincode: '',

      website: '',

      description: '',

      bankAccount: '',

      ifsc: '',

      paymentTerms: '',

      status: ''

    };

  }

  back(): void {

    this.router.navigate(['/vendor-details']);

  }

}