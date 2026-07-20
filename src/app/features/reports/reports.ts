import { Component, AfterViewInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { Chart, registerables } from 'chart.js';

Chart.register(...registerables);

interface VendorReport {
  id: number;
  vendorName: string;
  totalOrders: number;
  totalSpend: string;
  onTimeDelivery: string;
  qualityScore: string;
  reliabilityScore: string;
  status: string;
}

@Component({
  selector: 'app-reports',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './reports.html',
  styleUrl: './reports.css'
})
export class ReportsComponent implements AfterViewInit {

  reports: VendorReport[] = [
    {
      id: 1,
      vendorName: 'Tech Solutions Pvt Ltd',
      totalOrders: 25,
      totalSpend: '₹16,25,000',
      onTimeDelivery: '96%',
      qualityScore: '94%',
      reliabilityScore: '96%',
      status: 'Excellent'
    },
    {
      id: 2,
      vendorName: 'HP Enterprise',
      totalOrders: 10,
      totalSpend: '₹1,80,000',
      onTimeDelivery: '94%',
      qualityScore: '92%',
      reliabilityScore: '94%',
      status: 'Excellent'
    },
    {
      id: 3,
      vendorName: 'Cisco Systems',
      totalOrders: 12,
      totalSpend: '₹3,36,000',
      onTimeDelivery: '97%',
      qualityScore: '93%',
      reliabilityScore: '93%',
      status: 'Excellent'
    },
    {
      id: 4,
      vendorName: 'Lenovo India',
      totalOrders: 15,
      totalSpend: '₹7,80,000',
      onTimeDelivery: '93%',
      qualityScore: '91%',
      reliabilityScore: '91%',
      status: 'Very Good'
    },
    {
      id: 5,
      vendorName: 'Canon Solutions',
      totalOrders: 8,
      totalSpend: '₹1,00,000',
      onTimeDelivery: '89%',
      qualityScore: '88%',
      reliabilityScore: '90%',
      status: 'Very Good'
    }
  ];

  ngAfterViewInit(): void {
    setTimeout(() => {
    this.loadTrendChart();
    this.loadVendorChart();
    });
  }

  loadTrendChart(): void {

    const canvas = document.getElementById('trendChart') as HTMLCanvasElement;

    if (!canvas) return;

    new Chart(canvas, {
      type: 'line',
      data: {
        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'],
        datasets: [
          {
            label: 'Procurement',
            data: [20, 60, 90, 60, 90, 70, 120],
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

  loadVendorChart(): void {

    const canvas = document.getElementById('vendorChart') as HTMLCanvasElement;

    if (!canvas) return;

    new Chart(canvas, {
      type: 'bar',
      data: {
        labels: [
          'Tech',
          'HP',
          'Cisco',
          'Lenovo',
          'Canon'
        ],
        datasets: [
          {
            data: [96, 94, 93, 91, 90],
            backgroundColor: '#4f46e5',
            borderRadius: 6
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
            max: 100,
            beginAtZero: true
          }
        }
      }
    });

  }

}