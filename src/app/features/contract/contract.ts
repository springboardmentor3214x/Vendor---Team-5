import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-contracts',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    RouterModule
  ],
  templateUrl: './contract.html',
  styleUrls: ['./contract.css']
})
export class ContractComponent {

  contracts = [
    {
      id: 'PO-001',
      name: 'Supply Agreement 2026',
      vendor: 'Tech Solutions Pvt Ltd',
      date: '20 Jul 2026',
      amount: '₹5,20,000',
      status: 'Active'
    },
    {
      id: 'PO-002',
      name: 'Raw Material Supply',
      vendor: 'Global Supplies',
      date: '24 Jul 2026',
      amount: '₹3,75,000',
      status: 'Active'
    },
    {
      id: 'PO-003',
      name: 'Equipment Maintenance',
      vendor: 'Industrial Parts Co.',
      date: '20 Jul 2026',
      amount: '₹8,90,000',
      status: 'Active'
    },
    {
      id: 'PO-004',
      name: 'IT Services Agreement',
      vendor: 'IT Needs India',
      date: '20 Jul 2026',
      amount: '₹2,15,000',
      status: 'Expiring Soon'
    },
    {
      id: 'PO-005',
      name: 'Logistics Support',
      vendor: 'Prime Logistics',
      date: '23 Jul 2026',
      amount: '₹6,40,000',
      status: 'Active'
    }
  ];

  resetFilters(): void {
    alert('Filters Reset');
  }

}