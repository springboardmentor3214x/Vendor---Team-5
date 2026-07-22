import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
@Component({
  selector: 'app-vendor-list',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './vendor-list.html',
  styleUrls: ['./vendor-list.css']
})
export class VendorListComponent {

  searchText: string = '';

  vendors = [
    {
      name: 'Tech Solutions',
      phone: '9768506541',
      email: 'bharathi12@gmail.com',
      status: 'Active',
      approval: 'Approved'
    },
    {
      name: 'Build Constructions',
      phone: '4367236541',
      email: 'sonali65@gmail.com',
      status: 'Pending',
      approval: 'Pending'
    },
    {
      name: 'Green Supplies',
      phone: '4325678961',
      email: 'swathi123@gmail.com',
      status: 'Active',
      approval: 'Approved'
    },
    {
      name: 'Security Systems',
      phone: '9875678961',
      email: 'pranjelly20@gmail.com',
      status: 'Inactive',
      approval: 'Approved'
    },
    {
      name: 'Future Tech',
      phone: '4356745305',
      email: 'priya120@gmail.com',
      status: 'Inactive',
      approval: 'Pending'
    }
  ];

  constructor() {}

  addVendor() {
    alert('Add Vendor Clicked');
  }

  viewVendor(vendor: any) {
    console.log('View Vendor', vendor);
  }

  editVendor(vendor: any) {
    console.log('Edit Vendor', vendor);
  }

  deleteVendor(vendor: any) {
    const confirmDelete = confirm(
      `Are you sure you want to delete ${vendor.name}?`
    );

    if (confirmDelete) {
      this.vendors = this.vendors.filter(v => v !== vendor);
    }
  }
}