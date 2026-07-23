import { Component, AfterViewInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink, Router } from '@angular/router';
import { Chart, registerables } from 'chart.js';

Chart.register(...registerables);

interface Activity {
  activity: string;
  referenceId: string;
  category: string;
  performedBy: string;
  date: string;
  status: 'Completed' | 'Pending';
}

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.css'
})
export class DashboardComponent implements AfterViewInit {

  constructor(private router: Router) {}

  recentActivities: Activity[] = [
    {
      activity: 'New Vendor added - TechNova Solutions',
      referenceId: 'VEN-2505-001',
      category: 'Vendor',
      performedBy: 'Swathi.C',
      date: '10 July 2026',
      status: 'Completed'
    },
    {
      activity: 'Purchase request approved',
      referenceId: 'PR-2505-045',
      category: 'Procurement',
      performedBy: 'Pranjaly',
      date: '10 July 2026',
      status: 'Completed'
    },
    {
      activity: 'Contract renewed - ABC Supplies',
      referenceId: 'CON-2505-09',
      category: 'Contracts',
      performedBy: 'Bharathi',
      date: '09 July 2026',
      status: 'Completed'
    },
    {
      activity: 'Invoice pending approval',
      referenceId: 'INV-2505-110',
      category: 'Finance',
      performedBy: 'Swathi.H',
      date: '09 July 2026',
      status: 'Pending'
    },
    {
      activity: 'Vendor reliability score updated',
      referenceId: 'VEN-2505-002',
      category: 'Vendor',
      performedBy: 'Sonali',
      date: '09 July 2026',
      status: 'Completed'
    }
  ];

  ngAfterViewInit(): void {
    this.renderLineChart();
    this.renderBarChart();
  }

  private renderLineChart(): void {
    const canvas = document.getElementById('lineChart') as HTMLCanvasElement;
    if (!canvas) return;

    new Chart(canvas, {
      type: 'line',
      data: {
        labels: ['1 May', '3 May', '6 May', '7 May', '9 May', '10 May'],
        datasets: [
          {
            label: 'Reliability Score',
            data: [55, 45, 40, 65, 70, 85],
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
            ticks: { stepSize: 25 },
            grid: { color: '#f3f4f6' }
          },
          x: {
            grid: { display: false }
          }
        }
      }
    });
  }

  private renderBarChart(): void {
    const canvas = document.getElementById('barChart') as HTMLCanvasElement;
    if (!canvas) return;

    new Chart(canvas, {
      type: 'bar',
      data: {
        labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5'],
        datasets: [
          {
            label: 'Spend',
            data: [140000, 175000, 160000, 200000, 150000],
            backgroundColor: '#6366f1',
            borderRadius: 6,
            barThickness: 32
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
            ticks: {
              callback: (value) => `${Number(value) / 1000}K`
            },
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
    // Clear any stored auth tokens/session data here, e.g.:
    // localStorage.removeItem('authToken');
    this.router.navigate(['/login']);
  }
}