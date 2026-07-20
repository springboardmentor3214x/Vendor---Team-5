import { AfterViewInit, Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';

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
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './auditor.html',
  styleUrls: ['./auditor.css']
})
export class AuditorComponent implements AfterViewInit {

  totalVendors = 250;
  activeVendors = 180;
  pendingProcurements = 42;

  recentActivities = [
    {
      activity: 'New Vendor Added - TechNova Solutions',
      referenceId: 'VEN-2505-001',
      category: 'Vendor',
      performedBy: 'Swathi C.',
      date: '10 Jul 2026',
      status: 'Completed'
    },
    {
      activity: 'Purchase Request Approved',
      referenceId: 'PR-2505-045',
      category: 'Procurement',
      performedBy: 'Pranjelly',
      date: '10 Jul 2026',
      status: 'Completed'
    },
    {
      activity: 'Contract Renewal - ABC Supplies',
      referenceId: 'CON-2505-009',
      category: 'Contracts',
      performedBy: 'Bharathi',
      date: '09 Jul 2026',
      status: 'Completed'
    },
    {
      activity: 'Invoice Pending Approval',
      referenceId: 'INV-2505-110',
      category: 'Finance',
      performedBy: 'Swathi H.',
      date: '09 Jul 2026',
      status: 'Pending'
    },
    {
      activity: 'Vendor Reliability Score Updated',
      referenceId: 'VEN-2505-002',
      category: 'Vendor',
      performedBy: 'Sonali',
      date: '09 Jul 2026',
      status: 'Completed'
    }
  ];

  ngAfterViewInit(): void {
    this.createLineChart();
    this.createBarChart();
  }

  createLineChart(): void {
    new Chart('lineChart', {
      type: 'line',
      data: {
        labels: ['1 May', '3 May', '5 May', '7 May', '9 May', '10 May'],
        datasets: [
          {
            data: [30, 40, 28, 45, 65, 95],
            borderColor: '#22c55e',
            backgroundColor: 'rgba(34,197,94,0.15)',
            fill: true,
            tension: 0.4,
            pointRadius: 5
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
            data: [85000, 120000, 160000, 180000, 200000],
            backgroundColor: '#5b5df7',
            borderRadius: 8
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