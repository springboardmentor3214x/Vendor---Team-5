import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';

@Component({
  selector: 'app-purchase-orders-creation',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    RouterLink
  ],
  templateUrl: './purchase-orders-creation.html',
  styleUrls: ['./purchase-orders-creation.css']
})
export class PurchaseOrdersCreationComponent {

  constructor(private router: Router) {}

  purchaseOrder = {
    purchaseOrderNumber: 'PO-2026-00056',
    purchaseRequestNumber: 'PR-2026-00124',
    purchaseOrderDate: '',
    approvedBy: 'Priya Menon',
    status: 'Draft',
    paymentTerms: 'Net 30 Days',
    expectedDelivery: '',

    vendorName: 'ABC Enterprises',
    contactPerson: 'Ramesh Kumar',
    email: 'rameshkumar@gmail.com',
    contactNumber: '9987674532',
    vendorAddress: '',

    shippingAddress: '',
    state: '',
    city: '',

    taxDetails: 'GST @18%',
    additionalCharges: 0,
    remarks: ''
  };

  products = [
    {
      id: 1,
      itemName: 'Laptop',
      description: 'Dell Latitude',
      quantity: 15,
      unit: 'Nos',
      unitPrice: 75000,
      tax: 18,
      total: 1327500
    },
    {
      id: 2,
      itemName: 'Laptop Bag',
      description: '15 Inch',
      quantity: 15,
      unit: 'Nos',
      unitPrice: 1500,
      tax: 18,
      total: 26550
    }
  ];

  saveDraft(): void {
    console.log('Draft Saved', this.purchaseOrder);
    alert('Purchase Order saved as Draft.');
  }

  generatePurchaseOrder(): void {
    console.log('Purchase Order Generated', this.purchaseOrder);
    console.log(this.products);

    alert('Purchase Order generated successfully.');

    this.router.navigate(['/purchase-orders']);
  }

  cancel(): void {
    if (confirm('Are you sure you want to cancel?')) {
      this.router.navigate(['/purchase-orders']);
    }
  }

}