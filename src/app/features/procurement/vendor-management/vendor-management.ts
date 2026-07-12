import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink, Router } from '@angular/router';
import { Vendor } from './vendor.model';

@Component({
  selector: 'app-vendor-management',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './vendor-management.html',
  styleUrl: './vendor-management.css'
})
export class VendorManagementComponent {

  constructor(private router: Router) {}

  // Mock data - matches the Figma "Vendor Management" table
  vendors: Vendor[] = [
    {
      vendorId: 'VEND-001',
      companyName: 'Tech Solutions Pvt Ltd',
      category: 'IT Vendors',
      contactPerson: 'Swathi',
      status: 'Active',
      approvalStatus: 'Approved'
    },
    {
      vendorId: 'VEND-002',
      companyName: 'Global Supplies',
      category: 'Raw Material Suppliers',
      contactPerson: 'Bharathi',
      status: 'Pending',
      approvalStatus: 'Pending'
    },
    {
      vendorId: 'VEND-003',
      companyName: 'Industrial Parts Co.',
      category: 'Equipment Vendors',
      contactPerson: 'Sonali',
      status: 'Active',
      approvalStatus: 'Approved'
    },
    {
      vendorId: 'VEND-004',
      companyName: 'IT Needs India',
      category: 'IT Vendors',
      contactPerson: 'Pranjelly',
      status: 'Inactive',
      approvalStatus: 'Rejected'
    }
  ];

  statusClass(value: string): string {
    if (value === 'Active' || value === 'Approved') return 'completed';
    if (value === 'Pending') return 'pending';
    if (value === 'Inactive') return 'inactive';
    if (value === 'Rejected') return 'rejected';
    return '';
  }

  resetFilters(): void {
    // reset search/filter dropdowns here later
  }

  addVendor(): void {
    this.router.navigate(['/procurement/vendor-management/add-vendor']);
  }

  logout(): void {
    this.router.navigate(['/login']);
  }
}