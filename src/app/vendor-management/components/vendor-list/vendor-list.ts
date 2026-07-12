import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink, Router } from '@angular/router';

interface Vendor {
  vendorName: string;
  phone: string;
  email: string;
  status: 'Active' | 'Pending' | 'InActive' | 'In Active';
  approvedStatus: 'Approved' | 'Pending';
}

@Component({
  selector: 'app-vendor-list',
  templateUrl: './vendor-list.html',
  styleUrl: './vendor-list.css'
})
export class VendorListComponent {

  constructor(private router: Router) {}

  vendors: Vendor[] = [
    {
      vendorName: 'Tech Solutions',
      phone: '9768506541',
      email: 'bharathi12@gmail.com',
      status: 'Active',
      approvedStatus: 'Approved'
    },
    {
      vendorName: 'Build Constructions',
      phone: '4367236541',
      email: 'sonali65@gmail.com',
      status: 'Pending',
      approvedStatus: 'Pending'
    },
    {
      vendorName: 'Green Supplies',
      phone: '4325678961',
      email: 'swathi123@gmail.com',
      status: 'Active',
      approvedStatus: 'Approved'
    },
    {
      vendorName: 'Security Systems',
      phone: '9875678961',
      email: 'pranjelly20@gmail.com',
      status: 'InActive',
      approvedStatus: 'Approved'
    },
    {
      vendorName: 'Future Tech',
      phone: '4356745305',
      email: 'priya120@gmail.com',
      status: 'In Active',
      approvedStatus: 'Pending'
    }
  ];

  statusClass(status: string): string {
    if (status === 'Active' || status === 'Approved') return 'completed';
    if (status === 'Pending') return 'pending';
    if (status === 'InActive' || status === 'In Active') return 'inactive';
    return '';
  }

  logout(): void {
    this.router.navigate(['/login']);
  }
}