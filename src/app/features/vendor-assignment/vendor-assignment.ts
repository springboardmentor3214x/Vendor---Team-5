import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-vendor-assignment',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    RouterModule
  ],
  templateUrl: './vendor-assignment.html',
  styleUrls: ['./vendor-assignment.css']
})
export class VendorAssignmentComponent {

  selectedVendor: string = '';

  request = {
    requestNumber: 'PR-2026-00124',
    requestTitle: 'Laptop Purchase for Development Team',
    department: 'IT Department',
    requestedDate: '17 Jul 2026',
    priority: 'High',
    status: 'Approved'
  };

  vendors = [
    {
      name: 'ABC Enterprises',
      category: 'IT Hardware',
      contact: 'Ramesh Kumar',
      reliability: '92%',
      performance: '95%',
      delivery: '★★★★★'
    },
    {
      name: 'Dell Technologies',
      category: 'IT Hardware',
      contact: 'Sanjay Mehta',
      reliability: '88%',
      performance: '90%',
      delivery: '★★★★☆'
    },
    {
      name: 'XYZ Solutions',
      category: 'IT Accessories',
      contact: 'Priya Nair',
      reliability: '75%',
      performance: '78%',
      delivery: '★★★★☆'
    },
    {
      name: 'Tech Supplies Pvt Ltd',
      category: 'Office Equipment',
      contact: 'Vikram Rao',
      reliability: '68%',
      performance: '70%',
      delivery: '★★★☆☆'
    },
    {
      name: 'Global Infotech',
      category: 'IT Hardware',
      contact: 'Arun Verma',
      reliability: '60%',
      performance: '65%',
      delivery: '★★★☆☆'
    }
  ];

  assignVendor(): void {
    if (this.selectedVendor) {
      alert('Vendor Assigned Successfully!');
    } else {
      alert('Please select a vendor.');
    }
  }

  cancel(): void {
    this.selectedVendor = '';
  }

}