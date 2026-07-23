import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-vendor-management',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    RouterModule
  ],
  templateUrl: './vendor-management.html',
  styleUrls: ['./vendor-management.css']
})
export class VendorManagementComponent {

  vendors = [
    {
      id: 'VEND-001',
      company: 'Tech Solutions Pvt Ltd',
      category: 'IT Vendors',
      contact: 'Swathi',
      status: 'Active',
      approval: 'Approved'
    },
    {
      id: 'VEND-002',
      company: 'Global Supplies',
      category: 'Raw Material Suppliers',
      contact: 'Bharathi',
      status: 'Pending',
      approval: 'Pending'
    },
    {
      id: 'VEND-003',
      company: 'Industrial Parts Co.',
      category: 'Equipment Vendors',
      contact: 'Sonali',
      status: 'Active',
      approval: 'Approved'
    },
    {
      id: 'VEND-004',
      company: 'IT Needs India',
      category: 'IT Vendors',
      contact: 'Pranjelly',
      status: 'Inactive',
      approval: 'Rejected'
    }
  ];

  addVendor(): void {
    alert('Add Vendor button clicked');
  }

  resetFilters(): void {
    alert('Filters Reset');
  }

}