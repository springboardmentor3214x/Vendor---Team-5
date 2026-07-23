import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { Router, RouterLink } from '@angular/router';
@Component({
  selector: 'app-request-list',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    RouterModule,
    RouterLink,
  ],
  templateUrl: './request-list.html',
  styleUrls: ['./request-list.css']
})
export class RequestListComponent {

  searchText: string = '';

  requests = [

    {
      number: 'PR-2026-00125',
      title: 'Office Furniture Purchase',
      department: 'HR',
      requestedBy: 'John Mathew',
      vendor: '-',
      priority: 'High',
      budget: '₹1,20,000',
      status: 'Pending',
      date: '19 Jul 2026'
    },

    {
      number: 'PR-2026-00124',
      title: 'Laptop Purchase',
      department: 'IT',
      requestedBy: 'Alex Joseph',
      vendor: 'ABC Enterprises',
      priority: 'High',
      budget: '₹2,45,000',
      status: 'Approved',
      date: '18 Jul 2026'
    },

    {
      number: 'PR-2026-00123',
      title: 'Printer Accessories',
      department: 'Admin',
      requestedBy: 'Mary Thomas',
      vendor: 'XYZ Solutions',
      priority: 'Medium',
      budget: '₹85,000',
      status: 'Approved',
      date: '17 Jul 2026'
    },

    {
      number: 'PR-2026-00122',
      title: 'Server Upgrade',
      department: 'IT',
      requestedBy: 'Rohit Kumar',
      vendor: 'Tech Solutions',
      priority: 'High',
      budget: '₹3,75,000',
      status: 'Completed',
      date: '16 Jul 2026'
    },

    {
      number: 'PR-2026-00121',
      title: 'Stationery Purchase',
      department: 'Finance',
      requestedBy: 'Sneha Reddy',
      vendor: 'Office Mart',
      priority: 'Low',
      budget: '₹25,000',
      status: 'Approved',
      date: '15 Jul 2026'
    },

    {
      number: 'PR-2026-00120',
      title: 'Software License',
      department: 'IT',
      requestedBy: 'David Wilson',
      vendor: 'Microsoft',
      priority: 'Medium',
      budget: '₹1,15,000',
      status: 'Pending',
      date: '14 Jul 2026'
    },

    {
      number: 'PR-2026-00119',
      title: 'Networking Equipment',
      department: 'IT',
      requestedBy: 'James Thomas',
      vendor: 'Cisco',
      priority: 'High',
      budget: '₹4,80,000',
      status: 'Approved',
      date: '13 Jul 2026'
    },

    {
      number: 'PR-2026-00118',
      title: 'Office Chairs',
      department: 'Admin',
      requestedBy: 'Priya Sharma',
      vendor: 'Furniture Hub',
      priority: 'Low',
      budget: '₹65,000',
      status: 'Completed',
      date: '12 Jul 2026'
    }

  ];

  viewRequest(request: any): void {
    console.log('View', request);
  }

  editRequest(request: any): void {
    console.log('Edit', request);
  }

  deleteRequest(request: any): void {

    if (confirm('Are you sure you want to delete this request?')) {

      this.requests = this.requests.filter(
        r => r.number !== request.number
      );

    }

  }

}