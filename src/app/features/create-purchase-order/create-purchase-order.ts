import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-create-purchase-order',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './create-purchase-order.html',
  styleUrls: ['./create-purchase-order.css']
})
export class CreatePurchaseOrderComponent {

  vendorName = '';
  poDate = '';
  deliveryDate = '';
  contactPerson = '';
  email = '';
  phone = '';

  items = [
    {
      itemName: '',
      description: '',
      quantity: 1,
      unitPrice: 0,
      total: 0
    }
  ];

  calculateTotal(index: number) {
    this.items[index].total =
      this.items[index].quantity *
      this.items[index].unitPrice;
  }

  addItem() {
    this.items.push({
      itemName: '',
      description: '',
      quantity: 1,
      unitPrice: 0,
      total: 0
    });
  }

  savePO() {
    alert('Purchase Order Created Successfully');
  }

  cancel() {
    history.back();
  }
}