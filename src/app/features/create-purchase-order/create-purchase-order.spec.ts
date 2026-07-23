import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CreatePurchaseOrder } from './create-purchase-order';

describe('CreatePurchaseOrder', () => {
  let component: CreatePurchaseOrder;
  let fixture: ComponentFixture<CreatePurchaseOrder>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CreatePurchaseOrder],
    }).compileComponents();

    fixture = TestBed.createComponent(CreatePurchaseOrder);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
