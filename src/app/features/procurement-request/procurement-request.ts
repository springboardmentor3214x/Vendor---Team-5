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

  constructor(private router: Router) {}

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
    console.log('Draft Saved', this.procurement);
    alert('Draft saved successfully.');
  }

  submitRequest(): void {
    console.log('Procurement Request Submitted', this.procurement);

    alert('Procurement Request submitted successfully.');

    this.router.navigate(['/procurement-management']);
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

  onFileSelected(event: Event): void {

    const input = event.target as HTMLInputElement;

    if (input.files && input.files.length > 0) {
      console.log('Selected File:', input.files[0].name);
    }

  }

}