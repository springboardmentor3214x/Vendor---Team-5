import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink, RouterLinkActive } from '@angular/router';

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
export class VendorRankingComponent {

  searchText: string = '';

  category: string = 'All Category';

  score: string = 'All Scores';

  vendors = [
    {
      rank: 1,
      name: 'Vendor A Pvt Ltd',
      category: 'Raw Material Supplier',
      score: '92%',
      delivery: '90%',
      quality: '4.5 / 5',
      communication: '88%',
      remarks: '4.6 / 5'
    },
    {
      rank: 2,
      name: 'Vendor B Solutions',
      category: 'Equipment Vendor',
      score: '88%',
      delivery: '87%',
      quality: '4.3 / 5',
      communication: '85%',
      remarks: '4.4 / 5'
    },
    {
      rank: 3,
      name: 'Vendor C Supplies',
      category: 'Raw Material Supplier',
      score: '84%',
      delivery: '82%',
      quality: '4.2 / 5',
      communication: '83%',
      remarks: '4.3 / 5'
    },
    {
      rank: 4,
      name: 'Vendor D Industries',
      category: 'IT Vendor',
      score: '80%',
      delivery: '78%',
      quality: '4.1 / 5',
      communication: '79%',
      remarks: '4.2 / 5'
    },
    {
      rank: 5,
      name: 'Vendor E Enterprises',
      category: 'Service Provider',
      score: '78%',
      delivery: '76%',
      quality: '3.9 / 5',
      communication: '77%',
      remarks: '4.1 / 5'
    },
    {
      rank: 6,
      name: 'Vendor F Solutions',
      category: 'Equipment Vendor',
      score: '75%',
      delivery: '72%',
      quality: '3.8 / 5',
      communication: '76%',
      remarks: '4.0 / 5'
    }
  ];

  get filteredVendors() {
    return this.vendors.filter(v =>
      (this.category === 'All Category' || v.category === this.category) &&
      (this.score === 'All Scores' || parseInt(v.score) >= parseInt(this.score)) &&
      (
        this.searchText === '' ||
        v.name.toLowerCase().includes(this.searchText.toLowerCase())
      )
    );
  }

}