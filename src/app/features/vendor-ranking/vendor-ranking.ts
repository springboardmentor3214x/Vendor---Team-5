import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink, RouterLinkActive } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environments/environment';

@Component({
  selector: 'app-vendor-ranking',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    RouterLink,
    RouterLinkActive
  ],
  templateUrl: './vendor-ranking.html',
  styleUrls: ['./vendor-ranking.css']
})
export class VendorRankingComponent implements OnInit {

  searchText = '';
  category = 'All Category';
  score = 'All Scores';

  vendors: any[] = [];

  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    this.loadRankings();
  }

  loadRankings(): void {

    this.http.get<any[]>(
      `${environment.apiUrl}/performance/rankings`
    ).subscribe({

      next: (data) => {
        this.vendors = data;
      },

      error: (err) => {
        console.error('Failed to load vendor rankings', err);
      }

    });

  }

  get filteredVendors() {

    return this.vendors.filter(v =>
      (this.category === 'All Category' || v.category === this.category) &&
      (
        this.score === 'All Scores' ||
        parseInt(v.score) >= parseInt(this.score)
      ) &&
      (
        this.searchText === '' ||
        (v.name || '')
          .toLowerCase()
          .includes(this.searchText.toLowerCase())
      )
    );

  }

}