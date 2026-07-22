import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink, RouterLinkActive } from '@angular/router';

@Component({
  selector: 'app-product-quality-evaluation',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    RouterLink,
    RouterLinkActive
  ],
  templateUrl: './product-quality-evaluation.html',
  styleUrls: ['./product-quality-evaluation.css']
})
export class ProductQualityEvaluationComponent {

  searchText: string = '';

  purchaseOrder: string = 'PO-2026-0123';
  vendorName: string = 'Vendor A Pvt Ltd';
  inspectionDate: string = '';

  materialQuality: string = '4 - Good';
  packagingQuality: string = '4 - Good';
  quantityAccuracy: string = '5 - Excellent';
  specificationCompliance: string = '4 - Good';

  productDefects: string = 'Minor Defects';
  overallRating: string = '4 - Good';

  remarks: string =
    'Material quality is good and packaging is satisfactory. Minor defects were identified in a few items.';

  purchaseOrders = [
    'PO-2026-0123',
    'PO-2026-0124',
    'PO-2026-0125'
  ];

  vendors = [
    'Vendor A Pvt Ltd',
    'Vendor B Solutions',
    'Vendor C Supplies'
  ];

  ratings = [
    '5 - Excellent',
    '4 - Good',
    '3 - Average',
    '2 - Poor',
    '1 - Very Poor'
  ];

  defects = [
    'No Defects',
    'Minor Defects',
    'Major Defects'
  ];

  resetForm(): void {

    this.purchaseOrder = '';
    this.vendorName = '';
    this.inspectionDate = '';

    this.materialQuality = '';
    this.packagingQuality = '';
    this.quantityAccuracy = '';
    this.specificationCompliance = '';

    this.productDefects = '';
    this.overallRating = '';

    this.remarks = '';

  }

  saveEvaluation(): void {

    alert('Product Quality Evaluation Saved Successfully!');

    console.log({
      purchaseOrder: this.purchaseOrder,
      vendor: this.vendorName,
      inspectionDate: this.inspectionDate,
      materialQuality: this.materialQuality,
      packagingQuality: this.packagingQuality,
      quantityAccuracy: this.quantityAccuracy,
      specificationCompliance: this.specificationCompliance,
      productDefects: this.productDefects,
      overallRating: this.overallRating,
      remarks: this.remarks
    });

  }

}