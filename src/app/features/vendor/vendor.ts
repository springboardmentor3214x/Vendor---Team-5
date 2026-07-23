import { AfterViewInit, Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterLink } from '@angular/router';

import {
  Chart,
  LineController,
  LineElement,
  PointElement,
  LinearScale,
  CategoryScale,
  BarController,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';

Chart.register(
  LineController,
  LineElement,
  PointElement,
  LinearScale,
  CategoryScale,
  BarController,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

@Component({
  selector: 'app-vendor',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './vendor.html',
  styleUrls: ['./vendor.css']
})
export class VendorComponent implements AfterViewInit {

  totalVendors = 250;
  activeVendors = 180;
  pendingProcurements = 42;

  recentActivities = [
    {
      activity: 'Vendor Registration',
      referenceId: 'VEN-001',
      category: 'Registration',
      performedBy: 'Admin',
      date: '15 Jul 2026',
      status: 'Completed'
    },
    {
      activity: 'Purchase Order Created',
      referenceId: 'PO-102',
      category: 'Purchase Order',
      performedBy: 'Procurement Manager',
      date: '14 Jul 2026',
      status: 'Pending'
    },
    {
      activity: 'Contract Approved',
      referenceId: 'CON-205',
      category: 'Contract',
      performedBy: 'Finance Officer',
      date: '13 Jul 2026',
      status: 'Completed'
    },
    {
      activity: 'Vendor Profile Updated',
      referenceId: 'VEN-015',
      category: 'Profile',
      performedBy: 'Vendor',
      date: '12 Jul 2026',
      status: 'Completed'
    },
    {
      activity: 'Communication Sent',
      referenceId: 'COM-320',
      category: 'Communication',
      performedBy: 'Admin',
      date: '11 Jul 2026',
      status: 'Pending'
    }
  ];

  constructor(private router: Router) {}

  logout(): void {
    this.router.navigate(['/login']);
  }

  ngAfterViewInit(): void {
    this.createLineChart();
    this.createBarChart();
  }

  createLineChart(): void {
    new Chart('lineChart', {
      type: 'line',
      data: {
        labels: ['1 May', '3 May', '5 May', '7 May', '9 May', '11 May'],
        datasets: [
          {
            label: 'Vendor Reliability',
            data: [45, 60, 55, 75, 70, 92],
            borderColor: '#5B5DF7',
            backgroundColor: 'rgba(91,93,247,0.15)',
            fill: true,
            tension: 0.4,
            pointRadius: 5,
            pointBackgroundColor: '#5B5DF7'
          }
        ]
      },
      options: {
        responsive: true,
        plugins: {
          legend: {
            display: false
          }
        },
        scales: {
          y: {
            beginAtZero: true
          }
        }
      }
    });
  }

  createBarChart(): void {
    new Chart('barChart', {
      type: 'bar',
      data: {
        labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5'],
        datasets: [
          {
            data: [120, 180, 150, 230, 170],
            backgroundColor: [
              '#5B5DF7',
              '#5B5DF7',
              '#5B5DF7',
              '#5B5DF7',
              '#5B5DF7'
            ],
            borderRadius: 10
          }
        ]
      },
      options: {
        responsive: true,
        plugins: {
          legend: {
            display: false
          }
        },
        scales: {
          y: {
            beginAtZero: true
          }
        }
      }
    });
  }
}