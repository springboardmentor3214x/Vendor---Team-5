import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';

interface Payment {
  paymentId: string;
  vendor: string;
  invoiceNumber: string;
  paymentDate: string;
  amount: string;
  paymentMethod: string;
  status: string;
}

@Component({
  selector: 'app-payment-details',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    RouterLink
  ],
  templateUrl: './payment-details.html',
  styleUrls: ['./payment-details.css']
})
export class PaymentDetailsComponent {

  constructor(private router: Router) {}

  searchText = '';

  selectedTab = 'All Orders';

  tabs = [
    'All Orders',
    'Completed',
    'Pending',
    'Failed'
  ];

  payments: Payment[] = [
    {
      paymentId: 'PAY-2026-001',
      vendor: 'TechPro Solutions',
      invoiceNumber: 'INV-2026-001',
      paymentDate: '20 Jul 2026',
      amount: '5,20,000',
      paymentMethod: 'Bank Transfer',
      status: 'Paid'
    },
    {
      paymentId: 'PAY-2026-002',
      vendor: 'Global Supplies Ltd.',
      invoiceNumber: 'INV-2026-002',
      paymentDate: '24 Jul 2026',
      amount: '3,75,000',
      paymentMethod: 'NEFT',
      status: 'Paid'
    },
    {
      paymentId: 'PAY-2026-003',
      vendor: 'Prime Components',
      invoiceNumber: 'INV-2026-003',
      paymentDate: '23 Jul 2026',
      amount: '8,90,000',
      paymentMethod: 'RTGS',
      status: 'Pending'
    },
    {
      paymentId: 'PAY-2026-004',
      vendor: 'Reliable Industries',
      invoiceNumber: 'INV-2026-004',
      paymentDate: '20 Jul 2026',
      amount: '2,15,000',
      paymentMethod: 'Bank Transfer',
      status: 'Overdue'
    },
    {
      paymentId: 'PAY-2026-005',
      vendor: 'Advanced Systems',
      invoiceNumber: 'INV-2026-005',
      paymentDate: '23 Jul 2026',
      amount: '6,40,000',
      paymentMethod: 'UPI',
      status: 'Pending'
    }
  ];

  get filteredPayments(): Payment[] {

    let data = this.payments;

    if (this.selectedTab !== 'All Orders') {
      data = data.filter(
        p => p.status.toLowerCase() === this.selectedTab.toLowerCase()
      );
    }

    if (this.searchText.trim()) {
      const search = this.searchText.toLowerCase();

      data = data.filter(payment =>
        payment.paymentId.toLowerCase().includes(search) ||
        payment.vendor.toLowerCase().includes(search) ||
        payment.invoiceNumber.toLowerCase().includes(search)
      );
    }

    return data;
  }

  changeTab(tab: string): void {
    this.selectedTab = tab;
  }

  logout(): void {
    this.router.navigate(['/login']);
  }
}