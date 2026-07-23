import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';

@Component({
  selector: 'app-invoice-management',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './invoice-management.html',
  styleUrls: ['./invoice-management.css']
})
export class InvoiceManagementComponent {

  constructor(private router: Router) {}

  searchText = '';

  invoices = [
    {
      number: 'INV-001',
      vendor: 'TechPro Solutions',
      invoiceDate: '10 Jul 2026',
      dueDate: '20 Jul 2026',
      amount: '₹5,20,000',
      status: 'Paid'
    },
    {
      number: 'INV-002',
      vendor: 'Global Supplies Ltd.',
      invoiceDate: '09 Jul 2026',
      dueDate: '24 Jul 2026',
      amount: '₹3,75,000',
      status: 'Paid'
    },
    {
      number: 'INV-003',
      vendor: 'Prime Components',
      invoiceDate: '08 Jul 2026',
      dueDate: '23 Jul 2026',
      amount: '₹8,90,000',
      status: 'Pending'
    },
    {
      number: 'INV-004',
      vendor: 'Reliable Industries',
      invoiceDate: '07 Jul 2026',
      dueDate: '20 Jul 2026',
      amount: '₹2,15,000',
      status: 'Overdue'
    },
    {
      number: 'INV-005',
      vendor: 'Advanced Systems',
      invoiceDate: '05 Jul 2026',
      dueDate: '23 Jul 2026',
      amount: '₹6,40,000',
      status: 'Pending'
    }
  ];

  logout(): void {
    this.router.navigate(['/login']);
  }

}