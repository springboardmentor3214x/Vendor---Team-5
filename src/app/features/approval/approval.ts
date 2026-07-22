import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-approval',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './approval.html',
  styleUrls: ['./approval.css']
})
export class ApprovalComponent {

  request = {
    requestNumber: 'PR-2026-00126',
    department: 'IT Department',
    requestTitle: 'Laptop Purchase for Development Team',
    requestedBy: 'Alex Joseph',
    product: 'Laptop (Dell Latitude 5440)',
    category: 'IT Hardware',
    quantity: 15,
    budget: '₹7,50,000',
    priority: 'High',
    justification: 'Purchase laptops for the development team.',
    status: 'Pending Approval'
  };

  approvalHistory = [
    {
      action: 'Submitted',
      by: 'Alex Joseph',
      role: 'IT Manager',
      date: '19 Jul 2026 11:20 AM',
      remarks: 'Request submitted'
    }
  ];

  approveRequest(): void {
    alert('Request Approved Successfully');
  }

  rejectRequest(): void {
    alert('Request Rejected');
  }

  sendBack(): void {
    alert('Request Sent Back for Modification');
  }

}