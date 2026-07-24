import { ComponentFixture, TestBed } from '@angular/core/testing';

import { VendorDetailsComponent } from './vendor-details';

describe('VendorDetails', () => {
  let component: VendorDetailsComponent;
  let fixture: ComponentFixture<VendorDetailsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [VendorDetailsComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(VendorDetailsComponent);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
