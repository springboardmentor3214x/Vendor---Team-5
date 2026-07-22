import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PurchaseOrdersCreationComponent } from './purchase-orders-creation';

describe('PurchaseOrdersCreation', () => {
  let component: PurchaseOrdersCreationComponent;
  let fixture: ComponentFixture<PurchaseOrdersCreationComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [PurchaseOrdersCreationComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(PurchaseOrdersCreationComponent);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
