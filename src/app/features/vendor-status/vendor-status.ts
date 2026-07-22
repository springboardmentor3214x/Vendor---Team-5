import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-vendor-status',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './vendor-status.html',
  styleUrls: ['./vendor-status.css']
})
export class VendorStatusComponent {

  search = '';
  selectedStatus = 'All Status';

  vendors = [
    {
      name: 'Tech Solutions',
      status: 'Active',
      approvalStatus: 'Approved'
    },
    {
      name: 'Build Constructions',
      status: 'Pending',
      approvalStatus: 'Pending'
    },
    {
      name: 'Green Supplies',
      status: 'Inactive',
      approvalStatus: 'Approved'
    },
    {
      name: 'ABC Traders',
      status: 'Suspended',
      approvalStatus: 'Rejected'
    }
  ];

}