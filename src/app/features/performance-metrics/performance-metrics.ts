import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink, RouterLinkActive } from '@angular/router';

@Component({
  selector: 'app-performance-metrics',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    RouterLink,
    RouterLinkActive
  ],
  templateUrl: './performance-metrics.html',
  styleUrls: ['./performance-metrics.css']
})
export class PerformanceMetricsComponent {

  searchText: string = '';

  metrics = [
    {
      name: 'On-Time Delivery Rate',
      current: '87%',
      target: '90%',
      status: 'Good'
    },
    {
      name: 'Delayed Delivery Count',
      current: '32',
      target: '< 20',
      status: 'Warning'
    },
    {
      name: 'Average Quality Rating',
      current: '4.2 / 5',
      target: '4.5 / 5',
      status: 'Good'
    },
    {
      name: 'Average Communication Response Time',
      current: '1 hr 35 min',
      target: '2 hrs',
      status: 'Good'
    },
    {
      name: 'Issue Resolution Time',
      current: '1.8 Days',
      target: '2 Days',
      status: 'Good'
    },
    {
      name: 'Order Completion Rate',
      current: '93%',
      target: '95%',
      status: 'Good'
    },
    {
      name: 'Total Completed Orders',
      current: '236',
      target: '250',
      status: 'Good'
    },
    {
      name: 'Overall Performance Score',
      current: '88%',
      target: '90%',
      status: 'Good'
    }
  ];

}