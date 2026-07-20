import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';

interface PurchaseOrder {
  poNumber: string;
  vendor: string;
  orderDate: string;
  deliveryDate: string;
  amount: string;
  status: string;
}

@Component({
  selector: 'app-purchase-order',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    RouterLink
  ],
  templateUrl: './purchase-order.html',
  styleUrls: ['./purchase-order.css']
})
export class PurchaseOrderComponent {

  constructor(private router: Router) {}

  searchText = '';

  selectedTab = 'All Orders';

  tabs = [
    'All Orders',
    'Draft',
    'Pending Approval',
    'Approved',
    'Cancelled'
  ];

  purchaseOrders: PurchaseOrder[] = [
    {
      poNumber: 'PO-001',
      vendor: 'Supply Agreement 2026',
      orderDate: '10 Jul 2026',
      deliveryDate: '20 Jul 2026',
      amount: '5,20,000',
      status: 'Approved'
    },
    {
      poNumber: 'PO-002',
      vendor: 'Raw Material Supply',
      orderDate: '09 Jul 2026',
      deliveryDate: '24 Jul 2026',
      amount: '3,75,000',
      status: 'Approved'
    },
    {
      poNumber: 'PO-003',
      vendor: 'Equipment Maintenance',
      orderDate: '08 Jul 2026',
      deliveryDate: '23 Jul 2026',
      amount: '8,90,000',
      status: 'Pending Approval'
    },
    {
      poNumber: 'PO-004',
      vendor: 'IT Services Agreement',
      orderDate: '07 Jul 2026',
      deliveryDate: '20 Jul 2026',
      amount: '2,15,000',
      status: 'Approved'
    },
    {
      poNumber: 'PO-005',
      vendor: 'Logistics Support',
      orderDate: '05 Jul 2026',
      deliveryDate: '23 Jul 2026',
      amount: '6,40,000',
      status: 'Cancelled'
    }
  ];

  get filteredOrders(): PurchaseOrder[] {

    let orders = this.purchaseOrders;

    if (this.selectedTab !== 'All Orders') {
      orders = orders.filter(
        order => order.status.toLowerCase() === this.selectedTab.toLowerCase()
      );
    }

    if (this.searchText.trim()) {
      const search = this.searchText.toLowerCase();

      orders = orders.filter(order =>
        order.poNumber.toLowerCase().includes(search) ||
        order.vendor.toLowerCase().includes(search) ||
        order.status.toLowerCase().includes(search)
      );
    }

    return orders;
  }

  changeTab(tab: string): void {
    this.selectedTab = tab;
  }

  logout(): void {
    this.router.navigate(['/login']);
  }

}