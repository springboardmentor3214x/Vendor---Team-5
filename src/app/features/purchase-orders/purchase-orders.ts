import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';

interface PurchaseOrder {
  poNo: string;
  vendor: string;
  status: string;
  date: string;
  amount: string;
}

@Component({
  selector: 'app-purchase-order',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule
  ],
  templateUrl: './purchase-orders.html',
  styleUrls: ['./purchase-orders.css']
})
export class PurchaseOrdersComponent {

  constructor(private router: Router) {}

  searchText = '';
  selectedStatus = 'All';
  selectedVendor = 'All';
  dateRange = '';

  vendors: string[] = [
    'Tech Solutions Pvt Ltd',
    'Global Supplies',
    'Industrial Parts Co.',
    'IT Needs India'
  ];

  purchaseOrders: PurchaseOrder[] = [
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
      status: 'Draft',
      date: '12 Jul 2026',
      amount: '₹8,90,000'
    },
    {
      poNo: 'PO-004',
      vendor: 'IT Needs India',
      status: 'Cancelled',
      date: '13 Jul 2026',
      amount: '₹2,15,000'
    }
  ];

  get filteredOrders(): PurchaseOrder[] {
    return this.purchaseOrders.filter(order =>
      (this.selectedStatus === 'All' || order.status === this.selectedStatus) &&
      (this.selectedVendor === 'All' || order.vendor === this.selectedVendor) &&
      (
        this.searchText === '' ||
        order.poNo.toLowerCase().includes(this.searchText.toLowerCase()) ||
        order.vendor.toLowerCase().includes(this.searchText.toLowerCase())
      )
    );
  }

  resetFilters(): void {
    this.searchText = '';
    this.selectedStatus = 'All';
    this.selectedVendor = 'All';
    this.dateRange = '';
  }

  createPurchaseOrder(): void {
    this.router.navigate(['/purchase-orders-creation']);
  }

  viewOrder(order: PurchaseOrder): void {
    alert('Viewing ' + order.poNo);
  }

  editOrder(order: PurchaseOrder): void {
    alert('Editing ' + order.poNo);
  }

  deleteOrder(order: PurchaseOrder): void {
    if (confirm('Delete ' + order.poNo + '?')) {
      this.purchaseOrders = this.purchaseOrders.filter(
        p => p.poNo !== order.poNo
      );
    }
  }

}