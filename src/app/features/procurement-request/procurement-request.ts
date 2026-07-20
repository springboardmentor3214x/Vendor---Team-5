import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
@Component({
  selector: 'app-procurement-request',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './procurement-request.html',
  styleUrls: ['./procurement-request.css']
})
export class ProcurementRequestComponent {

  procurement = {
    requestNumber: 'PR-2026-00124',
    requestTitle: '',
    department: '',
    requestedBy: '',
    productName: '',
    category: '',
    quantity: 1,
    unit: '',
    budget: 0,
    deliveryDate: '',
    priority: 'Medium',
    status: 'Pending',
    justification: '',
    remarks: ''
  };

  saveDraft(): void {
    console.log('Draft Saved');
    alert('Draft Saved Successfully');
  }

  submitRequest(): void {
    console.log(this.procurement);
    alert('Procurement Request Submitted Successfully');
  }

  cancel(): void {
    this.procurement = {
      requestNumber: 'PR-2026-00124',
      requestTitle: '',
      department: '',
      requestedBy: '',
      productName: '',
      category: '',
      quantity: 1,
      unit: '',
      budget: 0,
      deliveryDate: '',
      priority: 'Medium',
      status: 'Pending',
      justification: '',
      remarks: ''
    };
  }

  onFileSelected(event: any): void {
    const file = event.target.files[0];
    if (file) {
      console.log('Selected File:', file.name);
    }
  }
}