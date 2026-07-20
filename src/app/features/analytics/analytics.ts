import { AfterViewInit, Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Chart, registerables } from 'chart.js';
import { Router, RouterLink } from '@angular/router';
Chart.register(...registerables);

@Component({
  selector: 'app-analytics',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './analytics.html',
  styleUrls: ['./analytics.css']
})
export class AnalyticsComponent implements AfterViewInit {

  ngAfterViewInit(): void {
    this.loadProcurementChart();
    this.loadVendorChart();
  }

  loadProcurementChart() {

    new Chart('procurementChart', {
      type: 'line',
      data: {
        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        datasets: [{
          label: 'Procurement Value',
          data: [40, 55, 48, 70, 82, 95],
          borderColor: '#4F46E5',
          backgroundColor: 'rgba(79,70,229,0.15)',
          fill: true,
          tension: 0.4
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false
      }
    });

  }

  loadVendorChart() {

    new Chart('vendorChart', {
      type: 'bar',
      data: {
        labels: [
          'Vendor A',
          'Vendor B',
          'Vendor C',
          'Vendor D',
          'Vendor E'
        ],
        datasets: [{
          label: 'Performance',
          data: [92, 85, 95, 88, 91],
          backgroundColor: [
            '#4F46E5',
            '#22C55E',
            '#F97316',
            '#3B82F6',
            '#EC4899'
          ]
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false
      }
    });

  }

}