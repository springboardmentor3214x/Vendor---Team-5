import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environments/environment';

@Component({
  selector: 'app-purchase-orders-details',
  standalone: true,
  imports: [
    CommonModule,
    RouterLink
  ],
  templateUrl: './purchase-orders-details.html',
  styleUrls: ['./purchase-orders-details.css']
})
export class PurchaseOrdersDetailsComponent implements OnInit {

  constructor(private http: HttpClient) {}

  purchaseOrder: any = {};
  vendor: any = {};
  request: any = {};
  products: any[] = [];
  delivery: any = {};

  ngOnInit(): void {
    this.loadPurchaseOrder();
  }

  loadPurchaseOrder(): void {

    const purchaseOrderId = 1; // Replace during backend integration

    this.http.get<any>(
      `${environment.apiUrl}/purchase-orders/${purchaseOrderId}`
    ).subscribe({
      next: (data) => {
        this.purchaseOrder = data;
      },
      error: (err) => {
        console.error('Failed to load purchase order', err);
      }
    });

  }

}