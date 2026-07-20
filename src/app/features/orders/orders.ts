import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';

interface Orders {
  id: string;
  project: string;
  status: string;
  orderDate: string;
  deliveryDate: string;
  amount: string;
}

@Component({
  selector: 'app-orders',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './orders.html',
  styleUrls: ['./orders.css']
})
export class OrdersComponent {

  orders: Orders[] = [
    {
      id: 'PO-2026-1045',
      project: 'Office Supplies',
      status: 'In Progress',
      orderDate: 'Jul 11, 2026',
      deliveryDate: 'Jul 18, 2026',
      amount: '4,250'
    },
    {
      id: 'PO-2026-1044',
      project: 'IT Equipment',
      status: 'Pending',
      orderDate: 'Jul 10, 2026',
      deliveryDate: 'Jul 20, 2026',
      amount: '7,800'
    },
    {
      id: 'PO-2026-1043',
      project: 'Maintenance Service',
      status: 'Completed',
      orderDate: 'Jul 09, 2026',
      deliveryDate: 'Jul 22, 2026',
      amount: '2,150'
    },
    {
      id: 'PO-2026-1042',
      project: 'Networking Devices',
      status: 'Cancelled',
      orderDate: 'Jul 08, 2026',
      deliveryDate: 'Jul 19, 2026',
      amount: '5,900'
    },
    {
      id: 'PO-2026-1041',
      project: 'Furniture',
      status: 'Completed',
      orderDate: 'Jul 07, 2026',
      deliveryDate: 'Jul 16, 2026',
      amount: '8,400'
    }
  ];

}