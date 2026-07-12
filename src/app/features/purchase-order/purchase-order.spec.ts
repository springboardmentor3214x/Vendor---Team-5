import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PurchaseOrderComponent } from './purchase-order';

describe('PurchaseOrder', () => {
  let component: PurchaseOrderComponent;
  let fixture: ComponentFixture<PurchaseOrderComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [PurchaseOrderComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(PurchaseOrderComponent);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
