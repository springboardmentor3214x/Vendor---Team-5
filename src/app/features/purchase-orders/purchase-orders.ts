import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-purchase-order',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    RouterModule
  ],
  templateUrl: './purchase-orders.html',
  styleUrls: ['./purchase-orders.css']
})
export class PurchaseOrdersComponent {

  searchText: string = '';
  selectedStatus: string = 'All Status';
  selectedVendor: string = 'All Vendors';
  dateRange: string = '10/07/2026 - 30/06/2026';

  vendors = [
    'Tech Solutions Pvt Ltd',
    'Global Supplies',
    'Industrial Parts Co.',
    'IT Needs India'
  ];

  purchaseOrders = [
    {
      poNo: 'PO-001',
      vendor: 'Tech Solutions Pvt Ltd',
      status: 'Approved',
      date: '10 Jul 2026',
      amount: '₹5,20,000'
    },
    {
      poNo: 'PO-002',
      vendor: 'Global Supplies',
      status: 'Pending',
      date: '11 Jul 2026',
      amount: '₹3,75,000'
    },
    {
      poNo: 'PO-003',
      vendor: 'Industrial Parts Co.',
      status: 'Approved',
      date: '12 Jul 2026',
      amount: '₹8,90,000'
    },
    {
      poNo: 'PO-004',
      vendor: 'IT Needs India',
      status: 'Rejected',
      date: '13 Jul 2026',
      amount: '₹2,15,000'
    }
  ];

  resetFilters(): void {
    this.searchText = '';
    this.selectedStatus = 'All Status';
    this.selectedVendor = 'All Vendors';
    this.dateRange = '';
  }

  createPurchaseOrder(): void {
    alert('Navigate to Create Purchase Order Page');
  }

}