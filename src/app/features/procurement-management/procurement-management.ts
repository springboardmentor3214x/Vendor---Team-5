import { Component, AfterViewInit, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink, RouterLinkActive } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { Chart, registerables } from 'chart.js';
import { environment } from '../../../environments/environment';

Chart.register(...registerables);

@Component({
  selector: 'app-procurement-management',
  standalone: true,
  imports: [
    CommonModule,
    RouterLink,
    RouterLinkActive
  ],
  templateUrl: './procurement-management.html',
  styleUrls: ['./procurement-management.css']
})
export class ProcurementManagementComponent implements OnInit, AfterViewInit {

  private apiUrl = `${environment.apiUrl}`;

  purchaseOrders: any[] = [];

  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    this.loadPurchaseOrders();
  }

  ngAfterViewInit(): void {
    this.loadChart();
  }

  loadPurchaseOrders(): void {
    this.http.get<any[]>(`${this.apiUrl}/purchase-orders`).subscribe({
      next: (data) => {
        this.purchaseOrders = data;
      },
      error: () => {
        console.log('Backend not running. Using demo data.');

        this.purchaseOrders = [
          {
            number: 'PO-2026-0001',
            vendor: 'Tech Solutions Pvt Ltd',
            date: '10 Jul 2026',
            amount: '₹5,20,000',
            status: 'Approved'
          },
          {
            number: 'PO-2026-0002',
            vendor: 'Global Supplies',
            date: '10 Jul 2026',
            amount: '₹3,75,000',
            status: 'Pending'
          },
          {
            number: 'PO-2026-0003',
            vendor: 'Industrial Parts Co.',
            date: '10 Jul 2026',
            amount: '₹8,90,000',
            status: 'Approved'
          },
          {
            number: 'PO-2026-0004',
            vendor: 'IT Needs India',
            date: '10 Jul 2026',
            amount: '₹2,15,000',
            status: 'Draft'
          }
        ];
      }
    });
  }

  loadChart(): void {

    const existingChart = Chart.getChart('purchaseChart');

    if (existingChart) {
      existingChart.destroy();
    }

    new Chart('purchaseChart', {
      type: 'line',
      data: {
        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug'],
        datasets: [
          {
            label: 'Purchase Orders',
            data: [25, 40, 38, 75, 60, 55, 78, 65],
            borderColor: '#5b3df5',
            backgroundColor: 'rgba(91,61,245,0.15)',
            fill: true,
            tension: 0.4,
            borderWidth: 3,
            pointRadius: 4,
            pointBackgroundColor: '#5b3df5'
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            grid: {
              color: '#eeeeee'
            }
          },
          x: {
            grid: {
              display: false
            }
          }
        }
      }
    });
  }
}