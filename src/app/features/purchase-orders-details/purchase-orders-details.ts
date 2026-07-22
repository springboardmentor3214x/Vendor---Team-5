import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-purchase-orders-details',
  standalone: true,
  imports: [
    CommonModule,
    RouterLink
  ],
  templateUrl: './purchase-orders-details.html',
  styleUrls: ['./purchase-orders-details.css']
})
export class PurchaseOrdersDetailsComponent {

  purchaseOrder = {
    poNumber: 'PO-2026-00038',
    poDate: '17 July 2026',
    status: 'Approved',
    approvedBy: 'Priya (Procurement Manager)',
    approvedDate: '17 July 2026'
  };

  vendor = {
    name: 'Tech Solution Ltd.',
    address: '32 Industrial Area, Hyderabad, Telangana - 500032',
    contactPerson: 'Dhanush Sai',
    phone: '+91 9876543210',
    email: 'info@techsolution.com'
  };

  request = {
    requestNumber: 'PR-2026-00127',
    title: 'Laptop Purchase',
    department: 'IT Department',
    requestedBy: 'Dhanush Sai',
    priority: 'High'
  };

  products = [
    {
      id: 1,
      name: 'Dell Latitude 5440 Laptop',
      category: 'Electronics',
      quantity: 10,
      price: 61000,
      total: 610000
    },
    {
      id: 2,
      name: 'Laptop Bag',
      category: 'Accessories',
      quantity: 10,
      price: 1200,
      total: 12000
    },
    {
      id: 3,
      name: 'Wireless Mouse',
      category: 'Accessories',
      quantity: 10,
      price: 850,
      total: 8500
    }
  ];

  delivery = {
    address: 'IT Department, Main Office, Hyderabad',
    date: '17 July 2026',
    payment: '30 Days',
    tax: 'GST 18%',
    amount: '₹6,30,500'
  };

}