import { Component, AfterViewInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink, Router } from '@angular/router';
import { Chart, registerables } from 'chart.js';

Chart.register(...registerables);

interface PurchaseOrder {
  poNumber: string;
  vendorName: string;
  date: string;
  amount: string;
  status: 'Approved' | 'Pending' | 'Draft';
}

@Component({
  selector: 'app-procurement',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './procurement.html',
  styleUrl: './procurement.css'
})
export class ProcurementComponent implements AfterViewInit {

  constructor(private router: Router) {}

  recentPOs: PurchaseOrder[] = [
    {
      poNumber: 'PO-2026-0001',
      vendorName: 'Tech Solutions Pvt Ltd',
      date: '10 Jul 2026',
      amount: '5,20,000',
      status: 'Approved'
    },
    {
      poNumber: 'PO-2026-0002',
      vendorName: 'Global Supplies',
      date: '10 Jul 2026',
      amount: '3,75,000',
      status: 'Pending'
    },
    {
      poNumber: 'PO-2026-0003',
      vendorName: 'Industrial Parts Co.',
      date: '10 Jul 2026',
      amount: '8,90,000',
      status: 'Approved'
    },
    {
      poNumber: 'PO-2026-0004',
      vendorName: 'IT Needs India',
      date: '10 Jul 2026',
      amount: '2,15,000',
      status: 'Draft'
    }
  ];

  statusClass(status: string): string {
    if (status === 'Approved') return 'completed';
    if (status === 'Pending') return 'pending';
    if (status === 'Draft') return 'draft';
    return '';
  }

  ngAfterViewInit(): void {
    this.renderChart();
  }

  private renderChart(): void {
    const canvas = document.getElementById('procurementChart') as HTMLCanvasElement;
    if (!canvas) return;

    new Chart(canvas, {
      type: 'line',
      data: {
        labels: ['Jan', 'Feb', 'Mar', 'April', 'May', 'Jun', 'Jul', 'Aug'],
        datasets: [
          {
            label: 'Purchase Orders',
            data: [22, 35, 38, 78, 60, 52, 82, 65],
            borderColor: '#6366f1',
            backgroundColor: 'rgba(99, 102, 241, 0.1)',
            tension: 0.4,
            fill: true,
            pointBackgroundColor: '#6366f1',
            pointRadius: 4
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false }
        },
        scales: {
          y: {
            min: 0,
            max: 100,
            ticks: { stepSize: 20 },
            grid: { color: '#f3f4f6' }
          },
          x: {
            grid: { display: false }
          }
        }
      }
    });
  }

  logout(): void {
    this.router.navigate(['/login']);
  }
}