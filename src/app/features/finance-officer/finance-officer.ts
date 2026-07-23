import { Component, AfterViewInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { Chart, registerables } from 'chart.js';

Chart.register(...registerables);

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './finance-officer.html',
  styleUrls: ['./finance-officer.css']
})
export class FinanceOfficerComponent implements AfterViewInit {

  financeOpen = true;

  toggleFinance() {
    this.financeOpen = !this.financeOpen;
  }

  cards = [
    {
      title: 'Total Vendors',
      count: 250,
      color: '#5b4cf0',
      icon: '👥'
    },
    {
      title: 'Active Vendors',
      count: 180,
      color: '#34c759',
      icon: '🏠'
    },
    {
      title: 'Pending Procurements',
      count: 42,
      color: '#ff9500',
      icon: '📋'
    }
  ];

  activities = [
    {
      activity: 'New Vendor Added - TechNova Solutions',
      id: 'VEN-2505-001',
      category: 'Vendor',
      user: 'Swathi.C',
      date: '10 July 2026',
      status: 'Completed'
    },
    {
      activity: 'Purchase Request Approved',
      id: 'PR-2505-045',
      category: 'Procurement',
      user: 'Pranjelly',
      date: '10 July 2026',
      status: 'Completed'
    },
    {
      activity: 'Contract Renewed - ABC Supplies',
      id: 'CON-2505-09',
      category: 'Contracts',
      user: 'Bharathi',
      date: '09 July 2026',
      status: 'Completed'
    },
    {
      activity: 'Invoice Pending Approval',
      id: 'INV-2505-110',
      category: 'Finance',
      user: 'Swathi.H',
      date: '09 July 2026',
      status: 'Pending'
    }
  ];

  ngAfterViewInit(): void {
    setTimeout(() => {
      this.loadVendorChart();
      this.loadSpendChart();
    });
  }

  loadVendorChart(): void {

    const canvas = document.getElementById('vendorChart') as HTMLCanvasElement;

    if (!canvas) return;

    new Chart(canvas, {
      type: 'line',
      data: {
        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'],
        datasets: [
          {
            label: 'Vendor Reliability',
            data: [82, 85, 88, 91, 90, 94, 96],
            borderColor: '#4f46e5',
            backgroundColor: 'rgba(79,70,229,0.2)',
            fill: true,
            tension: 0.4
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false
      }
    });

  }

  loadSpendChart(): void {

    const canvas = document.getElementById('spendChart') as HTMLCanvasElement;

    if (!canvas) return;

    new Chart(canvas, {
      type: 'bar',
      data: {
        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        datasets: [
          {
            label: 'Spend Analysis',
            data: [25, 35, 40, 55, 48, 62],
            backgroundColor: [
              '#4f46e5',
              '#22c55e',
              '#f97316',
              '#06b6d4',
              '#eab308',
              '#ef4444'
            ],
            borderRadius: 8
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
            beginAtZero: true
          }
        }
      }
    });

  }
  
}