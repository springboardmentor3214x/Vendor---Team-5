import { Component, AfterViewInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Chart, registerables } from 'chart.js';
import { RouterLink } from '@angular/router';

Chart.register(...registerables);

@Component({
  selector: 'app-supply-chain-manager',
  standalone: true,
  imports: [CommonModule,RouterLink],
  templateUrl: './supply-chain-manager.html',
  styleUrls: ['./supply-chain-manager.css']
})
export class SupplyChainManagerComponent implements AfterViewInit {

  ngAfterViewInit(): void {
    this.createLineChart();
    this.createBarChart();
  }

  createLineChart(): void {

    const existingChart = Chart.getChart('lineChart');
    if (existingChart) {
      existingChart.destroy();
    }

    new Chart('lineChart', {

      type: 'line',

      data: {
        labels: ['1 May', '3 May', '5 May', '7 May', '9 May', '10 May'],

        datasets: [{
          data: [30, 30, 40, 25, 45, 65],

          borderColor: '#16a34a',

          backgroundColor: '#16a34a',

          borderWidth: 3,

          tension: 0.4,

          fill: false,

          pointRadius: 5,

          pointBackgroundColor: '#16a34a'
        }]
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

            max: 100,

            ticks: {
              stepSize: 25
            }

          }

        }

      }

    });

  }

  createBarChart(): void {

    const existingChart = Chart.getChart('barChart');
    if (existingChart) {
      existingChart.destroy();
    }

    new Chart('barChart', {

      type: 'bar',

      data: {

        labels: [
          'Week 1',
          'Week 2',
          'Week 3',
          'Week 4',
          'Week 5'
        ],

        datasets: [{

          data: [
            90000,
            130000,
            170000,
            185000,
            200000
          ],

          backgroundColor: '#5b4cf5',

          borderRadius: 8,

          barThickness: 30

        }]

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

            max: 200000,

            ticks: {

              callback: function(value) {
                return Number(value) / 1000 + 'K';
              }

            }

          }

        }

      }

    });

  }

}