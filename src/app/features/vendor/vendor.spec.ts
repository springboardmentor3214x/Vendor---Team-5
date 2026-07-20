import { ComponentFixture, TestBed } from '@angular/core/testing';

import { VendorComponent } from './vendor';

describe('Vendor', () => {
  let component: VendorComponent;
  let fixture: ComponentFixture<VendorComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [VendorComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(VendorComponent);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
