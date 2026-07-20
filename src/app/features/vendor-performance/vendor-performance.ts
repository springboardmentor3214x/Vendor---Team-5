import { Component, AfterViewInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink, RouterLinkActive } from '@angular/router';

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
export class VendorPerformanceComponent implements AfterViewInit {

  searchText = '';

  vendors = [
    {
      rank: 1,
      name: 'Vendor A',
      orders: 28,
      delivery: '92%',
      quality: '4.8/5',
      response: '4.1',
      score: '92%',
      status: 'Top Performer'
    },
    {
      rank: 2,
      name: 'Vendor B',
      orders: 24,
      delivery: '90%',
      quality: '4.3/5',
      response: '5.2',
      score: '89%',
      status: 'Top Performer'
    },
    {
      rank: 3,
      name: 'Vendor C',
      orders: 32,
      delivery: '86%',
      quality: '4.2/5',
      response: '6.0',
      score: '86%',
      status: 'Top Performer'
    },
    {
      rank: 4,
      name: 'Vendor D',
      orders: 18,
      delivery: '82%',
      quality: '4.0/5',
      response: '6.8',
      score: '82%',
      status: 'Good'
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
        labels: ['Jan 26', 'Feb 26', 'Mar 26', 'Apr 26', 'May 26', 'Jun 26', 'Jul 26'],
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
        labels: [
          'Vendor A',
          'Vendor B',
          'Vendor C',
          'Vendor D',
          'Vendor E'
        ],
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