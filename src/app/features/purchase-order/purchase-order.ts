import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink, Router } from '@angular/router';
import { FormArray, FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';

@Component({
  selector: 'app-purchase-order',
  standalone: true,
  imports: [CommonModule, RouterLink, ReactiveFormsModule],
  templateUrl: './purchase-order.html',
  styleUrl: './purchase-order.css'
})
export class PurchaseOrderComponent {
  poForm: FormGroup;
  isSaving = false;

  constructor(
    private fb: FormBuilder,
    private router: Router
  ) {
    this.poForm = this.fb.group({
      vendorName: ['', Validators.required],
      poDate: [this.today()],
      deliveryDate: [''],
      contactPerson: ['', Validators.required],
      email: ['', [Validators.required, Validators.email]],
      phone: ['', Validators.required],
      items: this.fb.array([this.createItem()])
    });
  }

  private today(): string {
    return new Date().toISOString().substring(0, 10);
  }

  private createItem(): FormGroup {
    return this.fb.group({
      itemName: [''],
      description: [''],
      quality: [''],
      unitPrice: [0],
      total: [0]
    });
  }

  get items(): FormArray {
    return this.poForm.get('items') as FormArray;
  }

  get grandTotal(): number {
    return this.items.controls.reduce((sum, item) => sum + (item.get('total')?.value || 0), 0);
  }

  updateTotal(index: number): void {
    const item = this.items.at(index);
    const unitPrice = Number(item.get('unitPrice')?.value) || 0;
    item.get('total')?.setValue(unitPrice);
  }

  addItem(): void {
    this.items.push(this.createItem());
  }

  removeItem(index: number): void {
    if (this.items.length > 1) {
      this.items.removeAt(index);
    }
  }

  onSave(): void {
    if (this.poForm.invalid) {
      this.poForm.markAllAsTouched();
      return;
    }

    this.isSaving = true;

    // Replace with a real API call, e.g.:
    // this.poService.create(this.poForm.value).subscribe({
    //   next: () => {
    //     this.isSaving = false;
    //     this.router.navigate(['/procurement']);
    //   }
    // });

    setTimeout(() => {
      this.isSaving = false;
      this.router.navigate(['/procurement']);
    }, 800);
  }

  onCancel(): void {
    this.router.navigate(['/procurement']);
  }
}