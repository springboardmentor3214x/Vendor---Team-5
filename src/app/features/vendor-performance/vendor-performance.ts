import { Component, AfterViewInit, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink, RouterLinkActive } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environments/environment';

import {
  Chart,
  registerables
} from 'chart.js';

Chart.register(...registerables);

@Component({
  selector: 'app-vendor-performance',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    RouterLink,
    RouterLinkActive
  ],
  templateUrl: './vendor-performance.html',
  styleUrls: ['./vendor-performance.css']
})
export class VendorPerformanceComponent implements OnInit, AfterViewInit {

  searchText = '';

  vendors: any[] = [];

  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    this.loadPerformance();
  }

  ngAfterViewInit(): void {
    this.createLineChart();
    this.createBarChart();
  }

  loadPerformance(): void {

    this.http.get<any>(
      `${environment.apiUrl}/performance/rankings`
    ).subscribe({
      next: (data) => {
        this.vendors = data;
      },
      error: (err) => {
        console.error('Failed to load performance', err);
      }
    });

  }

  createLineChart(): void {

    new Chart('lineChart', {
      type: 'line',
      data: {
        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'],
        datasets: [
          {
            label: 'Overall Score',
            data: [55, 70, 66, 75, 72, 81, 89],
            borderColor: '#5D4EF5',
            backgroundColor: 'rgba(93,78,245,0.15)',
            fill: true,
            tension: 0.4
          }
        ]
      },
      options: {
        responsive: true,
        plugins: {
          legend: {
            display: false
          }
        }
      }
    });

  }

  createBarChart(): void {

    new Chart('barChart', {
      type: 'bar',
      data: {
        labels: ['Vendor A', 'Vendor B', 'Vendor C', 'Vendor D', 'Vendor E'],
        datasets: [
          {
            data: [92, 89, 86, 82, 79],
            backgroundColor: '#5D4EF5'
          }
        ]
      },
      options: {
        responsive: true,
        indexAxis: 'y',
        plugins: {
          legend: {
            display: false
          }
        },
        scales: {
          x: {
            beginAtZero: true,
            max: 100
          }
        }
      }
    });

  }

}