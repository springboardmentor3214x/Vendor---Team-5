import { ComponentFixture, TestBed } from '@angular/core/testing';

import { VendorManagementsComponent } from './vendor-managements';

describe('VendorManagements', () => {
  let component: VendorManagementsComponent;
  let fixture: ComponentFixture<VendorManagementsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [VendorManagementsComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(VendorManagementsComponent);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBe(true);
  });
});
