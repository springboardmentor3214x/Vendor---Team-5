import { Component, AfterViewInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Chart, registerables } from 'chart.js';
import { Router, RouterLink } from '@angular/router';
Chart.register(...registerables);

@Component({
  selector: 'app-procurement-tracking',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './procurement-tracking.html',
  styleUrls: ['./procurement-tracking.css']
})
export class ProcurementTrackingComponent implements AfterViewInit {

  ngAfterViewInit(): void {
    this.createProcurementChart();
  }

  createProcurementChart(): void {

    new Chart('procurementChart', {

      type: 'bar',

      data: {

        labels: [
          'June 6',
          'June 13',
          'June 20',
          'June 27',
          'July 4',
          'July 11'
        ],

        datasets: [
          {

            label: 'Order Value',

            data: [
              620000,
              700000,
              620000,
              630000,
              600000,
              750000
            ],

            backgroundColor: '#C026D3',

            borderRadius: 6,

            barThickness: 30

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

            max: 1000000,

            ticks: {

              callback: function(value) {

                if (Number(value) === 1000000) {
                  return '1M';
                }

                return Number(value) / 1000 + 'K';
              }

            }

          }

        }

      }

    });

  }

}