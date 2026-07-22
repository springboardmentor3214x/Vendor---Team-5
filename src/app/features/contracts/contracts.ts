import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';

interface Contract {
  id: string;
  name: string;
  status: string;
  startDate: string;
  endDate: string;
  value: string;
}

@Component({
  selector: 'app-contracts',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './contracts.html',
  styleUrls: ['./contracts.css']
})
export class ContractsComponent {

  contracts: Contract[] = [
    {
      id: 'CON-2026-1045',
      name: 'IT Services Agreement',
      status: 'Active',
      startDate: 'Jul 11, 2026',
      endDate: 'Jul 18, 2026',
      value: '4,250'
    },
    {
      id: 'CON-2026-1044',
      name: 'Maintenance Agreement',
      status: 'Active',
      startDate: 'Jul 10, 2026',
      endDate: 'Jul 20, 2026',
      value: '7,800'
    },
    {
      id: 'CON-2026-1043',
      name: 'Supply Contract',
      status: 'Expiring Soon',
      startDate: 'Jul 09, 2026',
      endDate: 'Jul 22, 2026',
      value: '2,150'
    },
    {
      id: 'CON-2026-1042',
      name: 'Security Services',
      status: 'Expired',
      startDate: 'Jun 15, 2026',
      endDate: 'Jul 05, 2026',
      value: '3,950'
    },
    {
      id: 'CON-2026-1041',
      name: 'Office Equipment Lease',
      status: 'Active',
      startDate: 'Jul 01, 2026',
      endDate: 'Dec 31, 2026',
      value: '12,500'
    }
  ];

}